from typing import Annotated

from core.config import settings
from fastapi import APIRouter, Depends
from schemas.broker import PartyCreationMessage
from services.broker import PartyManagerService, get_party_manager_service

router = APIRouter()


@router.post("/party-creation")
async def create_party(
    party_creation_message: PartyCreationMessage,
    party_manager_service: Annotated[
        PartyManagerService, Depends(get_party_manager_service)
    ],
):
    party_id = await party_manager_service.create_party(party_creation_message)
    return {"redirect_url": f"{settings.party_manager_service_url}/{party_id}"}
