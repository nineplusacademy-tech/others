"""유튜브 쇼츠 업로드."""

from __future__ import annotations

from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from google_auth import get_credentials

EDUCATION_CATEGORY_ID = "27"


def upload_shorts(video_path: Path, title: str, description: str) -> str:
    """숏폼 영상을 업로드하고 영상 URL을 반환한다.

    제목/설명에 "#Shorts"가 없으면 유튜브가 쇼츠로 인식하지 않을 수 있어
    자동으로 덧붙인다(이미 있으면 중복 추가하지 않음).
    """
    creds = get_credentials()
    service = build("youtube", "v3", credentials=creds)

    if "#shorts" not in description.lower() and "#shorts" not in title.lower():
        description = f"{description}\n\n#Shorts"

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    request = service.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": EDUCATION_CATEGORY_ID,
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=media,
    )

    response = None
    while response is None:
        _, response = request.next_chunk()

    video_id = response["id"]
    return f"https://youtube.com/shorts/{video_id}"
