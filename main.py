from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import LoginInput, TokenOut
from auth import login as auth_login
from routers.gtins import router as gtins_router
from routers.glns import router as glns_router
from routers.empresas import router as empresas_router
from routers.export import router as export_router

app = FastAPI(
    title="GS1 El Salvador API",
    description="API para gestión de GTINs y GLNs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/auth/login", response_model=TokenOut)
async def login(datos: LoginInput):
    return await auth_login(datos.email, datos.password)

@app.get("/")
def root():
    return {"mensaje": "GS1 El Salvador API activa"}

app.include_router(gtins_router)
app.include_router(glns_router)
app.include_router(empresas_router)
app.include_router(export_router)