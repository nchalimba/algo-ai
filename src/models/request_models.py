from pydantic import BaseModel, HttpUrl, field_validator
from fastapi import UploadFile

from typing import List


class QuestionRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        if not value.strip():
            raise ValueError("Question cannot be empty or whitespace.")
        return value


class TextRequest(BaseModel):
    text: str
    title: str

    @field_validator("text", "title")
    @classmethod
    def validate_text(cls, value):
        if not value.strip():
            raise ValueError("Text cannot be empty or whitespace.")
        return value


class URLRequest(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def validate_url(cls, value):
        if not value.startswith(("http://", "https://")):
            raise ValueError("URL must start with 'http://' or 'https://'.")
        return value

class URLsRequest(BaseModel):
    urls: List[str]

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, values):
        for url in values:
            if not url.startswith(("http://", "https://")):
                raise ValueError("URL must start with 'http://' or 'https://'.")
        return values
