import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://jptsbutoikieipwnlbft.supabase.co"
SUPABASE_KEY = "sb_secret_KTTNWWrjuuuPL3CQRdHo-Q_1lcYZfFt"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Teste de Login")

user = st.text_input("Usuário")
pwd = st.text_input("Senha", type="password")

if st.button("Entrar"):
    try:
        res = supabase.table("usuarios").select("*").eq("usuario", user).eq("senha", pwd).execute()
        st.write("Resposta do Supabase:", res.data)
        if res.data:
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha incorretos.")
    except Exception as e:
        st.error(f"Erro na consulta: {e}")
