"""구글 OAuth 리프레시 토큰으로 Blogger/YouTube API용 Credentials를 만든다."""

from __future__ import annotations

import os

from google.oauth2.credentials import Credentials

TOKEN_URI = "https://oauth2.googleapis.com/token"

SCOPES = [
    "https://www.googleapis.com/auth/blogger",
    "https://www.googleapis.com/auth/youtube.upload",
]


def get_credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"],
        token_uri=TOKEN_URI,
        client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    # google-api-python-client가 필요할 때 알아서 refresh()를 호출하지만,
    # 여기서 미리 한 번 갱신해 자격증명이 유효한지 바로 확인한다.
    from google.auth.transport.requests import Request

    creds.refresh(Request())
    return creds
