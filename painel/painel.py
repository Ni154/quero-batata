from flask import Flask, request, jsonify
from supabase import create_client
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import uuid
import os
from datetime import datetime

app = Flask(__name__)

# Configurações Supabase (substitua pelos seus dados)
SUPABASE_URL = "https://jptsbutoikieipwnlbft.supabase.co"
SUPABASE_KEY = "sb_secret_KTTNWWrjuuuPL3CQRdHo-Q_1lcYZfFt"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

@app.route("/api/pedido", methods=["POST"])
def criar_pedido():
    data = request.get_json()

    # Valida campos obrigatórios
    for campo in ["nome", "telefone", "endereco", "produtos", "taxa_entrega", "total"]:
        if campo not in data:
            return jsonify({"error": f"Campo '{campo}' obrigatório"}), 400

    nome = data["nome"]
    telefone = data["telefone"]
    endereco = data["endereco"]
    produtos = data["produtos"]  # Espera lista de dicts {nome, preco, qtd}
    taxa_entrega = data["taxa_entrega"]
    total = data["total"]

    # Criar registro no Supabase
    pedido = {
        "nome_cliente": nome,
        "telefone": telefone,
        "endereco": endereco,
        "produtos": str(produtos),  # Pode salvar como JSON string ou ajustar tipo na tabela
        "taxa_entrega": taxa_entrega,
        "total": total,
        "criado_em": datetime.utcnow().isoformat()
    }
    supabase.table("pedidos").insert(pedido).execute()

    # Gerar PDF do pedido
    pdf_id = uuid.uuid4().hex
    pdf_path = os.path.join(PDF_FOLDER, f"pedido_{pdf_id}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Pedido Quero Batata")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Cliente: {nome}")
    c.drawString(50, 710, f"Telefone: {telefone}")
    c.drawString(50, 690, f"Endereço: {endereco}")
    c.drawString(50, 670, "Produtos:")

    y = 650
    for item in produtos:
        linha = f"{item['qtd']}x {item['nome']} - R$ {item['preco']:.2f}"
        c.drawString(60, y, linha)
        y -= 20

    c.drawString(50, y - 10, f"Taxa de entrega: R$ {taxa_entrega:.2f}")
    c.drawString(50, y - 30, f"Total: R$ {total:.2f}")

    c.save()

    # Aqui pode ser feito upload do PDF para storage e gerar URL público
    # Para simplificar, retornamos o caminho local do PDF (adaptar conforme deploy)
    pdf_url = f"/pdfs/pedido_{pdf_id}.pdf"

    return jsonify({"message": "Pedido criado com sucesso", "pdf_url": pdf_url}), 201

if __name__ == "__main__":
    app.run(debug=True)
