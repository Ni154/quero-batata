from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client
import jwt
import datetime
from reportlab.pdfgen import canvas
import os
import uuid

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://jptsbutoikieipwnlbft.supabase.co"
SUPABASE_KEY = "sb_secret_KTTNWWrjuuuPL3CQRdHo-Q_1lcYZfFt"
JWT_SECRET = "sua_chave_secreta_muito_forte"  # mantenha segura

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Pasta para salvar PDFs
PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    usuario = data.get("usuario")
    senha = data.get("senha")

    res = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("senha", senha).execute()

    if res.data:
        token = jwt.encode({
            "usuario": usuario,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }, JWT_SECRET, algorithm="HS256")

        return jsonify({"token": token, "usuario": usuario})

    return jsonify({"erro": "Usuário ou senha incorretos"}), 401


@app.route("/api/pedido", methods=["POST"])
def pedido():
    data = request.json
    nome = data.get("nome")
    endereco = data.get("endereco")
    telefone = data.get("telefone")
    produtos = data.get("produtos")  # espera lista de dicts [{nome, preco}, ...]
    taxa_entrega = data.get("taxa_entrega", 5.0)
    total = data.get("total")
    datahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Salvar no Supabase (converta lista para string JSON, se preferir)
    supabase.table("pedidos").insert({
        "nome_cliente": nome,
        "telefone": telefone,
        "endereco": endereco,
        "produtos": str(produtos),  # ou use json.dumps(produtos)
        "taxa_entrega": taxa_entrega,
        "total": total,
        "criado_em": datahora
    }).execute()

    # Gerar PDF
    filename = f"{uuid.uuid4().hex[:8]}_{nome.replace(' ', '_')}.pdf"
    path = os.path.join(PDF_DIR, filename)

    c = canvas.Canvas(path)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, "Pedido - Quero Batata")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Cliente: {nome}")
    c.drawString(50, 760, f"Endereço: {endereco}")
    c.drawString(50, 740, f"Telefone: {telefone}")
    c.drawString(50, 720, f"Data: {datahora}")

    y = 700
    for p in produtos:
        c.drawString(70, y, f"- {p['nome']} | R$ {p['preco']:.2f}")
        y -= 20

    c.drawString(50, y - 10, f"Taxa de entrega: R$ {taxa_entrega:.2f}")
    c.drawString(50, y - 30, f"Total: R$ {total:.2f}")
    c.save()

    return jsonify({
        "mensagem": "Pedido salvo com sucesso!",
        "pdf_url": f"/api/download/{filename}"
    })


@app.route("/api/download/<filename>")
def download(filename):
    return send_from_directory(PDF_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
