from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Senha com no mínimo 8 caracteres")
    full_name: str = Field(..., min_length=2, max_length=150)
    initial_workspace_name: Optional[str] = "Minhas Finanças (Solo)"

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str
    user: "UserResponse"

class MFAChallengeResponse(BaseModel):
    mfa_required: bool = True
    mfa_token: str
    message: str = "Autenticação em 2 etapas necessária. Digite o código de 6 dígitos do Google Authenticator ou um código de recuperação."

class MFASetupResponse(BaseModel):
    secret: str
    otpauth_uri: str
    qr_code_base64: str
    backup_codes: List[str]
    instructions: str = "1. Escaneie o QR Code no Google Authenticator ou Authy. 2. Guarde seus 8 códigos de backup em local seguro. 3. Envie o primeiro código de 6 dígitos para /api/v1/auth/2fa/enable para confirmar."

class MFAEnableRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, description="Código de 6 dígitos do app")

class MFAVerifyRequest(BaseModel):
    mfa_token: str
    code: str = Field(..., min_length=6, description="Código de 6 dígitos ou Código de Backup (XXXXX-XXXXX)")

class MFADisableRequest(BaseModel):
    password: str
    code: str

class WorkspaceBriefResponse(BaseModel):
    id: UUID
    name: str
    type: str
    role: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    workspaces: List[WorkspaceBriefResponse] = []

    class Config:
        from_attributes = True

TokenResponse.model_rebuild()
