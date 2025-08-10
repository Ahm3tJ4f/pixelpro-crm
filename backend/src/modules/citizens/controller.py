from fastapi import APIRouter
from src.modules.auth.service import GetOperatorUser
from src.modules.citizens.model import PinCodePath, CitizenResponse
from src.modules.citizens.service import CitizenServiceDep

router = APIRouter(prefix="/citizens", tags=["Citizens"])


@router.get("/{pinCode}", response_model=CitizenResponse)
async def get_citizen(
    pin_code: PinCodePath,
    citizen_service: CitizenServiceDep,
    current_user: GetOperatorUser,
) -> CitizenResponse:

    return await citizen_service.get_citizen(pin_code)
