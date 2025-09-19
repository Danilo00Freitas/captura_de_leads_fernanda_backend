from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI()

# Permitir que seu front-end faça requisições (substitua pelo domínio real)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho do PDF
BASE_DIR = Path(__file__).parent  # diretório onde está o main.py
PDF_FILE_PATH = BASE_DIR / "pdf" / "material-congresso-19.09.2025.pdf"

# Cria tabela de leads se não existir
def init_db():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            instagram TEXT
        )
    """)
    conn.commit()
    conn.close()
init_db()

@app.post("/leads")
async def capture_lead(request: Request):
    data = await request.json()
    nome = data.get("nome", "").strip()
    email = data.get("email", "").strip()
    instagram = data.get("instagram", "").strip()
    telefone = data.get("telefone", "").strip()

    # Validação simples
    if not nome or not email:
        raise HTTPException(status_code=400, detail="Nome e email são obrigatórios!")
    if instagram and not instagram.startswith("@"):
        raise HTTPException(status_code=400, detail="Instagram inválido!")
    if not telefone.isdigit() or len(telefone) != 11:
        raise HTTPException(status_code=400, detail="Telefone inválido!")

    # Salva no banco
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leads (nome, email, instagram, telefone) VALUES (?, ?, ?, ?)",
        (nome, email, instagram, telefone)
    )
    conn.commit()
    conn.close()

    # Retorna o PDF como download
    if not os.path.exists(PDF_FILE_PATH):
        raise HTTPException(status_code=404, detail="Arquivo PDF não encontrado.")

    return FileResponse(
        PDF_FILE_PATH,
        media_type="application/pdf",
        filename="material-congresso-19.09.2025.pdf"
    )
