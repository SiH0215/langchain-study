# LangChain 기초: 모델에서 대화까지

## 1. 역할과 패키지

Gemini 같은 모델은 입력을 받아 응답을 만든다. LangChain은 모델·프롬프트·검색·도구를 Python 코드에서 연결하도록 돕는다.
직접 SDK로 호출할 수도 있다. 여러 처리 단계를 공통 인터페이스로 다루면 중간 결과를 관찰하고 구성 요소를 교체하기 편하다.

| 구성 | 역할 | 예 |
| --- | --- | --- |
| 모델 제공자 | 모델 실행 API | Google Gemini |
| 연동 패키지 | 제공자 API 연결 | langchain-google-genai |
| langchain-core | 메시지·프롬프트·Runnable 등 공통 구성 | ChatPromptTemplate |
| langchain | 에이전트 등 상위 구성 | create_agent |
| langgraph | 상태를 가진 실행 흐름 | 체크포인터 |
| LangSmith | 실행 관찰·평가 서비스 | 추가 학습 단계 |

LangChain을 사용한다고 응답이 항상 정확해지거나 모델이 새 지식을 학습하는 것은 아니다.

## 2. 메시지와 응답 객체

```python
from langchain_core.messages import SystemMessage, HumanMessage
from examples.common import get_model

response = get_model().invoke([
    SystemMessage(content="한국어로 짧게 설명하라."),
    HumanMessage(content="RAG란 무엇인가?"),
])
print(type(response))
print(response.content)
print(response.usage_metadata)
```

`SystemMessage`는 동작 지침, `HumanMessage`는 사용자 입력, `AIMessage`는 모델 응답이다.
`ToolMessage`는 도구 실행 결과를 담는다. 도구 결과를 사용자 발언으로 바꾸면 역할 정보가 사라진다.
응답은 내용과 메타데이터를 가진 객체다. 기능·제공자에 따라 `content`가 블록 목록일 수 있다.
문자열 체인에서는 `StrOutputParser`를 사용한다. 도구 요청을 분석할 때는 응답 객체를 유지한다.
한 번의 호출은 이전 호출을 자동으로 기억하지 않는다.

## 3. 프롬프트 템플릿

`ChatPromptTemplate`은 메시지 역할과 변수 자리를 정한다. `{question}`에 실행 시 값을 전달한다.
입력 키가 `question`인데 `query`를 넘기면 프롬프트를 만들지 못한다.
템플릿에 JSON 중괄호 자체를 넣을 때는 `{{`, `}}`로 이스케이프한다.

```python
from examples.basics import make_prompt

prompt = make_prompt()
print(prompt.invoke({"question": "리스트란?"}).to_messages())
```

이 단계는 API를 호출하지 않는다. 최종 프롬프트를 눈으로 확인하면 입력 오류를 줄일 수 있다.
Few-shot은 원하는 입력·출력 사례를 프롬프트에 넣어 작업을 보여주는 방식이다. 모델 파라미터를 업데이트하는 파인튜닝과 다르다.
예시가 많을수록 입력 토큰도 늘어나므로 필요한 사례부터 넣는다.

## 4. LCEL과 Runnable

```text
dict → ChatPromptTemplate → 모델 → StrOutputParser → str
```

`prompt | model | parser`의 `|`는 앞 단계 출력을 다음 입력으로 연결한다. 이 표현 방식을 LCEL이라고 한다.
Runnable은 `invoke` 등 공통 실행 인터페이스를 제공하는 구성이다. 프롬프트·모델·체인을 비슷한 방식으로 실행할 수 있다.
`RunnableLambda`는 일반 함수를 흐름에 넣고, `RunnableParallel`은 같은 입력으로 여러 계산을 수행해 사전으로 모은다.
`RunnablePassthrough`는 입력을 유지할 때 쓴다. 모든 단계가 LLM 호출일 필요는 없다.
`offline` 예제로 입력의 키와 각 단계 출력 타입을 먼저 확인한다.

## 5. 호출 방식

| 메서드 | 결과 | 용도 / 주의점 |
| --- | --- | --- |
| invoke | 최종 출력 | 기본 호출, 완료까지 대기 |
| stream | 출력 조각 | 응답을 점진적으로 표시, 중간 오류 처리 필요 |
| batch | 출력 목록 | 독립 요청 여러 개, 동시 실행과 쿼터 제한 |
| ainvoke | await할 작업 | 다른 비동기 작업과 결합 |

비동기는 요청 하나의 추론을 자동으로 빠르게 만드는 기능이 아니다. 기다리는 동안 다른 작업을 진행하는 방식이다.
스트림 조각은 문장·단어 경계와 일치하지 않을 수 있다. 이어 붙여 최종 응답을 만든다.
일반 문자열 체인과 에이전트 상태 업데이트 스트림의 반환 형태는 다르다.

## 6. 출력 파서와 구조화 출력

`StrOutputParser`는 텍스트를 받는 데 쓴다. JSON 문자열을 직접 파싱하면 코드 펜스나 형식 오류를 처리해야 한다.
`with_structured_output(StudyNote, method="json_schema")`는 스키마를 기준으로 필드를 받는다.
`examples.structured`는 Pydantic의 필수 필드·목록·Literal 값을 사용한다.

예상 형태의 예시이며 실제 실행 결과를 기록한 것은 아니다.

```json
{"topic": "RAG", "level": "beginner", "keywords": ["문서 분할", "검색"]}
```

형식 검증은 사실 검증과 다르다. topic이 문자열이어도 내용이 틀릴 수 있다.
네이티브 JSON 스키마 지원 여부는 모델·제공자에 따라 확인한다.
에이전트의 `response_format`으로 만든 결과는 `structured_response`에서 받으며 직접 모델에 쓰는 메서드와 구분한다.

## 7. 멀티턴 대화와 저장

```text
history 읽기 → history + 현재 질문 → 응답 → 질문·응답 추가 → 저장
```

`MessagesPlaceholder("history")`는 여러 메시지가 들어갈 자리다. `{history}`라는 문자열 변수와 다르다.
파일에 저장만 하고 모델 입력에 넘기지 않으면 이전 맥락은 전달되지 않는다.
예제는 최근 10개 문답만 입력에 쓰고 전체 기록은 로컬 JSON에 저장한다.
문답 수 제한은 토큰 제한이 아니다. 문답 하나가 길면 여전히 문맥 한도를 넘을 수 있다.
잘린 오래된 대화를 모델은 알 수 없다. 요약·토큰 기준 자르기는 다음 개선 단계다.

| 저장 방식 | 프로세스 재시작 후 유지 | 학습 포인트 |
| --- | --- | --- |
| Python 리스트 | 아니오 | 직접 메시지 전달 |
| JSON 파일 | 예 | 저장과 입력 문맥은 별개 |
| InMemorySaver | 아니오 | 실행 중 thread_id별 에이전트 상태 |
| DB 체크포인터 | 저장 방식에 따름 | 프로세스 밖 상태 유지, 별도 구현 |

JSON 예제는 한 사용자·한 프로세스용이다. 서비스에서는 사용자별 접근 제어와 동시 쓰기 처리가 필요하다.

## 공식 참고

- [모델](https://docs.langchain.com/oss/python/langchain/models), [메시지](https://docs.langchain.com/oss/python/langchain/messages)
- [Gemini 구조화 출력](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#structured-output)
- [에이전트 구조화 출력](https://docs.langchain.com/oss/python/langchain/structured-output), [단기 기억](https://docs.langchain.com/oss/python/langchain/short-term-memory)
