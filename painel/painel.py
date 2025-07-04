import streamlit as st
from supabase import create_client
from datetime import datetime

# Config Supabase
SUPABASE_URL = "https://jptsbutoikieipwnlbft.supabase.co"
SUPABASE_KEY = "sb_secret_KTTNWWrjuuuPL3CQRdHo-Q_1lcYZfFt"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Usuários autorizados para login (alterar conforme quiser)
USUARIOS = {
    "admin": "senha123"
}

# ----- LOGIN -----
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login - Painel Quero Batata")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state.logado = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# ------ PAINEL ------
st.set_page_config(page_title="Painel Quero Batata", layout="wide")
st.title("📦 Painel Administrativo - Quero Batata")

menu = st.sidebar.selectbox("Menu", ["Pedidos", "Produtos", "Categorias", "Loja", "Dashboard"])

# ------- ABRIR/FECHAR LOJA --------
def get_loja_status():
    res = supabase.table("config").select("valor").eq("chave", "loja_aberta").single().execute()
    if res.data:
        return res.data["valor"] == "true"
    return False

def set_loja_status(aberta: bool):
    existe = supabase.table("config").select("chave").eq("chave", "loja_aberta").execute()
    if existe.data:
        supabase.table("config").update({"valor": "true" if aberta else "false"}).eq("chave", "loja_aberta").execute()
    else:
        supabase.table("config").insert({"chave": "loja_aberta", "valor": "true" if aberta else "false"}).execute()

# ------- MENU: LOJA --------
if menu == "Loja":
    st.header("🟢 Abrir / 🔴 Fechar Loja")
    aberta = get_loja_status()
    st.write(f"Status atual da loja: {'Aberta' if aberta else 'Fechada'}")
    if aberta:
        if st.button("Fechar Loja"):
            set_loja_status(False)
            st.success("Loja fechada!")
            st.experimental_rerun()
    else:
        if st.button("Abrir Loja"):
            set_loja_status(True)
            st.success("Loja aberta!")
            st.experimental_rerun()

# ------- MENU: CATEGORIAS --------
if menu == "Categorias":
    st.header("📁 Gerenciar Categorias")

    with st.form("form_categoria"):
        nova_categoria = st.text_input("Nova categoria")
        enviar = st.form_submit_button("Adicionar Categoria")
        if enviar:
            if not nova_categoria:
                st.warning("Digite o nome da categoria")
            else:
                # Verifica se já existe
                cat_existe = supabase.table("categorias").select("*").eq("nome", nova_categoria).execute()
                if cat_existe.data:
                    st.warning("Categoria já existe")
                else:
                    supabase.table("categorias").insert({"nome": nova_categoria}).execute()
                    st.success(f"Categoria '{nova_categoria}' adicionada!")
                    st.experimental_rerun()

    # Listar categorias
    categorias = supabase.table("categorias").select("*").execute()
    if categorias.data:
        st.subheader("Categorias cadastradas")
        for cat in categorias.data:
            st.write(f"- {cat['nome']}")

# ------- MENU: PRODUTOS --------
if menu == "Produtos":
    st.header("🍟 Gerenciar Produtos")

    categorias = supabase.table("categorias").select("*").execute()
    cat_list = [c["nome"] for c in categorias.data] if categorias.data else []

    with st.form("form_produto"):
        nome = st.text_input("Nome do produto")
        preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
        img_url = st.text_input("URL da imagem")
        categoria = st.selectbox("Categoria", cat_list)
        enviar = st.form_submit_button("Adicionar Produto")

        if enviar:
            if not nome or preco <= 0 or not categoria:
                st.warning("Preencha nome, preço válido e categoria")
            else:
                supabase.table("produtos").insert({
                    "nome": nome,
                    "preco": preco,
                    "imagem": img_url,
                    "categoria": categoria
                }).execute()
                st.success(f"Produto '{nome}' adicionado!")
                st.experimental_rerun()

    # Listar produtos
    produtos = supabase.table("produtos").select("*").execute()
    if produtos.data:
        st.subheader("Produtos cadastrados")
        for p in produtos.data:
            st.write(f"- {p['nome']} (R$ {p['preco']:.2f}) — Categoria: {p['categoria']}")

# ------- MENU: PEDIDOS --------
if menu == "Pedidos":
    st.header("📋 Pedidos Recentes")

    res = supabase.table("pedidos").select("*").order("criado_em", desc=True).execute()
    dados = res.data

    if not dados:
        st.info("Nenhum pedido registrado ainda.")
    else:
        for pedido in dados:
            with st.container():
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader(f"👤 {pedido['nome']}")
                    st.write(f"📞 {pedido['telefone']}")
                    st.write(f"📍 {pedido['endereco']}")
                    st.write(f"🕒 {pedido['data']}")
                    st.write(f"💰 Total: R$ {pedido['total']:.2f}")
                    st.write(f"🚚 Taxa de entrega: R$ {pedido['taxa_entrega']:.2f}")

                with col2:
                    st.subheader("🧀 Produtos:")
                    try:
                        itens = eval(pedido["produtos"])
                        for item in itens:
                            st.markdown(f"- {item['nome']} - R$ {item['preco']:.2f}")
                    except:
                        st.error("Erro ao exibir produtos.")

        st.success(f"Total de pedidos encontrados: {len(dados)}")

# ------- MENU: DASHBOARD --------
if menu == "Dashboard":
    st.header("📊 Dashboard")

    pedidos = supabase.table("pedidos").select("*").execute()
    if not pedidos.data:
        st.info("Nenhum pedido para análise.")
    else:
        # Contar vendas por produto
        contador = {}
        for p in pedidos.data:
            try:
                produtos_pedido = eval(p["produtos"])
                for item in produtos_pedido:
                    nome = item["nome"]
                    qtd = item.get("qtd", 1)
                    contador[nome] = contador.get(nome, 0) + qtd
            except:
                continue

        if not contador:
            st.info("Nenhuma venda registrada.")
        else:
            st.subheader("Produtos mais vendidos:")
            produtos_ordenados = sorted(contador.items(), key=lambda x: x[1], reverse=True)
            for nome, qtd in produtos_ordenados:
                st.write(f"- {nome}: {qtd} unidades")
