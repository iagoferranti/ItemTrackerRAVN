import streamlit as st
import pandas as pd
from services.database import SupabaseService

def exibir_historico():
    st.header("📜 Histórico de Movimentações")
    db = SupabaseService()
    res = db.buscar_todas_movimentacoes()

    if not res.data:
        st.info("Nenhum dado encontrado.")
        return

    df = pd.DataFrame(res.data)
    df['occurred_at'] = pd.to_datetime(df['occurred_at'], errors='coerce', utc=True)
    df = df.sort_values(by='occurred_at', ascending=False)

    # Filtros Simplificados
    col1, col2 = st.columns(2)
    with col1:
        f_item = st.text_input("🔍 Buscar Item:").upper()
    with col2:
        f_pessoa = st.text_input("🔍 Buscar Pessoa:").upper()

    if f_item: df = df[df['item_name'].str.contains(f_item)]
    if f_pessoa: df = df[(df['from_person'].str.contains(f_pessoa)) | (df['to_person'].str.contains(f_pessoa))]

    st.write("---")

    for _, row in df.iterrows():
        # Lógica de cor baseada no Status
        color = "#da3633" if row['status'] == 'EMPRESTADO' else "#238636" if row['status'] == 'CLÃ' else "#1f6feb"
        data_f = row['occurred_at'].strftime('%d/%m %H:%M')
        
        st.markdown(f"""
            <div style="border-bottom: 1px solid #30363d; padding: 5px 0; font-size: 0.9em;">
                <span style="color: #8b949e;">[{data_f}]</span> 
                <b style="color: #adbac7;">{row['item_name']}</b> 
                <span style="color: #768390;">({row['label']})</span>: 
                {row['from_person']} ➔ {row['to_person']} 
                <span style="background-color: {color}; color: white; padding: 1px 6px; border-radius: 10px; font-size: 0.75em; margin-left: 5px;">
                    {row['status']}
                </span>
            </div>
        """, unsafe_allow_html=True)