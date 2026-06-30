from fastapi import APIRouter, HTTPException, Depends
from database import supabase
from models import GTINCreate, GTINUpdate, GTINOut
from auth import solo_admin, admin_o_cliente

router = APIRouter(prefix="/gtins", tags=["GTINs"])

@router.get("/", response_model=list[GTINOut])
def listar_gtins(payload: dict = Depends(admin_o_cliente)):
    rol = payload.get("rol")
    empresa_id = payload.get("empresa_id")

    if rol == "admin":
        result = supabase.table("gtins").select("*").execute()
    else:
        if not empresa_id:
            raise HTTPException(status_code=403, detail="Cliente sin empresa asignada")
        result = supabase.table("gtins").select("*").eq("empresa_id", empresa_id).execute()

    return result.data

@router.get("/{gtin}", response_model=GTINOut)
def obtener_gtin(gtin: str, payload: dict = Depends(admin_o_cliente)):
    rol = payload.get("rol")
    empresa_id = payload.get("empresa_id")

    result = supabase.table("gtins").select("*").eq("gtin", gtin).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="GTIN no encontrado")

    # Cliente solo puede ver GTINs de su empresa
    if rol == "cliente" and result.data["empresa_id"] != empresa_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este GTIN")

    return result.data

@router.post("/", response_model=GTINOut, status_code=201)
def crear_gtin(gtin: GTINCreate, payload: dict = Depends(solo_admin)):
    existe = supabase.table("gtins").select("id").eq("gtin", gtin.gtin).execute()
    if existe.data:
        raise HTTPException(status_code=400, detail="GTIN ya registrado")

    result = supabase.table("gtins").insert(gtin.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear GTIN")
    return result.data[0]

@router.put("/{gtin_id}", response_model=GTINOut)
def actualizar_gtin(gtin_id: str, datos: GTINUpdate, payload: dict = Depends(solo_admin)):
    existe = supabase.table("gtins").select("id").eq("id", gtin_id).execute()
    if not existe.data:
        raise HTTPException(status_code=404, detail="GTIN no encontrado")

    actualizacion = {k: v for k, v in datos.model_dump().items() if v is not None or k == "activo"}
    if not actualizacion:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    result = supabase.table("gtins").update(actualizacion).eq("id", gtin_id).execute()
    return result.data[0]

@router.delete("/{gtin_id}", status_code=204)
def eliminar_gtin(gtin_id: str, payload: dict = Depends(solo_admin)):
    existe = supabase.table("gtins").select("id").eq("id", gtin_id).execute()
    if not existe.data:
        raise HTTPException(status_code=404, detail="GTIN no encontrado")

    supabase.table("gtins").delete().eq("id", gtin_id).execute()