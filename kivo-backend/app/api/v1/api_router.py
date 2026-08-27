from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, workspaces, financial, intelligence

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação & 2FA"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces & Membros"])
api_router.include_router(financial.router, prefix="/workspaces", tags=["Financeiro (Contas, Categorias, Tags & Transações)"])
api_router.include_router(intelligence.router, prefix="/workspaces", tags=["Inteligência Financeira (Equalização Casal, Dívidas, DTI & Simulador)"])
