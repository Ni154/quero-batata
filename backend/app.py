from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client
from reportlab.pdfgen import canvas
import os
import uuid
import jwt
import datetime

# 🔧 Configurações
SUPABASE_URL = "https://jptsbutoikieipwnlbft.supabase.co"
SUPABASE_KEY = "sb_secret_KTTNWWrjuuuPL3CQRdHo-Q_1lcYZfFt"
JWT_SECRET = "chave_super_secreta"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app)

PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# 🔐 Login com Supabase e JWT
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

# 📦 Pedido com PDF
@app.route("/api/pedido", methods=["POST"])
def pedido():
    data = request.json
    nome = data.get("nome")
    endereco = data.get("endereco")
    telefone = data.get("telefone")
    produtos = data.get("produtos")
    taxa_entrega = data.get("taxa_entrega", 5.0)
    total = data.get("total")
    criado_em = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    supabase.table("pedidos").insert({
        "nome_cliente": nome,
        "telefone": telefone,
        "endereco": endereco,
        "produtos": produtos,
        "taxa_entrega": taxa_entrega,
        "total": total,
        "criado_em": criado_em
    }).execute()

    # 🧾 PDF
    filename = f"{uuid.uuid4().hex[:8]}_{nome.replace(' ', '_')}.pdf"
    path = os.path.join(PDF_DIR, filename)
    c = canvas.Canvas(path)
    c.drawString(50, 800, "📄 Pedido - Quero Batata")
    c.drawString(50, 780, f"Cliente: {nome}")
    c.drawString(50, 760, f"Endereço: {endereco}")
    c.drawString(50, 740, f"Telefone: {telefone}")
    y = 720
    for p in produtos:
        c.drawString(60, y, f"- {p['nome']} R$ {p['preco']:.2f}")
        y -= 20
    c.drawString(50, y, f"Entrega: R$ {taxa_entrega:.2f}")
    c.drawString(50, y - 20, f"Total: R$ {total:.2f}")
    c.save()

    return jsonify({
        "mensagem": "Pedido enviado com sucesso!",
        "pdf_url": f"/api/download/{filename}"
    })

@app.route("/api/download/<filename>")
def download(filename):
    return send_from_directory(PDF_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
