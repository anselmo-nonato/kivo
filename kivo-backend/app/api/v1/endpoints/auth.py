from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_mfa_challenge_token,
    decode_token,
    generate_totp_secret,
    get_totp_uri,
    generate_qr_code_base64,
    verify_totp_code,
    generate_backup_codes,
)
from app.models import (
    User,
    UserBackupCode,
    Workspace,
    WorkspaceMember,
    WorkspaceType,
    MemberRole,
    CostCenter,
    CostCenterScope,
    Category
)
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    MFAChallengeResponse,
    MFASetupResponse,
    MFAEnableRequest,
    MFAVerifyRequest,
    MFADisableRequest,
    UserResponse,
    WorkspaceBriefResponse
)
from app.api.deps import get_current_user

router = APIRouter()

def build_user_response(user: User) -> UserResponse:
    """Helper para formatar resposta do usuário com seus workspaces."""
    workspaces_list = []
    if user.memberships:
        for m in user.memberships:
            if m.workspace:
                workspaces_list.append(
                    WorkspaceBriefResponse(
                        id=m.workspace.id,
                        name=m.workspace.name,
                        type=m.workspace.type.value,
                        role=m.role.value
                    )
                )
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at,
        workspaces=workspaces_list
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="Registro de Novo Usuário")
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Cadastra novo usuário, gera seu workspace Solo inicial e retorna os tokens de acesso.
    """
    # 1. Verifica se email já existe
    stmt = select(User).where(User.email == req.email.lower().strip())
    existing_user = (await db.execute(stmt)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma conta cadastrada com este endereço de e-mail."
        )

    # 2. Cria usuário
    new_user = User(
        id=uuid.uuid4(),
        email=req.email.lower().strip(),
        password_hash=get_password_hash(req.password),
        full_name=req.full_name.strip(),
        is_active=True,
        mfa_enabled=False
    )
    db.add(new_user)
    await db.flush()

    # 3. Cria Workspace Solo Padrão
    solo_workspace = Workspace(
        id=uuid.uuid4(),
        name=req.initial_workspace_name or "Minhas Finanças (Solo)",
        type=WorkspaceType.SOLO,
        owner_id=new_user.id,
        currency="BRL"
    )
    db.add(solo_workspace)
    await db.flush()

    # 4. Adiciona como Owner
    member = WorkspaceMember(
        id=uuid.uuid4(),
        workspace_id=solo_workspace.id,
        user_id=new_user.id,
        role=MemberRole.OWNER,
        display_name=new_user.full_name,
        declared_income=0.00
    )
    db.add(member)
    await db.flush()

    # 5. Cria Centros de Custo Padrão
    cc_pessoal = CostCenter(
        id=uuid.uuid4(),
        workspace_id=solo_workspace.id,
        name="Pessoal",
        scope=CostCenterScope.INDIVIDUAL,
        assigned_member_id=member.id
    )
    cc_casa = CostCenter(
        id=uuid.uuid4(),
        workspace_id=solo_workspace.id,
        name="Casa / Moradia",
        scope=CostCenterScope.HOME,
        assigned_member_id=member.id
    )
    db.add_all([cc_pessoal, cc_casa])

    # 6. Cria Categorias Padrão
    cats = [
        Category(id=uuid.uuid4(), workspace_id=solo_workspace.id, name="Alimentação", icon="utensils", color="#10B981"),
        Category(id=uuid.uuid4(), workspace_id=solo_workspace.id, name="Moradia", icon="home", color="#3B82F6"),
        Category(id=uuid.uuid4(), workspace_id=solo_workspace.id, name="Transporte", icon="car", color="#F59E0B"),
        Category(id=uuid.uuid4(), workspace_id=solo_workspace.id, name="Saúde", icon="heart-pulse", color="#EF4444"),
        Category(id=uuid.uuid4(), workspace_id=solo_workspace.id, name="Lazer & Conforto", icon="sparkles", color="#8B5CF6"),
        Category(id=uuid.uuid4(), workspace_id=solo_workspace.id, name="Receitas", icon="trending-up", color="#00D084"),
    ]
    db.add_all(cats)
    await db.commit()

    # 7. Recarrega com relacionamentos
    stmt = select(User).where(User.id == new_user.id).options(
        selectinload(User.memberships).selectinload(WorkspaceMember.workspace)
    )
    loaded_user = (await db.execute(stmt)).scalar_one()

    access_token = create_access_token(loaded_user.id)
    refresh_token = create_refresh_token(loaded_user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        user=build_user_response(loaded_user)
    )


@router.post("/login", summary="Login do Usuário")
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Etapa 1 do Login: Verifica credenciais.
    Se o 2FA estiver ativado, retorna um token efêmero para a Etapa 2.
    Caso contrário, retorna diretamente os tokens de acesso.
    """
    stmt = select(User).where(User.email == req.email.lower().strip()).options(
        selectinload(User.memberships).selectinload(WorkspaceMember.workspace)
    )
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Entre em contato com o suporte."
        )

    # Se 2FA estiver ativado, emite desafio
    if user.mfa_enabled:
        mfa_token = create_mfa_challenge_token(user.id)
        return MFAChallengeResponse(
            mfa_required=True,
            mfa_token=mfa_token,
            message="Autenticação em 2 etapas requerida. Forneça o código do Google Authenticator ou backup code."
        )

    # Login direto sem 2FA
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        user=build_user_response(user)
    )


