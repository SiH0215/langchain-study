"""Prompts, messages, LCEL and invoke/stream/batch/ainvoke."""

import argparse
import asyncio

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

from examples.common import get_model


def make_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "너는 파이썬 강사다. 한국어로 두 문장 이내로 설명한다."),
        ("human", "{question}"),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["invoke", "stream", "batch", "async", "offline"], default="invoke")
    args = parser.parse_args()
    prompt = make_prompt()
    if args.mode == "offline":
        # Runnable composition can be learned without a model or API key.
        flow = RunnableParallel(
            original=RunnableLambda(lambda value: value["question"]),
            length=RunnableLambda(lambda value: len(value["question"])),
        )
        print(prompt.invoke({"question": "리스트가 뭐야?"}).to_messages())
        print(flow.invoke({"question": "리스트가 뭐야?"}))
        return

    chain = prompt | get_model() | StrOutputParser()
    inputs = {"question": "파이썬 리스트와 튜플은 어떻게 달라?"}
    if args.mode == "stream":
        for token in chain.stream(inputs):
            print(token, end="", flush=True)
        print()
    elif args.mode == "batch":
        # Two requests; batching does not mean a single billed model call.
        print(chain.batch([inputs, {"question": "딕셔너리는 언제 써?"}], config={"max_concurrency": 2}))
    elif args.mode == "async":
        print(asyncio.run(chain.ainvoke(inputs)))
    else:
        print(chain.invoke(inputs))


if __name__ == "__main__":
    main()
