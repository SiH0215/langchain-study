# LangChain 실습 정리

## 1. 실습 환경

- OS: Windows
- IDE: VS Code
- Python: 3.10.11
- 작업 폴더: `E:\SiH\Langchain`
- 가상환경: `venv`
- LLM: Google Gemini
- LangChain 기반 독립 실습 프로젝트

---

## 2. 가상환경 생성

작업 폴더로 이동한다.

```powershell
cd E:\SiH\Langchain
```

가상환경 생성:

```powershell
python -m venv venv
```

PowerShell에서 가상환경 활성화:

```powershell
.\venv\Scripts\Activate.ps1
```

현재 Python이 가상환경을 사용하는지 확인:

```powershell
python -c "import sys; print(sys.executable)"
```

정상이라면 다음과 비슷한 경로가 출력된다.

```text
E:\SiH\Langchain\venv\Scripts\python.exe
```

---

## 3. 패키지 설치

기본 LangChain + Gemini 연동:

```powershell
python -m pip install langchain langchain-google-genai python-dotenv
```

RAG 실습용:

```powershell
python -m pip install langchain-text-splitters numpy
```

현재 실습에서 사용하는 주요 패키지는 다음과 같다.

```text
langchain
langchain-google-genai
langchain-text-splitters
python-dotenv
numpy
```

---

## 4. LangChain이란?

LangChain은 GPT, Gemini, Claude 같은 LLM을 이용한 애플리케이션을 만들기 쉽게 해주는 프레임워크다.

LangChain 자체가 AI 모델은 아니다.

```text
내 프로그램
    ↓
LangChain
    ↓
LLM 연동 패키지
    ↓
Gemini / GPT / Claude / Local LLM
```

현재 실습에서는 Gemini를 사용하므로 다음 패키지를 사용한다.

```text
langchain-google-genai
```

Python에서는 다음과 같이 import한다.

```python
from langchain_google_genai import ChatGoogleGenerativeAI
```

LangChain은 모델 제공사별 연동 패키지를 별도로 제공한다.

```text
Google Gemini   → langchain-google-genai
OpenAI          → langchain-openai
Anthropic       → langchain-anthropic
```

---

# 5. 가장 기본적인 LLM 호출

`.env` 파일:

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

기본 호출:

```python
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

response = model.invoke(
    "LangChain이 무엇인지 한 문장으로 설명해줘."
)

print(response.content)
```

LangChain에서 가장 기본적인 흐름은 다음과 같다.

```text
질문
 ↓
Model
 ↓
응답
```

---

# 6. PromptTemplate과 Chain

LangChain에서는 프롬프트, 모델, 출력 파서를 하나의 체인으로 연결할 수 있다.

```python
chain = prompt | model | parser
```

흐름:

```text
사용자 입력
    ↓
Prompt
    ↓
LLM
    ↓
Output Parser
    ↓
결과
```

예시:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "너는 파이썬 강사야. 초보자에게 쉬운 말로 간략하게 설명해줘."
    ),
    (
        "human",
        "{question}"
    )
])

chain = prompt | model | StrOutputParser()

answer = chain.invoke({
    "question": "파이썬 리스트가 뭐야?"
})

print(answer)
```

`StrOutputParser()`를 사용하면 LLM 응답을 문자열 형태로 편하게 받을 수 있다.

---

# 7. 멀티턴 대화

멀티턴 대화에서는 이전 대화를 `history`에 저장하고 다음 질문에 함께 전달한다.

핵심 구성:

```python
MessagesPlaceholder("history")
```

프롬프트:

```python
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "너는 파이썬 강사야. 초보자에게 쉬운 말로 간략하게 설명해줘."
    ),
    MessagesPlaceholder("history"),
    (
        "human",
        "{question}"
    )
])
```

현재 실습에서는 대화 기록을 `chat_history.json` 파일에 저장하도록 구현했다.

예시 코드:

```python
import json
from pathlib import Path

history_file = Path(__file__).parent / "chat_history.json"

if history_file.exists():
    with history_file.open("r", encoding="utf-8") as file:
        history = json.load(file)
else:
    history = []


def save_history():
    with history_file.open("w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=2
        )
```

대화가 끝날 때마다:

```python
history.append({
    "role": "human",
    "content": question
})

history.append({
    "role": "ai",
    "content": answer
})

save_history()
```

---

# 8. RAG란?

RAG는 **Retrieval-Augmented Generation**의 약자다.

LLM에게 문서 전체를 매번 전달하는 대신, 질문과 관련된 문서 일부를 먼저 검색한 뒤 그 부분만 LLM에게 전달하는 방식이다.

기본 구조:

```text
문서
 ↓
