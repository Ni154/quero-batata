import streamlit as st
from supabase import create_client
import pandas as pd
import json
from datetime import datetime

# 🔑 Supabase config (substitua com os seus dados)
SUPABASE_URL = "https://jptsbutoikieipwnlbft.supabase.co"
SUPABASE_KEY = "sb_secret_KTTNWWrjuuuPL3CQRdHo-Q_1lcYZfFt"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Painel Quero Batata", layout="wide")

st.title("📦 Painel de Pedidos - Quero Batata")
st.markdown("Veja aqui os pedidos mais recentes. Para atualizar, recarregue a página.")

# Buscar pedidos
res = supabase.table("pedidos").select("*").order("criado_em", desc=True).execute()
dados = res.data

if not dados:
    st.info("Nenhum pedido registrado ainda.")
else:
    for pedido in dados:
        with st.container(border=True):
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

