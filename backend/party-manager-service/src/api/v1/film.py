from typing import Annotated

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
    result = await party_manager_service.create_party(party_creation_message)
    return {"redirect_url": f"http://localhost:8000/sream/{result}"}
