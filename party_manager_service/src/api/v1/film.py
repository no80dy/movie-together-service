from typing import Annotated

from fastapi import APIRouter, Depends
from services.broker import PartyManagerService, get_party_manager_service

from .auth import decode_token, security_jwt

router = APIRouter()


@router.get("/party-ready")
async def check_party_id(
    token: Annotated[dict, Depends(security_jwt)],
    party_manager_service: Annotated[
        PartyManagerService, Depends(get_party_manager_service)
    ],
):
    """Проверяет готовность пати для фронта и отправляет ссылку на стрим."""
    user_data = decode_token(token)
    result = await party_manager_service.find_party_id_by_user_id(
        user_data["user_id"]
    )
    if not result:
        return {"redirect_url": "None"}
    print(result)
    return {
        "redirect_url": f"http://localhost/party-manager-service/api/v1/stream/{result['party_id']}"
    }
