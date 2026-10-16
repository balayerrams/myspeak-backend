
import asyncio
import base64
import binascii
import os
from pathlib import Path
import json
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

        credentials_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64", "").strip()
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip()

        if credentials_base64:
            # DigitalOcean: decode an encrypted environment secret in memory.
            try:
                decoded_json = base64.b64decode(
                    credentials_base64, validate=True
                ).decode("utf-8")
                credentials_info = json.loads(decoded_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info
                )
            except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError,
                    ValueError, KeyError, TypeError) as exc:
                raise ValueError(
                    "GOOGLE_CREDENTIALS_BASE64 is invalid or incomplete"
                ) from exc
        elif credentials_json:
            # Optional support for a raw JSON environment secret.
            try:
                credentials_info = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info
                )
            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
                raise ValueError(
                    "GOOGLE_CREDENTIALS_JSON is invalid or incomplete"
                ) from exc
        else:
            # Local development: use the existing credentials file.
            if not credentials_path or not Path(credentials_path).is_file():
                raise ValueError("Google credentials file not found")

            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
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
