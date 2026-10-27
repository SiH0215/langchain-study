"""Deterministic checks for data flow; no provider calls or API keys."""

import tempfile
import unittest
from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.fake_chat_models import FakeListChatModel, FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.vectorstores import InMemoryVectorStore
from pydantic import ValidationError

from examples.agent import make_agent, multiply
from examples.basics import make_prompt
from examples.chat import load_history, save_history
from examples.common import ROOT
from examples.rag import format_context, load_chunks, make_rewriter
from examples.structured import StudyNote


class KeywordEmbeddings(Embeddings):
    """A controlled vector space to check plumbing, not real semantic quality."""

    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        return [float("일정표" in text), float("발표자" in text), 0.01]


class ScriptedToolModel(FakeMessagesListChatModel):
    """Predefined replies to test execution, not the model's tool selection."""

    def bind_tools(self, tools, **kwargs):
        return self


class OfflineTests(unittest.TestCase):
    def test_prompt_requires_question_and_keeps_roles(self):
        prompt = make_prompt()
        with self.assertRaises(KeyError):
            prompt.invoke({"query": "wrong key"})
        messages = prompt.invoke({"question": "리스트란?"}).to_messages()
        self.assertEqual([m.type for m in messages], ["system", "human"])
        self.assertEqual(messages[-1].content, "리스트란?")

    def test_history_roundtrip_and_invalid_file_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            self.assertEqual(load_history(path), [])
            history = [{"role": "human", "content": "안녕"}, {"role": "ai", "content": "반가워"}]
            save_history(history, path)
            self.assertEqual(load_history(path), history)
            path.write_text('{"wrong": true}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_history(path)
            self.assertEqual(path.read_text(encoding="utf-8"), '{"wrong": true}')

    def test_split_preserves_source_offsets_and_text(self):
        path = ROOT / "data" / "study_guide.txt"
        original = path.read_text(encoding="utf-8")
        chunks = load_chunks(path)
        self.assertGreater(len(chunks), 1)
        for doc in chunks:
            self.assertLessEqual(len(doc.page_content), 300)
            self.assertEqual(doc.metadata["source"], path.name)
            start = doc.metadata["start_index"]
            self.assertEqual(original[start:start + len(doc.page_content)], doc.page_content)
        context = format_context(chunks[:2])
        self.assertIn("[1] study_guide.txt", context)
        self.assertIn("[2] study_guide.txt", context)

    def test_retriever_returns_matching_source_with_controlled_vectors(self):
        from langchain_core.documents import Document

        store = InMemoryVectorStore(KeywordEmbeddings())
        store.add_documents([
            Document(page_content="原本 일정표를 수정한다", metadata={"source": "schedule"}),
            Document(page_content="발표자를 배정한다", metadata={"source": "speaker"}),
        ])
        result = store.as_retriever(search_kwargs={"k": 1}).invoke("일정표")
        self.assertEqual(result[0].metadata["source"], "schedule")

    def test_rewriter_passes_history_before_followup(self):
        model = FakeListChatModel(responses=["예정 시트의 내용은 어디서 수정하나?"])
        history = [HumanMessage(content="예정 시트 수정 가능해?"), AIMessage(content="원본을 수정하세요.")]
        chain = make_rewriter(model)
        rendered = chain.first.invoke({"history": history, "question": "그럼 어디서?"}).to_messages()
        self.assertEqual(rendered[1:3], history)
        self.assertEqual(rendered[-1].content, "그럼 어디서?")
        self.assertEqual(chain.invoke({"history": history, "question": "그럼 어디서?"}), "예정 시트의 내용은 어디서 수정하나?")

    def test_structured_schema_rejects_invalid_level(self):
        valid = StudyNote(topic="RAG", level="beginner", keywords=["검색"])
        self.assertEqual(valid.topic, "RAG")
        with self.assertRaises(ValidationError):
            StudyNote(topic="RAG", level="unknown", keywords=[])

    def test_tool_calculation_and_input_validation(self):
        self.assertEqual(multiply.invoke({"a": 17, "b": 23}), 391)
        with self.assertRaises(ValidationError):
            multiply.invoke({"a": "invalid", "b": 23})

    def test_agent_executes_tool_and_isolates_threads(self):
        model = ScriptedToolModel(responses=[
            AIMessage(content="", tool_calls=[{"name": "multiply", "args": {"a": 17, "b": 23}, "id": "call1", "type": "tool_call"}]),
            AIMessage(content="391"),
            AIMessage(content="민수"),
            AIMessage(content="새 대화"),
        ])
        agent = make_agent(model)
        config = {"configurable": {"thread_id": "one"}, "recursion_limit": 10}
        result = agent.invoke({"messages": [HumanMessage(content="나는 민수야. 17 곱하기 23?")]}, config=config)
        tool_messages = [message for message in result["messages"] if message.type == "tool"]
        self.assertEqual(tool_messages[0].content, "391")
        self.assertEqual(tool_messages[0].tool_call_id, "call1")
        second = agent.invoke({"messages": [HumanMessage(content="내 이름은?")]}, config=config)
        self.assertEqual(second["messages"][0].content, "나는 민수야. 17 곱하기 23?")
        separate = agent.invoke({"messages": [HumanMessage(content="새 대화 시작")]}, config={"configurable": {"thread_id": "two"}})
        self.assertEqual(len(separate["messages"]), 2)
        self.assertEqual(separate["messages"][0].content, "새 대화 시작")


if __name__ == "__main__":
    unittest.main()
