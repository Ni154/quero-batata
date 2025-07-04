from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
from supabase import create_client, Client
from reportlab.pdfgen import canvas
import os
import uuid

# 🔑 Supabase config (substitua pelos seus dados)
SUPABASE_URL = "https://jptsbutoikieipwnlbft.supabase.co"
SUPABASE_KEY = "sb_secret_KTTNWWrjuuuPL3CQRdHo-Q_1lcYZfFt"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📁 Pasta onde os PDFs serão salvos
PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

@app.route("/api/pedido", methods=["POST"])
def pedido():
    data = request.json
    nome = data.get("nome")
    endereco = data.get("endereco")
    telefone = data.get("telefone")
    produtos = data.get("produtos")
    taxa_entrega = data.get("taxa_entrega", 5.0)
    total = data.get("total")

    datahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 👉 Salvar no Supabase
    supabase.table("pedidos").insert({
        "nome": nome,
        "telefone": telefone,
        "endereco": endereco,
        "produtos": str(produtos),
        "taxa_entrega": taxa_entrega,
        "total": total,
        "data": datahora
    }).execute()

    # 📄 Gerar PDF
    filename = f"{uuid.uuid4().hex[:8]}_{nome.replace(' ', '_')}.pdf"
    path = os.path.join(PDF_DIR, filename)
    c = canvas.Canvas(path)
    c.drawString(50, 800, "Pedido - Quero Batata")
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

