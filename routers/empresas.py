from fastapi import APIRouter, HTTPException
from database import supabase
from models import EmpresaCreate, EmpresaOut
from auth import solo_admin
from fastapi import Depends

router = APIRouter(prefix="/empresas", tags=["Empresas"])

@router.get("/", response_model=list[EmpresaOut])
def listar_empresas(payload: dict = Depends(solo_admin)):
    result = supabase.table("empresas").select("*").execute()
    return result.data

@router.get("/{empresa_id}", response_model=EmpresaOut)
def obtener_empresa(empresa_id: str, payload: dict = Depends(solo_admin)):
    result = supabase.table("empresas").select("*").eq("id", empresa_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return result.data

@router.post("/", response_model=EmpresaOut, status_code=201)
def crear_empresa(empresa: EmpresaCreate, payload: dict = Depends(solo_admin)):
    # Verificar que no exista ya
    existe = supabase.table("empresas").select("id").eq("id", empresa.id).execute()
    if existe.data:
        raise HTTPException(status_code=400, detail="Ya existe una empresa con ese ID")
    
    result = supabase.table("empresas").insert(empresa.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear empresa")
    return result.data[0]

@router.delete("/{empresa_id}", status_code=204)
def eliminar_empresa(empresa_id: str, payload: dict = Depends(solo_admin)):
    existe = supabase.table("empresas").select("id").eq("id", empresa_id).execute()
    if not existe.data:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    supabase.table("empresas").delete().eq("id", empresa_id).execute()