from datetime import datetime, timezone
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from healthos_api.config import get_settings
from healthos_api.crypto import encrypt_token
from healthos_api.models import GarminConnection, RawGarminPayload


class GarminClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def exchange_code(self, code: str, redirect_uri: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                self.settings.garmin_token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self.settings.garmin_client_id,
                    "client_secret": self.settings.garmin_client_secret,
                },
            )
            response.raise_for_status()
            return response.json()

    async def fetch_summary_payloads(self, access_token: str, start_time: str, end_time: str) -> list[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.settings.garmin_api_base_url}/userMetrics",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"uploadStartTimeInSeconds": start_time, "uploadEndTimeInSeconds": end_time},
            )
            response.raise_for_status()
            payload = response.json()
            return payload if isinstance(payload, list) else [payload]


def upsert_connection(db: Session, user_id: UUID, token_payload: dict) -> GarminConnection:
    connection = db.query(GarminConnection).filter(GarminConnection.user_id == user_id).one_or_none()
    if connection is None:
        connection = GarminConnection(
            user_id=user_id,
            encrypted_access_token="",
            encrypted_refresh_token="",
            scopes=[],
        )
        db.add(connection)

    connection.encrypted_access_token = encrypt_token(token_payload["access_token"])
    connection.encrypted_refresh_token = encrypt_token(token_payload.get("refresh_token", ""))
    connection.scopes = token_payload.get("scope", "").split() if isinstance(token_payload.get("scope"), str) else token_payload.get("scope", [])
    connection.token_expires_at = datetime.now(timezone.utc)
    connection.last_error = None
    db.commit()
    db.refresh(connection)
    return connection


def store_raw_payload(db: Session, user_id: UUID, payload_type: str, payload: dict, external_id: str | None = None) -> RawGarminPayload:
    raw = RawGarminPayload(user_id=user_id, payload_type=payload_type, payload=payload, external_id=external_id)
    db.add(raw)
    db.commit()
    db.refresh(raw)
    return raw

