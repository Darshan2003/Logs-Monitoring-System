from fastapi import APIRouter
from src.endpoints import features_endp

router = APIRouter()
router.include_router(features_endp.router)
