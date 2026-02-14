import streamlit as st
import pandas as pd
from services.database import SupabaseService

def exibir_historico():
    st.header("📜 Histórico de Movimentações")
    db = SupabaseService()
    
    # Busca opções para o Selectbox
    try:
        lista_pessoas, lista_itens, _ = db.get_opcoes_autocomplete()
    except:
        lista_pessoas, lista_itens = [], []

    res = db.buscar_todas_movimentacoes()
    if not res.data:
        st.info("Nenhuma movimentação registrada ainda.")
        return

    df = pd.DataFrame(res.data)
    df['occurred_at'] = pd.to_datetime(df['occurred_at'], utc=True)

    # --- FILTROS COM SELECTBOX (USABILIDADE UPGRADE) ---
    col1, col2 = st.columns(2)
    with col1:
        # Agora o usuário escolhe da lista em vez de digitar
        filtro_item = st.selectbox("🔍 Filtrar por Item:", options=["TODOS"] + lista_itens)
    with col2:
        filtro_pessoa = st.selectbox("👤 Filtrar por Pessoa:", options=["TODOS"] + lista_pessoas)

    # Aplicando os filtros no DataFrame
    if filtro_item != "TODOS":
        df = df[df['item_name'] == filtro_item]
    if filtro_pessoa != "TODOS":
        # Filtra se a pessoa foi a origem OU o destino
        df = df[(df['from_person'] == filtro_pessoa) | (df['to_person'] == filtro_pessoa)]

    # Exibição dos dados
    st.write("---")
    for _, row in df.sort_values('occurred_at', ascending=False).iterrows():
        status_color = "blue" if row['status'] == 'DEVOLVIDO' else "red" if row['status'] == 'EMPRESTADO' else "green"
        data = row['occurred_at'].strftime('%d/%m %H:%M')
        
        st.markdown(f"""
            <div style="font-size: 0.9em; margin-bottom: 8px; padding: 5px; border-bottom: 1px solid #1c2128;">
                <span style="color: #768390;">[{data}]</span> 
                <b>{row['item_name']}</b> <small>({row['label']})</small>: 
                {row['from_person']} ➔ {row['to_person']} 
                <span style="background-color: {status_color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.7em; margin-left: 5px;">
                    {row['status']}
                </span>
            </div>
        """, unsafe_allow_html=True)