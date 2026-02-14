import streamlit as st
import pandas as pd
from services.database import SupabaseService

def exibir_adm():
    st.header("⚙️ Painel de Administração")
    
    # Proteção de acesso
    senha_digitada = st.text_input("Senha de acesso:", type="password")
    if senha_digitada != st.secrets.get("SENHA_ADM", "admin123"):
        st.stop() # Interrompe a renderização aqui

    db = SupabaseService()
    res = db.buscar_movimentacoes_adm()

    if res.data:
        df = pd.DataFrame(res.data)
        st.subheader("🗑️ Histórico Recente (Para Correção)")
        
        for _, row in df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Item:** {row['item_name']} | **Status:** {row['status']}")
                    st.caption(f"{row['from_person']} ➜ {row['to_person']} em {row['occurred_at'][:16]}")
                with col2:
                    if st.button("🗑️ Apagar", key=f"del_{row['id']}"):
                        db.deletar_movimentacao(row['id'])
                        st.toast("Registro apagado!", icon="🔥")
                        st.rerun()
    else:
        st.info("Nenhum registro encontrado.")