@router.post("/2fa/setup", response_model=MFASetupResponse, summary="Iniciar Configuração de 2FA")
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Gera novo segredo TOTP, QR Code e 8 códigos de backup.
    O 2FA só é ativado após a chamada a /2fa/enable.
    """
    secret = generate_totp_secret()
    otpauth_uri = get_totp_uri(secret, current_user.email)
    qr_code = generate_qr_code_base64(otpauth_uri)
    
    plain_backups, hashed_backups = generate_backup_codes(8)

    # Salva segredo temporário no usuário
    current_user.mfa_secret = secret
    
    # Remove códigos de backup antigos se houver e insere os novos
    stmt = select(UserBackupCode).where(UserBackupCode.user_id == current_user.id)
    existing_codes = (await db.execute(stmt)).scalars().all()
    for c in existing_codes:
        await db.delete(c)

    for h in hashed_backups:
        db.add(UserBackupCode(
            id=uuid.uuid4(),
            user_id=current_user.id,
            code_hash=h
        ))

    await db.commit()

    return MFASetupResponse(
        secret=secret,
        otpauth_uri=otpauth_uri,
        qr_code_base64=qr_code,
        backup_codes=plain_backups
    )


@router.post("/2fa/enable", response_model=UserResponse, summary="Confirmar e Ativar 2FA")
async def enable_2fa(
    req: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Valida o primeiro código de 6 dígitos gerado pelo app no celular e ativa o 2FA.
    """
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma configuração de 2FA em andamento. Chame /api/v1/auth/2fa/setup primeiro."
        )

    is_valid = verify_totp_code(current_user.mfa_secret, req.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de autenticação inválido. Verifique o relógio do seu celular e tente novamente."
        )

    current_user.mfa_enabled = True
    await db.commit()
    await db.refresh(current_user)

    return build_user_response(current_user)


@router.post("/2fa/verify", response_model=TokenResponse, summary="Validar 2FA na Etapa 2 do Login")
async def verify_2fa(req: MFAVerifyRequest, db: AsyncSession = Depends(get_db)):
    """
    Valida o código de 6 dígitos ou um código de backup na segunda etapa do login.
    """
    payload = decode_token(req.mfa_token, expected_type="mfa_challenge")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de desafio 2FA expirado ou inválido. Faça login novamente."
        )

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id).options(
        selectinload(User.backup_codes),
        selectinload(User.memberships).selectinload(WorkspaceMember.workspace)
    )
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inválido ou 2FA inativo.")

    clean_code = req.code.strip()
    is_authenticated = False

    # 1. Tenta validação TOTP (6 dígitos)
    if len(clean_code) == 6 and clean_code.isdigit():
        if verify_totp_code(user.mfa_secret, clean_code):
            is_authenticated = True

    # 2. Se não bateu TOTP, tenta código de backup
    if not is_authenticated and user.backup_codes:
        for backup_code_entry in user.backup_codes:
            if backup_code_entry.used_at is None:
                if verify_password(clean_code, backup_code_entry.code_hash):
                    # Marca como usado
                    backup_code_entry.used_at = datetime.now(timezone.utc)
                    await db.commit()
                    is_authenticated = True
                    break

    if not is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de autenticação ou de recuperação inválido."
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        user=build_user_response(user)
    )


@router.post("/2fa/disable", response_model=UserResponse, summary="Desativar 2FA")
async def disable_2fa(
    req: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Desativa o 2FA mediante confirmação de senha + código atual de segurança.
    """
    if not verify_password(req.password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta.")

    if not verify_totp_code(current_user.mfa_secret, req.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código 2FA incorreto.")

    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    
    # Remove códigos de backup
    stmt = select(UserBackupCode).where(UserBackupCode.user_id == current_user.id)
    codes = (await db.execute(stmt)).scalars().all()
    for c in codes:
        await db.delete(c)

    await db.commit()
    await db.refresh(current_user)

    return build_user_response(current_user)


@router.get("/me", response_model=UserResponse, summary="Dados do Usuário Autenticado")
async def get_me(current_user: User = Depends(get_current_user)):
    """Retorna dados do perfil e workspaces do usuário logado."""
    return build_user_response(current_user)


@router.post("/refresh", response_model=TokenResponse, summary="Renovar Access Token")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Gera um novo Access Token usando o Refresh Token."""
    payload = decode_token(refresh_token, expected_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado."
        )

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id).options(
        selectinload(User.memberships).selectinload(WorkspaceMember.workspace)
    )
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido ou inativo.")

    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=new_refresh_token,
        user=build_user_response(user)
    )
