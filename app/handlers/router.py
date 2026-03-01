from aiogram import Router

from app.handlers.main_handler import router as main_router
from app.handlers.status import router as status_router
from app.handlers.delete import router as delete_router
from app.handlers.record import router as record_router
from app.handlers.other import router as redact_router

router = Router()
router.include_router(main_router)
router.include_router(status_router)
router.include_router(delete_router)
router.include_router(record_router)
router.include_router(redact_router)