# LangChain 기초 실습 노트

Gemini를 LangChain에 연결하고, 프롬프트와 체인 → 대화 기록 → 문서 검색과 RAG → 도구를 쓰는 작은 에이전트까지 익히는 Python 학습 저장소다.
입력·출력·검색 근거를 직접 확인하는 것을 목표로 한다.

## 학습 기록과 추가 자료

- **기존 실습**: 모델 호출, Prompt/Chain, JSON 대화 저장, 청크·임베딩·InMemoryVectorStore, 멀티턴 RAG를 진행했다. [당시 원본 기록](docs/original-study.md)을 보존했다. 원본의 테스트 결과는 당시 기록이다.
- **추가 학습 자료**: 구조화 출력, 호출 방식 비교, History-aware RAG, Tool/Agent 등을 예제와 함께 구성했다. 자료가 있다는 것과 학습자가 실습을 완료했다는 것은 구분한다.
- **이번 검증**: [검증 기록](docs/verification.md) 참고. 실모델 응답 품질은 API 실행 후 별도로 확인한다.

## 여기까지 하면 기초를 써봤다고 할 수 있다

공식 자격 기준이 아니라 이 저장소의 학습 목표다.

| 단계 | 직접 설명하고 실행할 내용 | 자료 / 코드 |
| --- | --- | --- |
| 1 | 모델 API와 LangChain 역할, 환경변수, 메시지 역할 | [기본 개념](docs/foundations.md) |
| 2 | 템플릿 변수, `prompt \| model \| parser`, Runnable 입출력 | [basics.py](examples/basics.py) |
| 3 | invoke, stream, batch, ainvoke 비교 | [호출 실습](examples/basics.py) |
| 4 | 자연어 대신 스키마에 맞춘 필드 추출 | [structured.py](examples/structured.py) |
| 5 | 대화 기록 전달·저장·초기화와 문맥 제한 | [chat.py](examples/chat.py) |
| 6 | Document, 청크, 임베딩, 검색, 메타데이터 | [RAG 설명](docs/rag.md) |
| 7 | 기본 RAG와 질문 재작성 RAG 비교, 출처 확인 | [rag.py](examples/rag.py) |
| 8 | 도구 정의, 모델의 도구 요청과 실제 실행 구분 | [agent.py](examples/agent.py) |
| 9 | 오류·지연·토큰·검색 품질을 나눠 점검 | [운영 기초](docs/practice.md) |

읽은 뒤 [완료 체크리스트와 비교 실험](docs/checklist.md)에 실제 결과를 기록한다.

## 빠른 시작

추가 예제는 **Python 3.12 이상**, LangChain 1.x 계열을 기준으로 한다. 기존 기록의 Python 3.10 환경과 구분한다.
PowerShell에서 저장소 루트를 기준으로 실행한다.

```powershell
git clone https://github.com/SiH0215/langchain-study.git
cd langchain-study
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

활성화가 막히면 정책을 바꾸지 않고 `.\venv\Scripts\python.exe -m examples.basics --mode offline`처럼 직접 실행한다.
`.env`에 본인의 `GOOGLE_API_KEY`를 넣고, 채팅·임베딩 모델 ID는 자신의 계정에서 사용 가능한 값으로 바꾼다.
샘플 ID는 공식 문서의 예시이며 계정별 제공 여부나 앞으로의 지원을 보장하지 않는다.
모델 제공사를 바꾸면 연동 클래스·패키지·키도 확인한다.

### 1. API 없이 흐름 확인

```powershell
python -m examples.basics --mode offline
python -m unittest discover -s tests -v
```

템플릿 메시지, Runnable의 병렬 출력, 로컬 검증 결과를 확인한다. 두 명령은 API 키가 필요 없다.

### 2. 모델 호출과 출력 형식

```powershell
python -m examples.basics
python -m examples.basics --mode stream
python -m examples.basics --mode batch
python -m examples.basics --mode async
python -m examples.structured
python -m examples.chat
```

`batch` 예제는 모델 요청 두 개를 보낸다. 스트리밍은 답변 조각을 먼저 보여주는 방식이며 비용을 없애는 기능은 아니다.

### 3. 검색 → RAG → 대화 맥락을 반영한 RAG

```powershell
python -m examples.rag --search-only --k 2
python -m examples.rag --k 2
python -m examples.rag --history-aware --k 2
```

같은 질문을 순서대로 입력해 비교한다.

```text
예정 시트에서 직접 수정해도 돼?
그럼 어디서 수정해야 해?
스터디 참가비는 얼마야?
종료
```

검색 질문·원문·메타데이터를 확인한다. 마지막 질문의 정답은 문서에 없다.
`--search-only`도 문서와 질문을 임베딩하므로 API를 사용한다. 이 모드에서는 답변 생성과 질문 재작성을 하지 않는다.
채팅과 RAG는 `초기화`, `종료` 명령을 지원한다. 일반 채팅은 `chat_history.json`에 저장하고, RAG 대화는 메모리에만 둔다.

### 4. Tool / Agent

```powershell
python -m examples.agent
```

17 × 23을 도구로 계산하는 과정과 같은 `thread_id`의 후속 대화를 확인한다.
실제 도구 호출 여부는 `tool_calls`와 `tool` 메시지로 확인한다. 모델의 선택은 실행할 때 관찰해야 한다.

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

- 개인용 CLI 예제다. 인증, 다중 사용자, 동시 파일 쓰기, 웹 배포는 포함하지 않는다.
- 벡터 저장소와 `InMemorySaver`는 프로세스 종료 시 사라진다. RAG 재실행 시 문서를 다시 임베딩한다.
- 예제 문서는 새로 만든 가상 데이터다. 원본 실습에 쓰던 업무 문서는 포함하지 않는다.
- RAG의 출처 번호는 인용 형식을 유도한다. 실제로 올바른 근거인지 원문과 비교해야 한다.
- 실제 API 호출에는 본인의 키가 필요하며 비용·쿼터·모델 지원 여부는 공급자와 계정에 따라 다르다.
- 기본 설치는 `requirements.txt`, 검증과 같은 버전은 `python -m pip install -r requirements-lock.txt`를 사용한다.

## 공식 문서

2026-10-27에 확인했다. 공식 API를 참고해 저장소에 맞는 한국어 학습 예제를 작성했다.

- [개요](https://docs.langchain.com/oss/python/langchain/overview), [모델](https://docs.langchain.com/oss/python/langchain/models), [메시지](https://docs.langchain.com/oss/python/langchain/messages)
- [Gemini 연동](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai), [임베딩](https://docs.langchain.com/oss/python/integrations/embeddings/google_generative_ai)
- [텍스트 분할](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter), [도구](https://docs.langchain.com/oss/python/langchain/tools)
- [구조화 출력](https://docs.langchain.com/oss/python/langchain/structured-output), [에이전트 시작](https://docs.langchain.com/oss/python/langchain/quickstart)
- [단기 기억](https://docs.langchain.com/oss/python/langchain/short-term-memory), [LangSmith 추적](https://docs.langchain.com/langsmith/observability-quickstart)
