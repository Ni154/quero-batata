import streamlit as st
import requests

API_BASE_URL = "https://quero-batata-production.up.railway.app"

st.title("Painel Administrativo Quero Batata")

# --- Categorias ---

def listar_categorias():
    r = requests.get(f"{API_BASE_URL}/api/categorias")
    if r.status_code == 200:
        return r.json()
    else:
        st.error("Erro ao carregar categorias")
        return []

def criar_categoria(nome):
    r = requests.post(f"{API_BASE_URL}/api/categorias", json={"nome": nome})
    if r.status_code == 201:
        st.success("Categoria criada!")
    else:
        st.error(f"Erro: {r.json().get('error')}")

def editar_categoria(id, nome):
    r = requests.put(f"{API_BASE_URL}/api/categorias/{id}", json={"nome": nome})
    if r.status_code == 200:
        st.success("Categoria atualizada!")
    else:
        st.error(f"Erro: {r.json().get('error')}")

def excluir_categoria(id):
    r = requests.delete(f"{API_BASE_URL}/api/categorias/{id}")
    if r.status_code == 200:
        st.success("Categoria excluída!")
    else:
        st.error(f"Erro: {r.json().get('error')}")

# --- Produtos ---

def listar_produtos():
    r = requests.get(f"{API_BASE_URL}/api/produtos")
    if r.status_code == 200:
        return r.json()
    else:
        st.error("Erro ao carregar produtos")
        return []

def criar_produto(nome, preco, categoria_id):
    r = requests.post(f"{API_BASE_URL}/api/produtos", json={
        "nome": nome,
        "preco": preco,
        "categoria_id": categoria_id
    })
    if r.status_code == 201:
        st.success("Produto criado!")
    else:
        st.error(f"Erro: {r.json().get('error')}")

def editar_produto(id, nome, preco, categoria_id):
    r = requests.put(f"{API_BASE_URL}/api/produtos/{id}", json={
        "nome": nome,
        "preco": preco,
        "categoria_id": categoria_id
    })
    if r.status_code == 200:
        st.success("Produto atualizado!")
    else:
        st.error(f"Erro: {r.json().get('error')}")

def excluir_produto(id):
    r = requests.delete(f"{API_BASE_URL}/api/produtos/{id}")
    if r.status_code == 200:
        st.success("Produto excluído!")
    else:
        st.error(f"Erro: {r.json().get('error')}")

# --- Interface simples para testar ---

st.header("Categorias")

categorias = listar_categorias()
for cat in categorias:
    st.write(f"{cat['id']}: {cat['nome']}")

with st.form("form_categorias"):
    nome_cat = st.text_input("Nova categoria")
    submitted = st.form_submit_button("Criar categoria")
    if submitted and nome_cat:
        criar_categoria(nome_cat)

st.header("Produtos")

produtos = listar_produtos()
for prod in produtos:
    st.write(f"{prod['id']}: {prod['nome']} - R$ {prod['preco']} (Categoria {prod['categoria_id']})")

with st.form("form_produtos"):
    nome_prod = st.text_input("Nome do produto")
    preco_prod = st.number_input("Preço", min_value=0.0, step=0.5)
    cat_ids = [c['id'] for c in categorias]
    cat_id_selecionada = st.selectbox("Categoria", cat_ids)
    submitted_prod = st.form_submit_button("Criar produto")
    if submitted_prod and nome_prod:
        criar_produto(nome_prod, preco_prod, cat_id_selecionada)
