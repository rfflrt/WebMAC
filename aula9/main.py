# Arquivo main.py

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import Aluno
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select, col

@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=initFunction)
app.mount("/Static", StaticFiles(directory="static"), name="static")

arquivo_sqlite = "HTMX2.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
 
def buscar_alunos(busca):
    with Session(engine) as session:
        query = select(Aluno).where(col(Aluno.nome).contains(busca)).order_by(Aluno.nome)
        return session.exec(query).all()
    
@app.get("/", response_class=HTMLResponse)
def busca(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/busca", response_class=HTMLResponse)
def busca(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str | None='', pagina: int = 1):
    ITENS_POR_PAGINA = 10
    todos_alunos = buscar_alunos(busca)
    
    total = len(todos_alunos)
    total_paginas = max(1, -(-total // ITENS_POR_PAGINA))  # ceil division
    pagina = max(1, min(pagina, total_paginas))             # clamp
    
    inicio = (pagina - 1) * ITENS_POR_PAGINA
    alunos = todos_alunos[inicio : inicio + ITENS_POR_PAGINA]
    
    return templates.TemplateResponse(request, "lista.html", {
        "alunos": alunos,
        "pagina": pagina,
        "total_paginas": total_paginas,
        "busca": busca,
    })
    
@app.get("/editarAlunos")
def novoAluno(request: Request):
    return templates.TemplateResponse(request, "options.html")

@app.post("/novoAluno", response_class=HTMLResponse)
def criar_aluno(nome: str = Form(...)):
    with Session(engine) as session:
        novo_aluno = Aluno(nome=nome)
        session.add(novo_aluno)
        session.commit()
        session.refresh(novo_aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {novo_aluno.nome} foi registrado(a)!</p>")
    
@app.delete("/deletaAluno", response_class=HTMLResponse)
def deletar_aluno(id: int):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if (not aluno):
            raise HTTPException(404, "Aluno não encontrado")
        session.delete(aluno)
        session.commit()
        return HTMLResponse(content=f"<p>O(a) aluno(a) {aluno.nome} foi deletado(a)!</p>")

@app.put("/atualizaAluno", response_class=HTMLResponse)
def atualizar_aluno(id: int = Form(...), novoNome: str = Form(...)):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if (not aluno):
            raise HTTPException(404, "Aluno não encontrado")
        nomeAntigo = aluno.nome
        aluno.nome = novoNome
        session.commit()
        session.refresh(aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {nomeAntigo} foi atualizado(a) para {aluno.nome}!</p>")

@app.delete("/apagar", response_class=HTMLResponse)
def apagar():
    return ""