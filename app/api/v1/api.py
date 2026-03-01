from fastapi import APIRouter
from app.api.v1.endpoints import auth, groups, tree_members

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(tree_members.router, prefix="/groups", tags=["tree-members"])
