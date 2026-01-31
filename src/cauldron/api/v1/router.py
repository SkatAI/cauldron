from fastapi import APIRouter

from cauldron.api.v1.endpoints.validation import router as validation_router

v1_router = APIRouter()
v1_router.include_router(validation_router)
