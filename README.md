# LangChain 기초 실습 노트

Gemini를 LangChain에 연결하고, 프롬프트와 체인 → 대화 기록 → 문서 검색과 RAG 까지 익히는 Python 학습 저장소.
학습 목표: 입력·출력·검색 근거의 직접 확인.


## 환경

 **Python 3.12 이상**, LangChain 1.x 계열 기준.


### 1. API 없이 흐름 확인

```powershell
python -m examples.basics --mode offline
python -m unittest discover -s tests -v
```

템플릿 메시지, Runnable의 병렬 출력, 로컬 검증 결과 확인. 두 명령 모두 API 키 불필요.

### 2. 모델 호출과 출력 형식

```powershell
python -m examples.basics
python -m examples.basics --mode stream
python -m examples.basics --mode batch
python -m examples.basics --mode async
python -m examples.structured
python -m examples.chat
```

`batch` 예제는 모델 요청 두 개 전송. 스트리밍은 답변 조각을 먼저 보여주는 방식이며 비용을 없애는 기능은 아님.

### 3. 검색 → RAG → 대화 맥락을 반영한 RAG

```powershell
python -m examples.rag --search-only --k 2
python -m examples.rag --k 2
python -m examples.rag --history-aware --k 2
```

같은 질문을 순서대로 입력해 비교.

```text
예정 시트에서 직접 수정해도 돼?
그럼 어디서 수정해야 해?
스터디 참가비는 얼마야?
종료
```

검색 질문·원문·메타데이터 확인. 마지막 질문의 정답은 문서에 없음.
`--search-only`도 문서와 질문을 임베딩하므로 API 사용. 이 모드에서는 답변 생성과 질문 재작성 미수행.
채팅과 RAG는 `초기화`, `종료` 명령 지원. 일반 채팅은 `chat_history.json`에 저장하고, RAG 대화는 메모리에만 보관.

### 4. Tool / Agent

```powershell
python -m examples.agent
```

17 × 23을 도구로 계산하는 과정과 같은 `thread_id`의 후속 대화 확인.
실제 도구 호출 여부는 `tool_calls`와 `tool` 메시지로 확인. 모델의 선택은 실행할 때 관찰 필요.

## 저장소 구조

```text
README.md                  학습 순서와 실행 안내
.env.example               키가 없는 설정 예시
.gitignore                 가상환경·키·로컬 기록 제외
requirements.txt           직접 사용하는 패키지의 허용 범위
requirements-lock.txt      검증 시점의 전체 패키지 버전
examples/
  common.py                설정과 모델 생성
  basics.py                Prompt, Runnable, 호출 방식
  structured.py            Pydantic 구조화 출력
  chat.py                  파일 기반 멀티턴 대화
  rag.py                   검색·기본 RAG·질문 재작성 RAG
  agent.py                 Tool과 Agent, thread별 메모리
data/study_guide.txt        공개용 가상 문서
docs/
  foundations.md           모델·메시지·체인·출력·기억
  rag.md                   문서 검색부터 History-aware RAG까지
  practice.md              오류·평가·비용·추적·다음 단계
  checklist.md             완료 조건과 결과 기록 양식
  original-study.md        처음 실습한 README 원본
  verification.md          검증 범위와 한계
tests/test_offline.py       외부 API 없는 핵심 동작 검증
```

## 실행 범위와 한계

- 개인용 CLI 예제. 인증, 다중 사용자, 동시 파일 쓰기, 웹 배포는 포함하지 않음.
- 벡터 저장소와 `InMemorySaver`는 프로세스 종료 시 소멸. RAG 재실행 시 문서 재임베딩.
- 예제 문서는 새로 만든 가상 데이터. 원본 실습에 쓰던 업무 문서는 포함하지 않음.
- RAG의 출처 번호는 인용 형식 유도. 실제로 올바른 근거인지 원문과 비교 필요.
- 실제 API 호출에는 본인의 키가 필요하며 비용·쿼터·모델 지원 여부는 공급자와 계정에 따라 다름.
- 기본 설치는 `requirements.txt`, 검증과 같은 버전은 `python -m pip install -r requirements-lock.txt` 사용.

## 공식 문서

2026-10-27에 확인. 공식 API를 참고하여 한국어 학습 예제 작성.

- [개요](https://docs.langchain.com/oss/python/langchain/overview), [모델](https://docs.langchain.com/oss/python/langchain/models), [메시지](https://docs.langchain.com/oss/python/langchain/messages)
- [Gemini 연동](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai), [임베딩](https://docs.langchain.com/oss/python/integrations/embeddings/google_generative_ai)
- [텍스트 분할](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter), [도구](https://docs.langchain.com/oss/python/langchain/tools)
- [구조화 출력](https://docs.langchain.com/oss/python/langchain/structured-output), [에이전트 시작](https://docs.langchain.com/oss/python/langchain/quickstart)
- [단기 기억](https://docs.langchain.com/oss/python/langchain/short-term-memory), [LangSmith 추적](https://docs.langchain.com/langsmith/observability-quickstart)
