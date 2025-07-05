import streamlit as st
import requests
from PIL import Image
import io

API_BASE_URL = "https://quero-batata-production.up.railway.app"

st.set_page_config(page_title="Painel Quero Batata", layout="wide")

# Login simples
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

menu = st.sidebar.radio("Menu", ["Pedidos", "Produtos", "Categorias", "Controle Loja", "Dashboard"])

# --- PEDIDOS ---
if menu == "Pedidos":
    st.title("Pedidos")
    res = requests.get(f"{API_BASE_URL}/api/pedidos")
    pedidos = res.json() if res.status_code == 200 else []

    novos = [p for p in pedidos if p.get("status") != "Finalizado"]
    finalizados = [p for p in pedidos if p.get("status") == "Finalizado"]

    st.subheader("🆕 Novos Pedidos")
    for p in novos:
        with st.expander(f"Pedido de {p.get('nome_cliente')} - R$ {p.get('total')}"):
            st.write(f"📞 {p.get('telefone')}")
            st.write(f"📍 {p.get('endereco')}")
            st.write(f"🛍️ Produtos: {p.get('produtos')}")
            st.write(f"💰 Total: R$ {p.get('total')} + Taxa: R$ {p.get('taxa_entrega')}")
            st.write(f"🕒 Criado em: {p.get('criado_em')}")
            if st.button("Marcar como Finalizado", key=f"finalizar_{p.get('id')}"):
                requests.put(f"{API_BASE_URL}/api/pedidos/{p.get('id')}", json={"status": "Finalizado"})
                st.experimental_rerun()

    st.divider()
    st.subheader("✅ Pedidos Finalizados")
    for p in finalizados:
        st.write(f"{p.get('nome_cliente')} - R$ {p.get('total')}")

# --- PRODUTOS ---
elif menu == "Produtos":
    st.title("Produtos")
    prod_res = requests.get(f"{API_BASE_URL}/api/produtos")
    cat_res = requests.get(f"{API_BASE_URL}/api/categorias")
    produtos = prod_res.json() if prod_res.status_code == 200 else []
    categorias = cat_res.json() if cat_res.status_code == 200 else []

    cat_dict = {c["nome"]: c["id"] for c in categorias}

    with st.form("form_produto"):
        nome = st.text_input("Nome")
        preco = st.number_input("Preço", min_value=0.0, step=0.5)
        categoria_nome = st.selectbox("Categoria", list(cat_dict.keys()))
        imagem = st.file_uploader("Imagem do produto", type=["png", "jpg", "jpeg"])
        submit = st.form_submit_button("Adicionar Produto")

        if submit:
            categoria_id = cat_dict[categoria_nome]
            imagem_url = ""

            if imagem:
                img = Image.open(imagem)
                img = img.resize((300, 300))
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                files = {"file": ("imagem.png", buf, "image/png")}
                upload = requests.post(f"{API_BASE_URL}/api/upload", files=files)
                if upload.status_code == 200:
                    imagem_url = upload.json().get("url", "")

            novo = {
                "nome": nome,
                "preco": preco,
                "categoria_id": categoria_id,
                "imagem_url": imagem_url
            }
            r = requests.post(f"{API_BASE_URL}/api/produtos", json=novo)
            if r.status_code == 201:
                st.success("Produto criado!")
                st.rerun()
            else:
                st.error("Erro ao criar produto.")

    st.subheader("📦 Produtos Cadastrados")
    for p in produtos:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{p.get('nome')}** - R$ {p.get('preco')} | Categoria ID: {p.get('categoria_id')}")
        with col2:
            if st.button("Excluir", key=f"delprod_{p.get('id')}"):
                requests.delete(f"{API_BASE_URL}/api/produtos/{p.get('id')}")
                st.rerun()

# --- CATEGORIAS ---
elif menu == "Categorias":
    st.title("Categorias")
    res = requests.get(f"{API_BASE_URL}/api/categorias")
    categorias = res.json() if res.status_code == 200 else []

    with st.form("form_cat"):
        nome = st.text_input("Nome da Categoria")
        submit = st.form_submit_button("Adicionar Categoria")
        if submit:
            r = requests.post(f"{API_BASE_URL}/api/categorias", json={"nome": nome})
            if r.status_code == 201:
                st.success("Categoria criada!")
                st.rerun()
            else:
                st.error("Erro ao criar categoria.")

    st.subheader("📂 Categorias Cadastradas")
    for c in categorias:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{c.get('id')} - {c.get('nome')}")
        with col2:
            if st.button("Excluir", key=f"delcat_{c.get('id')}"):
                requests.delete(f"{API_BASE_URL}/api/categorias/{c.get('id')}")
                st.rerun()

# --- CONTROLE DA LOJA ---
elif menu == "Controle Loja":
    st.title("🛍️ Status da Loja")
    res = requests.get(f"{API_BASE_URL}/api/status")
    aberto = res.json().get("loja_aberta", False)
    st.write(f"Loja está: **{'Aberta' if aberto else 'Fechada'}**")

    if st.button("Abrir Loja" if not aberto else "Fechar Loja"):
        r = requests.post(f"{API_BASE_URL}/api/status", json={"loja_aberta": not aberto})
        if r.status_code == 200:
            st.success("Status alterado")
            st.rerun()
        else:
            st.error("Erro ao alterar status")

# --- DASHBOARD ---
elif menu == "Dashboard":
    st.title("📊 Dashboard")
    st.write("Em breve: gráficos de produtos mais vendidos, clientes frequentes e filtro por período.")
