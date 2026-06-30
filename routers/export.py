from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from database import supabase
from auth import admin_o_cliente
import csv
import json
import io

router = APIRouter(prefix="/export", tags=["Export"])

def filtrar_por_rol(tabla: str, payload: dict, codigo: str = None):
    rol = payload.get("rol")
    empresa_id = payload.get("empresa_id")

    query = supabase.table(tabla).select("*")

    if codigo:
        campo = "gtin" if tabla == "gtins" else "gln"
        query = query.eq(campo, codigo)

    if rol == "cliente":
        if not empresa_id:
            raise HTTPException(status_code=403, detail="Cliente sin empresa asignada")
        query = query.eq("empresa_id", empresa_id)

    result = query.execute()
    return result.data

@router.get("/gtins")
def exportar_gtins(
    formato: str = Query("json", enum=["json", "csv"]),
    gtin: str = Query(None),
    empresa_id: str = Query(None),
    payload: dict = Depends(admin_o_cliente)
):
    datos = filtrar_por_rol("gtins", payload, codigo=gtin)
    if payload.get("rol") == "admin" and empresa_id:
        datos = [d for d in datos if d["empresa_id"] == empresa_id]
    if not datos:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return generar_respuesta(datos, formato, "gtins")

@router.get("/glns")
def exportar_glns(
    formato: str = Query("json", enum=["json", "csv"]),
    gln: str = Query(None),
    empresa_id: str = Query(None),
    payload: dict = Depends(admin_o_cliente)
):
    datos = filtrar_por_rol("glns", payload, codigo=gln)
    if payload.get("rol") == "admin" and empresa_id:
        datos = [d for d in datos if d["empresa_id"] == empresa_id]
    if not datos:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return generar_respuesta(datos, formato, "glns")

def generar_respuesta(datos: list, formato: str, nombre: str) -> StreamingResponse:
    if formato == "json":
        contenido = json.dumps(datos, indent=2, default=str)
        return StreamingResponse(
            io.StringIO(contenido),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={nombre}.json"}
        )
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=datos[0].keys())
    writer.writeheader()
    writer.writerows(datos)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nombre}.csv"}
    )

    # Transforma booleanos para CSV
    datos_csv = []
    for row in datos:
        fila = dict(row)
        if "activo" in fila:
            fila["activo"] = "Activo" if fila["activo"] else "Inactivo"
        datos_csv.append(fila)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=datos_csv[0].keys())
    writer.writeheader()
    writer.writerows(datos_csv)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nombre}.csv"}
    )