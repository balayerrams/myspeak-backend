
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.services.google_translation_service import (
    GoogleTranslationService,
)

app = FastAPI(
    title="MySpeak API",
    description="Backend services for MySpeak multilingual voice reminders",
    version="1.0.0",
)


class ReminderTranslationRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    source_language: str = "en"
    target_language: str


class ReminderTranslationResponse(BaseModel):
    original_message: str
    translated_message: str
    target_language: str
    provider: str
    requires_review: bool


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "MySpeak",
        "service": "backend",
        "version": "1.0.0",
    }


@app.post(
    "/api/v1/translate/reminder",
    response_model=ReminderTranslationResponse,
)
async def translate_reminder(
    request: ReminderTranslationRequest,
):
    if request.source_language != "en":
        raise HTTPException(
            status_code=400,
            detail="Currently only English source is supported",
        )

    if request.target_language not in ("en", "te", "hi"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported target language",
        )

    try:
        service = GoogleTranslationService()

        translated = await service.translate(
            message=request.message,
            source_language=request.source_language,
            target_language=request.target_language,
        )

        return ReminderTranslationResponse(
            original_message=request.message,
            translated_message=translated,
            target_language=request.target_language,
            provider="google_cloud_translation_v3",
            requires_review=True,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Translation service unavailable",
        )
