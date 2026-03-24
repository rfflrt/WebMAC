from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="./static/"), name="static")
templates = Jinja2Templates(directory="templates")

bd = {
    "contador": 0,
    "aba": "curtir"
}

partials = {
        "curtir": "partials/curtidas.html",
        "jupiter": "partials/jupiter.html",
        "professor": "partials/pagina.html"
    }

ordem = list(partials.keys())

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, "contador": bd["contador"], "aba": bd["aba"]
        })

@app.post("/curtir")
async def curtir(request: Request):
    bd["contador"] += 1
    return templates.TemplateResponse("partials/contador.html", {
        "request": request, "contador": bd["contador"]
        })

@app.delete("/curtir")
async def reset(request: Request):
    bd["contador"] = 0
    return templates.TemplateResponse("partials/contador.html", {
        "request": request, "contador": bd["contador"]
        })

@app.get("/aba/{nome}")
async def trocar_aba(request: Request, nome: str):
    bd["aba"] = nome
    
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse("index.html", {
        "request": request, 
        "contador": bd["contador"],
        "aba": bd["aba"]
    })

    return templates.TemplateResponse(partials[nome], {
        "request": request, 
        "contador": bd["contador"],
        "aba": bd["aba"]
    })

@app.get("/proxima")
async def alternar_abas(request: Request):
    idx = ordem.index(bd["aba"])
    idx = (idx + 1) % len(ordem)
    bd["aba"] = ordem[idx]
    
    return templates.TemplateResponse(partials[bd["aba"]], {
        "request": request, 
        "contador": bd["contador"],
        "aba": bd["aba"]
    })