Chunk 분할
 ↓
Embedding
 ↓
Vector Store
 ↓

사용자 질문
 ↓
질문 Embedding
 ↓
유사한 Chunk 검색
 ↓
관련 문서 + 질문
 ↓
LLM
 ↓
답변
```

핵심 역할은 다음과 같다.

```text
Embedding
→ 텍스트를 의미 기반 벡터로 변환

Vector Store
→ 벡터를 저장하고 유사한 벡터를 검색

Retriever / similarity_search
→ 질문과 관련된 문서 Chunk를 찾음

LLM
→ 검색된 문서를 참고해서 자연어 답변 생성
```

---

# 9. Embedding이란?

Embedding은 텍스트를 의미를 표현하는 숫자 벡터로 변환하는 과정이다.

개념적으로:

```text
"파이썬은 데이터 분석에 사용된다."
            ↓
[0.12, -0.44, 0.87, ...]
```

비슷한 의미의 문장은 벡터 공간에서도 가깝게 위치하도록 만들어진다.

예:

```text
"차량의 엔진이 고장났다."
"자동차 엔진에 문제가 생겼다."
```

두 문장은 표현은 다르지만 의미가 비슷하므로 유사한 벡터가 만들어진다.

반대로 같은 단어가 들어가더라도 문맥이 다르면 다른 방향의 벡터가 만들어질 수 있다.

문서와 질문은 반드시 같은 임베딩 모델로 벡터화해야 한다.

---

# 10. Vector DB / Vector Store

Vector Store는 임베딩된 벡터와 원문, 메타데이터 등을 저장하고 유사도 검색을 수행한다.

예:

```text
vector:
[0.12, -0.44, 0.87, ...]

text:
"파이썬은 데이터 분석에 사용된다."

metadata:
source = "rag.txt"
```

질문 역시 벡터로 변환되고 저장된 문서 벡터와 비교된다.

```text
질문
 ↓
Embedding
 ↓
질문 Vector
 ↓
Vector Store
 ↓
가까운 문서 Vector 검색
 ↓
관련 Chunk 반환
```

현재 실습에서는 별도의 DB 서버 없이 LangChain의 메모리 기반 Vector Store를 사용했다.

```python
from langchain_core.vectorstores import InMemoryVectorStore
```

---

# 11. Chunk 분할

긴 문서를 그대로 Embedding하지 않고 적당한 크기의 작은 단위로 나눈다.

현재 설정:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
```

## chunk_size

하나의 Chunk가 가질 최대 크기.

```text
전체 문서
 ↓
Chunk 1
Chunk 2
Chunk 3
...
```

`chunk_size=500`이면 약 500자 정도의 크기로 나눈다.

## chunk_overlap

인접한 Chunk 사이에 일부 내용을 중복해서 포함한다.

```text
Chunk 1:
AAAAAAAAAAAAAAAA

Chunk 2:
          AAAABBBBBBBBBBBB
          ↑
        overlap
```

문장이나 문맥이 Chunk 경계에서 끊기는 것을 방지하기 위해 사용한다.

현재 설정은:

```text
chunk_size = 500
chunk_overlap = 100
```

이므로 약 20% 정도가 겹치는 구조다.

---

# 12. Chunk 분할 코드

```python
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

file_path = Path(__file__).parent / "rag.txt"

with file_path.open("r", encoding="utf-8") as file:
    text = file.read()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = text_splitter.create_documents([text])

for i, chunk in enumerate(chunks):
    print(f"\n===== Chunk {i + 1} =====")
    print(chunk.page_content)
```

현재 실습 문서에서는 7개의 Chunk가 생성되었다.

---

# 13. Embedding + Vector Store

Google Gemini Embedding 모델을 사용한다.

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)

vector_store = InMemoryVectorStore(
    embeddings
)

vector_store.add_documents(chunks)
```

흐름:

```text
chunks
 ↓
GoogleGenerativeAIEmbeddings
 ↓
Vector 생성
 ↓
InMemoryVectorStore
```

---

# 14. 유사 문서 검색

질문:

```python
query = "예정 시트에서 직접 수정해도 돼?"
```

검색:

```python
results = vector_store.similarity_search(
    query,
    k=2
)
```

`k=2`는 질문과 가장 관련성이 높은 Chunk 2개를 가져온다는 의미다.

예:

```python
for i, doc in enumerate(results):
    print(f"\n===== 검색 결과 {i + 1} =====")
    print(doc.page_content)
