from fastapi import APIRouter, HTTPException, Depends
from database import supabase
from models import GLNCreate, GLNUpdate, GLNOut
from auth import solo_admin, admin_o_cliente

router = APIRouter(prefix="/glns", tags=["GLNs"])

@router.get("/", response_model=list[GLNOut])
def listar_glns(payload: dict = Depends(admin_o_cliente)):
    rol = payload.get("rol")
    empresa_id = payload.get("empresa_id")

    if rol == "admin":
        result = supabase.table("glns").select("*").execute()
    else:
        if not empresa_id:
            raise HTTPException(status_code=403, detail="Cliente sin empresa asignada")
        result = supabase.table("glns").select("*").eq("empresa_id", empresa_id).execute()

    return result.data

@router.get("/{gln}", response_model=GLNOut)
def obtener_gln(gln: str, payload: dict = Depends(admin_o_cliente)):
    rol = payload.get("rol")
    empresa_id = payload.get("empresa_id")

    result = supabase.table("glns").select("*").eq("gln", gln).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="GLN no encontrado")

    if rol == "cliente" and result.data["empresa_id"] != empresa_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este GLN")

    return result.data

@router.post("/", response_model=GLNOut, status_code=201)
def crear_gln(gln: GLNCreate, payload: dict = Depends(solo_admin)):
    existe = supabase.table("glns").select("id").eq("gln", gln.gln).execute()
    if existe.data:
        raise HTTPException(status_code=400, detail="GLN ya registrado")

    result = supabase.table("glns").insert(gln.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear GLN")
    return result.data[0]

@router.put("/{gln_id}", response_model=GLNOut)
def actualizar_gln(gln_id: str, datos: GLNUpdate, payload: dict = Depends(solo_admin)):
    existe = supabase.table("glns").select("id").eq("id", gln_id).execute()
    if not existe.data:
        raise HTTPException(status_code=404, detail="GLN no encontrado")

    actualizacion = {k: v for k, v in datos.model_dump().items() if v is not None or k == "activo"}
    if not actualizacion:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    result = supabase.table("glns").update(actualizacion).eq("id", gln_id).execute()
    return result.data[0]

@router.delete("/{gln_id}", status_code=204)
def eliminar_gln(gln_id: str, payload: dict = Depends(solo_admin)):
    existe = supabase.table("glns").select("id").eq("id", gln_id).execute()
    if not existe.data:
        raise HTTPException(status_code=404, detail="GLN no encontrado")

    supabase.table("glns").delete().eq("id", gln_id).execute()