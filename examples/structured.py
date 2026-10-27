"""Extract validated fields instead of parsing free-form prose."""

from typing import Literal

from pydantic import BaseModel, Field

from examples.common import get_model


class StudyNote(BaseModel):
    topic: str = Field(description="학습 주제")
    level: Literal["beginner", "intermediate", "advanced"]
    keywords: list[str] = Field(description="핵심 키워드")


def main():
    model = get_model().with_structured_output(StudyNote, method="json_schema")
    result = model.invoke("초보자를 위한 RAG 학습 메모: 문서 분할, 임베딩, 검색을 연습했다.")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