```

RAG에서는 문서 전체를 LLM이 읽는 것이 아니다.

```text
Vector Store
→ 관련 부분 검색

LLM
→ 검색된 부분만 읽고 답변
```

---

# 15. 기본 멀티턴 RAG

현재까지 만든 구조:

```text
rag.txt
 ↓
Chunk 분할
 ↓
Embedding
 ↓
Vector Store

사용자 질문
 ↓
similarity_search()
 ↓
관련 Chunk
 ↓
context
 ↓
history + context + question
 ↓
Gemini
 ↓
답변
```

전체 코드:

```python
import os
import json
import warnings
import logging
from pathlib import Path

from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =======================================
# 경고 제거

warnings.filterwarnings(
    "ignore",
    message="Direct use of automatic function calling.*"
)

logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)


# =======================================
# 환경변수

load_dotenv()


# =======================================
# 파일 경로

base_path = Path(__file__).parent

history_file = base_path / "chat_history.json"
rag_file = base_path / "rag.txt"


# =======================================
# RAG 문서 읽기

with rag_file.open("r", encoding="utf-8") as file:
    text = file.read()


# =======================================
# Chunk 분할

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = text_splitter.create_documents([text])


# =======================================
# Embedding

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)


# =======================================
# Vector Store

vector_store = InMemoryVectorStore(
    embeddings
)

vector_store.add_documents(chunks)


# =======================================
# LLM

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# =======================================
# Prompt

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''
너는 제공된 문서를 기반으로 사용자의 질문에 답변하는 AI야.

아래 참고 문서를 우선하여 답변해.
문서에서 확인할 수 없는 내용은 추측하지 말고
"문서에서 확인할 수 없습니다."라고 답변해.

답변은 초보자도 이해하기 쉽게 간략하게 작성해.

