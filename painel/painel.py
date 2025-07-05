import streamlit as st
import requests
import json
from datetime import datetime

API_BASE_URL = "https://quero-batata-production.up.railway.app"

st.set_page_config(page_title="Painel Quero Batata", layout="wide")

# --- Login ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if user == "admin" and pwd == "admin":
            st.session_state.logado = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")
    st.stop()

# --- Menu lateral ---
menu = st.sidebar.radio("Menu", ["Pedidos", "Produtos", "Categorias", "Controle Loja", "Dashboard"])

# --- PEDIDOS ---
if menu == "Pedidos":
    st.title("📦 Pedidos")
    res = requests.get(f"{API_BASE_URL}/api/pedidos")
    if res.status_code == 200:
        pedidos = res.json()
        novos = [p for p in pedidos if p['status'] != "Finalizado"]
        finalizados = [p for p in pedidos if p['status'] == "Finalizado"]

        st.subheader("🟢 Novos Pedidos")
        for p in novos:
            with st.expander(f"{p['nome_cliente']} - R$ {p['total']}"):
                st.write(f"Telefone: {p['telefone']}")
                st.write(f"Endereço: {p['endereco']}")
                st.write(f"Status: {p['status']}")
                st.write(f"Criado em: {p['criado_em']}")
                st.write("Produtos:")
                for item in p['produtos']:
                    st.markdown(f"- {item['nome']} - R$ {item['preco']}")
                if st.button("Marcar como Finalizado", key=f"finalizar_{p['id']}"):
                    requests.put(f"{API_BASE_URL}/api/pedidos/{p['id']}", json={"status": "Finalizado"})
                    st.experimental_rerun()

        st.markdown("---")
        st.subheader("🔴 Pedidos Finalizados")
        for p in finalizados:
            st.markdown(f"**{p['nome_cliente']}** - R$ {p['total']} - {p['criado_em']}")

# --- PRODUTOS ---
elif menu == "Produtos":
    st.title("🧀 Produtos")

    cat_res = requests.get(f"{API_BASE_URL}/api/categorias")
    categorias = cat_res.json() if cat_res.status_code == 200 else []
    cat_map = {c['nome']: c['id'] for c in categorias}

    with st.form("form_produto"):
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço", step=0.5)
        categoria_nome = st.selectbox("Categoria", list(cat_map.keys()))
        imagem = st.file_uploader("Imagem", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Cadastrar")

        if submit:
            img_url = ""
            if imagem:
                files = {"file": imagem.getvalue()}
                up = requests.post(f"{API_BASE_URL}/api/upload", files=files)
                if up.status_code == 200:
                    img_url = up.json()["url"]
            payload = {
                "nome": nome,
                "preco": preco,
                "categoria_id": cat_map[categoria_nome],
                "imagem_url": img_url
            }
            r = requests.post(f"{API_BASE_URL}/api/produtos", json=payload)
            if r.status_code == 201:
                st.success("Produto criado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("Erro ao criar produto.")

    # Tabela de produtos
    res = requests.get(f"{API_BASE_URL}/api/produtos")
    produtos = res.json() if res.status_code == 200 else []
    st.subheader("📋 Produtos Cadastrados")
    for p in produtos:
        col1, col2 = st.columns([5,1])
        with col1:
            st.markdown(f"**{p['nome']}** - R$ {p['preco']} | Cat: {p['categoria_id']}")
        with col2:
            if st.button("Excluir", key=f"excluir_prod_{p['id']}"):
                requests.delete(f"{API_BASE_URL}/api/produtos/{p['id']}")
                st.experimental_rerun()

# --- CATEGORIAS ---
elif menu == "Categorias":
    st.title("📁 Categorias")
    with st.form("form_categoria"):
        nome = st.text_input("Nome da Categoria")
        submit = st.form_submit_button("Cadastrar")
        if submit:
            r = requests.post(f"{API_BASE_URL}/api/categorias", json={"nome": nome})
            if r.status_code == 201:
                st.success("Categoria criada!")
                st.experimental_rerun()
            else:
                st.error("Erro ao criar categoria")

    res = requests.get(f"{API_BASE_URL}/api/categorias")
    categorias = res.json() if res.status_code == 200 else []
    st.subheader("📋 Categorias Cadastradas")
    for c in categorias:
        col1, col2 = st.columns([5,1])
        with col1:
            st.markdown(f"**{c['nome']}** (ID: {c['id']})")
        with col2:
            if st.button("Excluir", key=f"excluir_cat_{c['id']}"):
                requests.delete(f"{API_BASE_URL}/api/categorias/{c['id']}")
                st.experimental_rerun()

# --- CONTROLE LOJA ---
elif menu == "Controle Loja":
    st.title("🏪 Controle de Loja")
    res = requests.get(f"{API_BASE_URL}/api/status")
    status = res.json().get("loja_aberta", False)
    st.write("Loja está:", "🟢 Aberta" if status else "🔴 Fechada")
    if st.button("Abrir Loja" if not status else "Fechar Loja"):
        r = requests.post(f"{API_BASE_URL}/api/status", json={"loja_aberta": not status})
        if r.status_code == 200:
            st.experimental_rerun()
        else:
            st.error("Erro ao atualizar status")

# --- DASHBOARD ---
elif menu == "Dashboard":
    st.title("📊 Dashboard")
    pedidos = requests.get(f"{API_BASE_URL}/api/pedidos").json()
    produtos = requests.get(f"{API_BASE_URL}/api/produtos").json()

    total_pedidos = len(pedidos)
    total_vendas = sum(p['total'] for p in pedidos)

    # Produto mais vendido
    contagem = {}
    for p in pedidos:
        for item in p['produtos']:
            nome = item['nome']
            contagem[nome] = contagem.get(nome, 0) + 1
    produto_top = max(contagem, key=contagem.get) if contagem else "-"

    # Cliente que mais compra
    clientes = {}
    for p in pedidos:
        nome = p['nome_cliente']
        clientes[nome] = clientes.get(nome, 0) + 1
    cliente_top = max(clientes, key=clientes.get) if clientes else "-"

    st.metric("Total de Pedidos", total_pedidos)
    st.metric("Total em Vendas", f"R$ {total_vendas:.2f}")
    st.metric("Produto Mais Vendido", produto_top)
    st.metric("Cliente Mais Fiel", cliente_top)
