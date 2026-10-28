# 검증 기록

## 환경

- 날짜: 2026-10-27
- OS: Windows
- Python: 3.12.14
- langchain: 1.4.7
- langchain-core: 1.7.0
- langchain-google-genai: 4.4.2
- langchain-text-splitters: 1.1.3
- langgraph: 1.2.18
- 전체 버전: [requirements-lock.txt](../requirements-lock.txt)

추가 예제의 안내 환경은 Python 3.12 이상. 검증 버전의 NumPy가 3.12 이상 요구.
원본 실습 기록의 Python 3.10.11 환경을 이번 검증 환경으로 표시하지 않음.

## 확인한 것

`python -m unittest discover -s tests -v`: **8개 통과**.

| 테스트 | 확인한 동작 |
| --- | --- |
| 프롬프트 | 필수 변수 누락 감지, 메시지 역할·질문 전달 |
| JSON history | 한글 저장·읽기, 잘못된 기록을 덮어쓰지 않고 오류 |
| 청크 | 길이 범위, source·시작 위치와 실제 원문 일치 |
| 검색 흐름 | 통제된 임베딩으로 검색·Retriever 반환 확인 |
| 질문 재작성 | history와 후속 질문의 입력 순서, 가짜 모델 출력 전달 |
| 구조 스키마 | 허용되지 않은 level 값 거부 |
| Tool | 17 × 23 = 391, 잘못된 인자 검증 |
| Agent | 미리 정한 도구 요청 실행, ToolMessage 연결, 같은 thread 상태 유지와 다른 thread 분리 |

`python -m examples.basics --mode offline`: 프롬프트 메시지와 병렬 계산 결과 확인.
Python 문법, 문서의 상대 링크, Git 공백 검사도 확인.
실제 키 대신 임시 문자열로 모델·임베딩 객체와 구조화 출력 설정을 생성해 API 호환성 확인. 이 과정에서 생성·임베딩 요청을 보내지 않았음.

## 확인하지 않은 것

- 실제 Gemini 생성·임베딩 API 호출, 계정별 모델 지원·쿼터·요금
- 실제 임베딩의 의미 검색 품질과 후속 질문 재작성 정확도
- 실제 모델의 JSON 응답·도구 선택·문서 밖 답변 거부·인용 정확도
- PDF, 영속 DB, Agentic RAG, 웹 배포, 다중 사용자 동시 실행

가짜 모델과 통제된 벡터 테스트는 프로그램의 데이터 전달 검증. 실제 모델의 추론·도구 선택 능력이나 검색 품질을 검증한 것은 아님.
실모델 실험은 [체크리스트](checklist.md)의 빈 기록 표에 별도로 기록.
원본 문서의 테스트 결과는 이전 실습 당시의 기록이며 이번 자동 검증과 구분.