[참고 문서]
{context}
'''
    ),

    MessagesPlaceholder("history"),

    (
        "human",
        "{question}"
    )
])


# =======================================
# Chain

chain = prompt | model | StrOutputParser()


# =======================================
# 기존 대화 기록

if history_file.exists():
    with history_file.open("r", encoding="utf-8") as file:
        history = json.load(file)
else:
    history = []


# =======================================
# 대화 기록 저장

def save_history():
    with history_file.open("w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=2
        )


# =======================================
# 멀티턴 대화

while True:

    question = input("\n나: ").strip()

    if question == "종료":
        print("대화를 종료합니다.")
        break

    if question == "초기화":

        history.clear()
        save_history()

        print("대화 기록을 초기화했습니다.")

        continue

    if not question:
        continue


    # ===================================
    # 관련 Chunk 검색

    results = vector_store.similarity_search(
        question,
        k=2
    )


    # ===================================
    # Context 생성

    context = "\n\n".join(
        doc.page_content
        for doc in results
    )


    # ===================================
    # 답변 생성

    print("AI: ", end="", flush=True)

    answer = ""

    for chunk in chain.stream({
        "history": history,
        "context": context,
        "question": question
    }):

        print(chunk, end="", flush=True)
        answer += chunk

    print()


    # ===================================
    # 대화 기록 저장

    history.append({
        "role": "human",
        "content": question
    })

    history.append({
        "role": "ai",
        "content": answer
    })

    save_history()
```

---

# 16. 현재 RAG 테스트 결과

문서에 존재하는 내용:

```text
사용자:
셀 삽입은 어떻게 해야해?

AI:
메인 편성표에서 셀을 삽입하는 방법을 문서 기준으로 설명
```

문서에 없는 내용:

```text
사용자:
휴가원은 어떻게 작성해야해?

AI:
문서에서 확인할 수 없습니다.
```

즉 현재 RAG는 검색된 문서 내용을 근거로 답변하고, 문서에 없는 정보는 추측하지 않도록 동작한다.

---

# 17. 현재 구조의 한계

현재 답변 생성 단계에서는 `history`를 전달한다.

```python
chain.stream({
    "history": history,
    "context": context,
    "question": question
})
```

따라서 LLM은 이전 대화를 참고할 수 있다.

하지만 Vector Store 검색은 현재 질문만 사용한다.

```python
results = vector_store.similarity_search(
    question,
    k=2
)
```

예:

```text
1턴:
예정 시트에서 직접 수정해도 돼?

2턴:
그럼 어디서 수정해야 해?
```

LLM은 `history`를 통해 `그럼`의 의미를 파악할 수 있다.

하지만 Retriever는:

```text
"그럼 어디서 수정해야 해?"
```

만 검색한다.

따라서 문맥 의존적인 후속 질문에서는 검색 정확도가 떨어질 수 있다.

---

# 18. History-aware RAG

History-aware RAG는 이전 대화를 참고하여 현재 질문을 검색하기 좋은 독립적인 질문으로 다시 작성한다.

예:

```text
이전 대화:
예정 시트에서 직접 수정해도 돼?

현재 질문:
그럼 어디서 수정해야 해?
```

질문 재작성:

```text
예정 시트의 내용은 어디에서 수정해야 하는가?
```

그 후 이 질문으로 Vector Store를 검색한다.

전체 구조:

```text
history
+
현재 질문
 ↓
LLM
 ↓
검색용 질문 재작성
 ↓
Vector Store
 ↓
관련 Chunk
 ↓
최종 LLM
 ↓
답변
```

즉 역할을 구분하면:

```text
LLM 1
→ 이전 대화를 보고 검색 질문을 재작성

Vector Store
→ 관련 문서 검색

LLM 2
→ 검색된 문서를 이용해 최종 답변 생성
```

같은 Gemini 모델을 두 역할에 모두 사용할 수도 있다.

---

# 19. History-aware RAG와 Agentic RAG 차이

## History-aware RAG

검색 흐름이 개발자가 정한 순서대로 진행된다.

```text
대화 기록
 ↓
질문 재작성
 ↓
문서 검색
 ↓
답변
```

주요 특징:

- 이전 대화 고려
- 검색용 질문 재작성
- 검색 횟수와 절차가 대부분 고정
- 구조가 비교적 단순

## Agentic RAG

Agent가 상황을 보고 다음 행동을 판단한다.

```text
사용자 질문
 ↓
Agent 판단
 ├─ 문서를 검색할까?
 ├─ 다시 검색할까?
 ├─ 검색어를 바꿀까?
 ├─ 다른 DB를 볼까?
 ├─ 웹 검색을 할까?
 └─ 이제 답변할까?
```

즉 가장 큰 차이는 다음과 같다.

```text
History-aware RAG
→ 정해진 RAG 절차를 대화 맥락에 맞게 개선

Agentic RAG
→ 검색과 도구 사용 과정 자체를 LLM이 판단
```

학습 순서는 다음과 같이 잡을 수 있다.

```text
기본 LLM 호출
 ↓
Prompt / Chain / OutputParser
 ↓
멀티턴 대화
 ↓
기본 RAG
 ↓
멀티턴 RAG
 ↓
History-aware RAG
 ↓
Agentic RAG
```

---

# 20. 현재까지 학습한 핵심

### LangChain

LLM을 이용한 애플리케이션의 여러 단계를 연결하고 관리하는 프레임워크.

### Chain

```python
prompt | model | parser
```

형태로 처리 흐름을 연결한다.

### Multi-turn

이전 대화를 `history`에 포함하여 문맥을 유지한다.

### Chunk

긴 문서를 검색하기 좋은 크기로 나눈 단위.

### Embedding

텍스트의 의미를 숫자 벡터로 표현한다.

### Vector Store

Embedding된 문서를 저장하고 유사도를 기반으로 검색한다.

### RAG

질문과 관련된 문서를 먼저 검색하고 그 문서를 LLM에게 전달하여 답변하게 한다.

### History-aware RAG

이전 대화까지 고려해서 검색용 질문을 재작성한 뒤 문서를 검색한다.

### Agentic RAG

LLM이 어떤 검색이나 Tool을 사용할지 스스로 판단하며 RAG 과정을 수행한다.

---

# 21. 다음 실습 예정

다음 순서로 진행할 예정.

1. History-aware RAG 구현
2. `similarity_search_with_score()`로 검색 점수 확인
3. `k=2`, `k=3`, `k=5` 검색 결과 비교
4. InMemoryVectorStore 대신 실제 Vector DB 사용
5. 여러 문서 RAG
6. PDF 문서 RAG
7. Metadata 기반 검색
8. Agent / Tool
9. Agentic RAG

---

# 22. Git에 올릴 때 주의할 파일

API Key가 포함된 `.env` 파일과 가상환경은 Git에 올리지 않는다.

`.gitignore` 예시:

```gitignore
# Python virtual environment
venv/

# Environment variables
.env

# Python cache
__pycache__/
*.pyc

# Local chat history
chat_history.json
```

프로젝트 구조 예시:

```text
Langchain/
│
├─ main.py
├─ rag.py
├─ rag.txt
├─ README.md
├─ .gitignore
├─ .env
├─ chat_history.json
└─ venv/
```

Git에는 일반적으로 다음만 포함한다.

```text
main.py
rag.py
rag.txt
README.md
.gitignore
```
