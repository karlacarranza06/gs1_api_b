from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import supabase
import os

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 2

security = HTTPBearer()

def crear_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

def solo_admin(payload: dict = Depends(verificar_token)) -> dict:
    if payload.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores"
        )
    return payload

def admin_o_cliente(payload: dict = Depends(verificar_token)) -> dict:
    if payload.get("rol") not in ("admin", "cliente"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado"
        )
    return payload

async def login(email: str, password: str) -> dict:
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except Exception as e:
        print(f"ERROR SUPABASE: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    user = response.user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

# Obtener perfil del usuario
    perfil = supabase.table("perfiles").select("*").eq("id", user.id).single().execute()
    if not perfil.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sin perfil asignado"
        )

    rol = perfil.data["rol"]
    empresa_id = perfil.data.get("empresa_id")

    token = crear_token({
        "sub": user.id,
        "email": user.email,
        "rol": rol,
        "empresa_id": empresa_id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": rol,
        "empresa_id": empresa_id
    }


