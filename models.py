from pydantic import BaseModel
from typing import Optional
from datetime import datetime

#empresa
class EmpresaCreate(BaseModel):
    id: str #codigo gs1
    nombre: str
    nit: Optional[str] = None
    email_contacto: Optional[str] = None

class EmpresaOut(BaseModel):
    id: str
    nombre: str
    nit: Optional[str]
    created_at: Optional[datetime]

#gtin
class GTINCreate(BaseModel):
    gtin: str
    descripcion: Optional[str] = None
    activo: bool = True
    empresa_id: str

class GTINUpdate(BaseModel):
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class GTINOut(BaseModel):
    id: str
    gtin: str
    descripcion: Optional[str]
    activo: bool
    empresa_id: str
    created_at: Optional[datetime]

#gln
class GLNCreate(BaseModel):
    gln: str
    descripcion: Optional[str] = None
    activo: bool = True
    empresa_id: str

class GLNUpdate(BaseModel):
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class GLNOut(BaseModel):
    id: str
    gln: str
    descripcion: Optional[str]
    activo: bool
    empresa_id: str
    created_at: Optional[datetime]

#auth
class LoginInput(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    empresa_id: Optional[str]