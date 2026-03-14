from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

class Usuario(BaseModel):
    nome: str
    senha: str
    bio: str

usuarios_db = [{"nome": "test", "senha": "test", "bio": "test"}]

@app.get("/")
def get_signup(request: Request):
    return templates.TemplateResponse(
        request=request, name="signup.html"
    )

@app.post("/usuarios")
def criar_usuario(user: Usuario):
    usuarios_db.append(user.model_dump())
    return{"usuario": user.nome}

@app.post("/login")
def login(user: Usuario, response: Response):
    user = user.model_dump()
    usuario_encontrado = None
    for u in usuarios_db:
        if u["nome"] == user["nome"] and u["senha"] == user["senha"]:
            usuario_encontrado = u
            break

    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    response.set_cookie(key="session_user", value = user["nome"])
    return {"message": "Logado com sucesso"}

@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )


def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado: você não está logado")
    
    user = next((u for u in usuarios_db if u["nome"] == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user

@app.get("/home")
def get_home(request: Request, user: dict = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"nome": user["nome"], "bio": user["bio"]}
    )