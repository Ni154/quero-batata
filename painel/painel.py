import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid

# 🔑 Supabase config
SUPABASE_URL = "https://jptsbutoikieipwnlbft.supabase.co"
SUPABASE_KEY = "sb_secret_KTTNWWrjuuuPL3CQRdHo-Q_1lcYZfFt"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Painel Quero Batata", layout="wide")

# 🔐 Login simples
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login do Painel")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        res = supabase.table("usuarios").select("*").eq("usuario", user).eq("senha", pwd).execute()
        st.write("Consulta retornou:", res.data)
        if res.data:
            st.session_state.logado = True
            st.session_state.usuario = user
            st.success("Login realizado com sucesso!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

st.sidebar.title("Quero Batata - Admin")
menu = st.sidebar.radio("Menu", ["Pedidos", "Cadastrar Produto", "Cadastrar Categoria", "Controle da Loja", "Dashboard"])

# 📅 Pedidos
if menu == "Pedidos":
    st.title("📦 Pedidos Recebidos")
    res = supabase.table("pedidos").select("*").order("criado_em", desc=True).execute()
    dados = res.data

    if not dados:
        st.info("Nenhum pedido encontrado.")
    else:
        for pedido in dados:
            with st.container(border=True):
                st.subheader(f"👤 {pedido['nome_cliente']}")
                st.write(f"📞 {pedido['telefone']} | 🏠 {pedido['endereco']} | ⏰ {pedido['criado_em']}")
                st.write(f"💰 Total: R$ {pedido['total']:.2f} | 🚚 Entrega: R$ {pedido['taxa_entrega']:.2f}")
                st.markdown("**Produtos:**")
                try:
                    for item in pedido['produtos']:
                        st.markdown(f"- {item['nome']} - R$ {item['preco']:.2f}")
                except:
                    st.error("Erro ao ler produtos do pedido.")

# 💼 Cadastro de Produto
elif menu == "Cadastrar Produto":
    st.title("🍔 Cadastrar Novo Produto")
    nome = st.text_input("Nome do Produto")
    preco = st.number_input("Preço", min_value=0.0, step=0.5)
    categoria = st.text_input("Categoria")
    imagem_file = st.file_uploader("Imagem do Produto", type=["jpg", "png", "jpeg"])
imagem_url = ""

if imagem_file:
    nome_arquivo = f"{uuid.uuid4().hex}_{imagem_file.name}"
    supabase.storage.from_('produtos').upload(nome_arquivo, imagem_file)
    imagem_url = supabase.storage.from_('produtos').get_public_url(nome_arquivo)

    if st.button("Salvar Produto"):
    if not imagem_url:
        st.error("Envie uma imagem antes de salvar.")
    else:
        supabase.table("produtos").insert({
            "nome": nome,
            "preco": preco,
            "categoria": categoria,
            "imagem_url": imagem_url,
            "disponivel": True
        }).execute()
        st.success("Produto cadastrado com sucesso!")

# 📄 Cadastro de Categoria
elif menu == "Cadastrar Categoria":
    st.title("📚 Cadastrar Nova Categoria")
    nome_cat = st.text_input("Nome da Categoria")
    if st.button("Salvar Categoria"):
        supabase.table("categorias").insert({"nome": nome_cat}).execute()
        st.success("Categoria cadastrada com sucesso!")

# ⚖️ Controle de Loja
elif menu == "Controle da Loja":
    st.title("🏠 Status da Loja")
    res = supabase.table("config").select("valor").eq("chave", "loja_aberta").single().execute()
    loja_aberta = res.data['valor'] == 'true' if res.data else False

    status = "🛡️ Loja Aberta" if loja_aberta else "❌ Loja Fechada"
    st.subheader(status)
    nova = not loja_aberta
    if st.button("Abrir Loja" if nova else "Fechar Loja"):
        valor = 'true' if nova else 'false'
        supabase.table("config").upsert({"chave": "loja_aberta", "valor": valor}).execute()
        st.success("Status atualizado!")
        st.experimental_rerun()

# 🔢 Dashboard
elif menu == "Dashboard":
    st.title("📊 Produtos Mais Vendidos")
    res = supabase.table("pedidos").select("produtos").execute()
    contagem = {}
    for pedido in res.data:
        try:
            for item in pedido['produtos']:
                nome = item['nome']
                contagem[nome] = contagem.get(nome, 0) + 1
        except:
            continue

    df = pd.DataFrame(list(contagem.items()), columns=["Produto", "Vendas"])
    df = df.sort_values("Vendas", ascending=False)
    st.bar_chart(df.set_index("Produto"))
