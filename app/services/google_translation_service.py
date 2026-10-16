
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import translate_v3
from google.oauth2 import service_account

load_dotenv()


class GoogleTranslationService:

    def __init__(self):
        credentials_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS", ""
        )
        project_id = os.getenv(
            "GOOGLE_TRANSLATION_PROJECT_ID", ""
        )
        location = os.getenv(
            "GOOGLE_TRANSLATION_LOCATION", "global"
        )

        if not project_id:
            raise ValueError(
                "GOOGLE_TRANSLATION_PROJECT_ID is missing"
            )

        if not Path(credentials_path).is_file():
            raise ValueError(
                "Google credentials file not found"
            )

        credentials = (
            service_account.Credentials
            .from_service_account_file(credentials_path)
        )

        self.client = translate_v3.TranslationServiceClient(
            credentials=credentials
        )

        self.parent = (
            f"projects/{project_id}/locations/{location}"
        )

    async def translate(
        self,
        message: str,
        target_language: str,
        source_language: str = "en",
    ) -> str:

        if not message.strip():
            raise ValueError("Message cannot be empty")

        if target_language not in ("te", "hi", "en"):
            raise ValueError("Unsupported language")

        if target_language == source_language:
            return message.strip()

        request = {
            "parent": self.parent,
            "contents": [message.strip()],
            "mime_type": "text/plain",
            "source_language_code": source_language,
            "target_language_code": target_language,
        }

        response = await asyncio.to_thread(
            self.client.translate_text,
            request=request,
        )

        if not response.translations:
            raise RuntimeError(
                "Google Translation returned no results"
            )

        return response.translations[0].translated_text.strip()
