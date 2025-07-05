# backend/painel.py
import streamlit as st
import requests
import json

API_BASE_URL = "https://quero-batata-production.up.railway.app"

st.set_page_config(page_title="Painel Quero Batata", layout="wide")

# Login simples (exemplo sem segurança avançada)
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        # Aqui você pode fazer uma chamada para backend verificar login
        if user == "admin" and pwd == "admin":  # Troque por autenticação real
            st.session_state.logado = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")
    st.stop()

menu = st.sidebar.radio("Menu", ["Pedidos", "Produtos", "Categorias", "Controle Loja", "Dashboard"])

# --- Pedidos ---
if menu == "Pedidos":
    st.title("Pedidos")
    res = requests.get(f"{API_BASE_URL}/api/pedidos")  # Você pode precisar criar essa rota GET no backend
    pedidos = res.json() if res.status_code == 200 else []
    for p in pedidos:
        st.write(f"Cliente: {p['nome_cliente']} | Telefone: {p['telefone']}")
        st.write(f"Endereço: {p['endereco']}")
        st.write(f"Total: R$ {p['total']}")
        st.write(f"Status: {p['status']}")
        st.write("---")

# --- Produtos ---
elif menu == "Produtos":
    st.title("Produtos")
    res = requests.get(f"{API_BASE_URL}/api/produtos")
    produtos = res.json() if res.status_code == 200 else []
    nomes = [p['nome'] for p in produtos]
    with st.form("form_produtos"):
        nome = st.text_input("Nome")
        preco = st.number_input("Preço", min_value=0.0, step=0.5)
        categoria_id = st.number_input("ID Categoria", min_value=1)
        submitted = st.form_submit_button("Adicionar Produto")
        if submitted:
            novo = {"nome": nome, "preco": preco, "categoria_id": categoria_id}
            r = requests.post(f"{API_BASE_URL}/api/produtos", json=novo)
            if r.status_code == 201:
                st.success("Produto criado!")
            else:
                st.error("Erro ao criar produto.")

    for p in produtos:
        st.write(f"{p['id']} - {p['nome']} - R$ {p['preco']} (Cat: {p['categoria_id']})")

# --- Categorias ---
elif menu == "Categorias":
    st.title("Categorias")
    res = requests.get(f"{API_BASE_URL}/api/categorias")
    categorias = res.json() if res.status_code == 200 else []
    with st.form("form_categorias"):
        nome = st.text_input("Nome Categoria")
        submitted = st.form_submit_button("Adicionar Categoria")
        if submitted:
            r = requests.post(f"{API_BASE_URL}/api/categorias", json={"nome": nome})
            if r.status_code == 201:
                st.success("Categoria criada!")
            else:
                st.error("Erro ao criar categoria.")

    for c in categorias:
        st.write(f"{c['id']} - {c['nome']}")

# --- Controle Loja ---
elif menu == "Controle Loja":
    st.title("Controle da Loja")
    res = requests.get(f"{API_BASE_URL}/api/status")
    aberto = res.json().get("loja_aberta", False)
    st.write(f"Loja está {'Aberta' if aberto else 'Fechada'}")

    if st.button("Abrir Loja" if not aberto else "Fechar Loja"):
        r = requests.post(f"{API_BASE_URL}/api/status", json={"loja_aberta": not aberto})
        if r.status_code == 200:
            st.experimental_rerun()
        else:
            st.error("Erro ao alterar status")

# --- Dashboard ---
elif menu == "Dashboard":
    st.title("Dashboard")
    # Aqui você pode montar gráficos baseados em pedidos, produtos, etc.
    st.write("Dashboard a implementar...")
