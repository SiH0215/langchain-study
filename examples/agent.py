"""A bounded agent with a deterministic tool and in-process memory."""

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from examples.common import get_model


@tool
def multiply(a: int, b: int) -> int:
    """두 정수를 곱한다. 정확한 곱셈 결과가 필요할 때 사용한다."""
    return a * b


def make_agent(model):
    return create_agent(
        model=model,
        tools=[multiply],
        system_prompt="한국어 학습 도우미다. 곱셈은 반드시 multiply 도구로 계산하라.",
        checkpointer=InMemorySaver(),
    )


def main():
    agent = make_agent(get_model())
    config = {"configurable": {"thread_id": "study-demo"}, "recursion_limit": 10}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "나는 민수야. 17 곱하기 23은 얼마야?"}]},
        config=config,
    )
    for message in result["messages"]:
        print(message.type, message.content)
        if getattr(message, "tool_calls", None):
            print("도구 요청:", message.tool_calls)
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "내 이름이 뭐라고 했지?"}]},
        config=config,
    )
    print("후속 응답:", result["messages"][-1].content)


if __name__ == "__main__":
    main()
