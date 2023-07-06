from unittest import mock

import pytest
from sqlalchemy import func, select


@pytest.mark.asyncio
async def test_signup(async_client, headers):
    request_data = {
        "user": {
            "email": "SanyokGarbunek@vas.ru",
            "country": "US",
            "locale": "en_US",
            "phone_number": "+449534771093",
            "nickname": "Sanya",
            "password1": "string",
            "password2": "string"
        },
        "company": {
            "title": "GORA I KOMUTA",
            "locale": "en_US",
            "country": "US",
            "currency": "USD"
        }
    }

    response = await async_client.post("/api/user/signup", json=request_data)
    assert response.status_code == 200
