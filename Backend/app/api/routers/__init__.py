from fastapi import APIRouter

from app.api.routers.health import router as health_router
from app.api.routers.auth import router as auth_router
from app.api.routers.me import router as me_router
from app.api.routers.crawl import router as crawl_router
from app.api.routers.pdfs import router as pdfs_router
from app.api.routers.search import router as search_router
from app.api.routers.wordclouds import router as wordclouds_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(me_router, tags=["me"])
router.include_router(crawl_router, prefix="/crawl", tags=["crawl"])
router.include_router(pdfs_router, prefix="/pdfs", tags=["pdfs"])
router.include_router(search_router, prefix="/search", tags=["search"])
router.include_router(wordclouds_router, prefix="/wordclouds", tags=["wordclouds"])
