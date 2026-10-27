"""A single-user CLI chat with JSON persistence and a bounded history."""

import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from examples.common import ROOT, get_model

HISTORY_FILE = ROOT / "chat_history.json"


def load_history(path=HISTORY_FILE):
    if not path.exists():
        return []
    # Fail visibly for corrupt data; do not silently overwrite the original file.
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or any(
        not isinstance(item, dict)
        or item.get("role") not in {"human", "ai"}
        or not isinstance(item.get("content"), str)
        for item in data
    ):
        raise ValueError("대화 기록 형식이 다릅니다. chat_history.json을 확인하세요.")
    return data


def save_history(history, path=HISTORY_FILE):
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 학습 도우미다. 한국어로 간단하게 답하라."),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ])
    chain = prompt | get_model() | StrOutputParser()
    history = load_history()
    print("종료: 대화 끝내기 / 초기화: 저장된 대화 지우기")
    while True:
        question = input("나: ").strip()
        if question == "종료":
            break
        if question == "초기화":
            history = []
            save_history(history)
            print("기록을 초기화했습니다.")
            continue
        if not question:
            continue
        # Keep ten complete exchanges in the prompt. This is not token budgeting.
        answer = chain.invoke({"history": history[-20:], "question": question})
        print("AI:", answer)
        history.extend([{"role": "human", "content": question}, {"role": "ai", "content": answer}])
        save_history(history)


if __name__ == "__main__":
    main()
