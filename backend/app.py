from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://jptsbutoikieipwnlbft.supabase.co"
SUPABASE_KEY = "sb_secret_KTTNWWrjuuuPL3CQRdHo-Q_1lcYZfFt"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Produtos ---
@app.route('/api/produtos', methods=['GET', 'POST'])
def produtos():
    if request.method == 'GET':
        res = supabase.table("produtos").select("*").execute()
        return jsonify(res.data)
    if request.method == 'POST':
        data = request.json
        novo = {
            "nome": data.get("nome"),
            "preco": data.get("preco"),
            "categoria_id": data.get("categoria_id"),
            "imagem_url": data.get("imagem_url", ""),
            "disponivel": True
        }
        supabase.table("produtos").insert(novo).execute()
        return jsonify({"message": "Produto criado"}), 201

@app.route('/api/produtos/<int:id>', methods=['PUT', 'DELETE'])
def produto_update(id):
    if request.method == 'PUT':
        data = request.json
        supabase.table("produtos").update(data).eq("id", id).execute()
        return jsonify({"message": "Produto atualizado"})
    if request.method == 'DELETE':
        supabase.table("produtos").delete().eq("id", id).execute()
        return jsonify({"message": "Produto excluído"})

# --- Categorias ---
@app.route('/api/categorias', methods=['GET', 'POST'])
def categorias():
    if request.method == 'GET':
        res = supabase.table("categorias").select("*").execute()
        return jsonify(res.data)
    if request.method == 'POST':
        data = request.json
        supabase.table("categorias").insert({"nome": data.get("nome")}).execute()
        return jsonify({"message": "Categoria criada"}), 201

@app.route('/api/categorias/<int:id>', methods=['PUT', 'DELETE'])
def categoria_update(id):
    if request.method == 'PUT':
        data = request.json
        supabase.table("categorias").update(data).eq("id", id).execute()
        return jsonify({"message": "Categoria atualizada"})
    if request.method == 'DELETE':
        supabase.table("categorias").delete().eq("id", id).execute()
        return jsonify({"message": "Categoria excluída"})

# --- Pedidos ---
@app.route('/api/pedido', methods=['POST'])
def novo_pedido():
    # Verifica status da loja antes de aceitar pedido
    status_res = supabase.table("config").select("*").eq("chave", "loja_aberta").single().execute()
    loja_aberta = status_res.data['valor'] == 'true' if status_res.data else False

    if not loja_aberta:
        return jsonify({"error": "A loja está fechada no momento. Não é possível fazer pedidos."}), 403

    data = request.json
    pedido = {
        "nome_cliente": data.get("nome"),
        "telefone": data.get("telefone"),
        "endereco": data.get("endereco"),
        "produtos": data.get("produtos"),
        "taxa_entrega": data.get("taxa_entrega"),
        "total": data.get("total"),
        "status": "Recebido",
        "criado_em": datetime.now().isoformat()
    }
    supabase.table("pedidos").insert(pedido).execute()
    return jsonify({"message": "Pedido recebido"})

# --- Upload de imagem para produtos ---
@app.route('/api/upload', methods=['POST'])
def upload_imagem():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não enviado"}), 400
    file = request.files['file']
    nome_arquivo = f"produtos/{uuid.uuid4().hex}_{file.filename}"
    supabase.storage.from_('produtos').upload(nome_arquivo, file)
    url_publica = supabase.storage.from_('produtos').get_public_url(nome_arquivo)
    return jsonify({"url": url_publica})

# --- Status da loja ---
@app.route('/api/status', methods=['GET', 'POST'])
def status_loja():
    if request.method == 'GET':
        res = supabase.table("config").select("*").eq("chave", "loja_aberta").single().execute()
        return jsonify({"loja_aberta": res.data['valor'] == 'true' if res.data else False})
    if request.method == 'POST':
        data = request.json
        supabase.table("config").upsert({"chave": "loja_aberta", "valor": "true" if data.get("loja_aberta") else "false"}).execute()
        return jsonify({"message": "Status atualizado"})

if __name__ == '__main__':
    app.run(debug=True)
