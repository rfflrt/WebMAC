from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

class Usuario(BaseModel):
    nome: str
    #senha: str
    bio: str

usuarios_db = []

@app.get("/")
def get_home(request: Request):
    return templates.TemplateResponse(
        request=request, name="signup.html"
    )

@app.post("/usuarios")
def criar_usuario(user: Usuario):
    usuarios_db.append(user.model_dump())
    return{"usuario": user.nome}