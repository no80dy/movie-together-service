import json
from typing import Annotated

from fastapi import APIRouter, Depends
from faststream.rabbit.fastapi import RabbitRouter

from schemas.broker import PartyCreationMessage
from services.broker import PartyManagerService, get_party_manager_service
from .auth import security_jwt

router = APIRouter()


# @router.post("/party-creation")
# async def create_party(
#     party_creation_message: PartyCreationMessage,
#     party_manager_service: Annotated[
#         PartyManagerService, Depends(get_party_manager_service)
#     ],
# ):
#     result = await party_manager_service.create_party(party_creation_message)
#     return {"redirect_url": f"http://localhost/party-manager-service/api/v1/stream/{result}"}


@router.get("/party-ready")
async def check_party_id(
    user_data: Annotated[dict, Depends(security_jwt)],
    party_manager_service: Annotated[
        PartyManagerService, Depends(get_party_manager_service)
    ],
):
    """Проверяет готовность пати для фронта."""
    result = await party_manager_service.find_party_id_by_user_id(user_data["user_id"])
    if not result:
        return {"redirect_url": "None"}
    print(result)
    return {"redirect_url": f"http://localhost/party-manager-service/api/v1/stream/{result['party_id']}"}
