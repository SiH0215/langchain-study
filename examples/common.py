"""Shared configuration; importing this module does not call an external API."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

ROOT = Path(__file__).resolve().parents[1]


def configure():
    load_dotenv(ROOT / ".env")
    if not os.getenv("GOOGLE_API_KEY", "").strip():
        raise ValueError(".env에 GOOGLE_API_KEY를 입력하세요. .env.example을 참고하세요.")


def get_model():
    configure()
    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_CHAT_MODEL", "gemini-2.5-flash-lite"),
        vertexai=False,
        timeout=60,
        max_retries=2,
    )
