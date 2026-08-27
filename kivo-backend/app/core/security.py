import io
import os
import base64
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
import jwt
from passlib.context import CryptContext
import qrcode
import pyotp
from app.core.config import settings

# Contexto de Hashing com Argon2 e Fallback para Bcrypt
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Gera hash seguro da senha usando Argon2id."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro bate com o hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Cria Access Token JWT de curta duração (15 min)."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: str) -> str:
    """Cria Refresh Token JWT de longa duração (30 dias)."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def create_mfa_challenge_token(user_id: str) -> str:
    """Cria token de desafio temporário para segunda etapa do 2FA (5 minutos)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    payload = {
        "sub": str(user_id),
        "type": "mfa_challenge",
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str, expected_type: str = "access") -> Optional[dict]:
    """Decodifica e valida assinatura e expiração de um JWT."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            return None
        return payload
    except jwt.PyJWTError:
        return None

# ==================== 2FA / TOTP (RFC 6238) ====================

def generate_totp_secret() -> str:
    """Gera chave secreta Base32 para TOTP."""
    return pyotp.random_base32()

def get_totp_uri(secret: str, email: str) -> str:
    """Gera URI otpauth para aplicativos autenticadores."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="KIVO Finanças")

def generate_qr_code_base64(otpauth_uri: str) -> str:
    """Gera imagem PNG em base64 do QR Code para o app do celular."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(otpauth_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#051329", back_color="#FFFFFF")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

def verify_totp_code(secret: str, code: str) -> bool:
    """Verifica código de 6 dígitos TOTP com janela de tolerância de +-30s."""
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    # valid_window=1 aceita 30s antes ou 30s depois para evitar problemas de desvio de relógio
    return totp.verify(code.strip(), valid_window=1)

def generate_backup_codes(count: int = 8) -> Tuple[List[str], List[str]]:
    """
    Gera códigos de backup legíveis e seus respectivos hashes.
    Retorna (plain_codes, hashed_codes).
    """
    chars = string.ascii_uppercase + string.digits
    # Remove caracteres ambíguos (0, O, 1, I)
    chars = chars.replace("0", "").replace("O", "").replace("1", "").replace("I", "")
    
    plain_codes = []
    hashed_codes = []
    
    for _ in range(count):
        code = f"{''.join(secrets.choice(chars) for _ in range(5))}-{''.join(secrets.choice(chars) for _ in range(5))}"
        plain_codes.append(code)
        hashed_codes.append(get_password_hash(code))
        
    return plain_codes, hashed_codes
