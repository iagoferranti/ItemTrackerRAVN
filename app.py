import streamlit as st
import pandas as pd
from views.registrar import exibir_registrar
from views.inventario import exibir_inventario
from views.historico import exibir_historico
from views.adm import exibir_adm
from services.database import SupabaseService

# Configuração da página (deve ser a primeira coisa do script)
st.set_page_config(page_title="RAVN Item Tracker", layout="wide", initial_sidebar_state="expanded")

# CSS para customização básica (puxando pro Dark Mode e estilo Rag)
st.markdown("""
    <style>
    /* Fundo dos campos de input e selectbox mais destacados */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1c2128 !important;
        border: 1px solid #444c56 !important;
        color: #adbac7 !important;
    }
    /* Destaque quando o campo está focado */
    .stTextInput>div>div>input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 1px #58a6ff !important;
    }
    /* Estilo para os cards de info de seleção */
    .stAlert {
        padding: 5px 10px !important;
        background-color: #22272e !important;
        border: 1px solid #444c56 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="RAVN Tracker", layout="wide")
    db = SupabaseService()

    # --- SIDEBAR COM MÉTRICAS EM TEMPO REAL ---
    with st.sidebar:
        st.title("🦅 RAVN Tracker")
        
        try:
            res = db.buscar_todas_movimentacoes()
            if res.data:
                df = pd.DataFrame(res.data)
                # Forçamos a conversão de data para garantir o cálculo correto
                df['occurred_at'] = pd.to_datetime(df['occurred_at'], errors='coerce', utc=True)
                
                # Pegamos apenas o estado mais atual de cada item
                df_atual = df.loc[df.groupby(['item_name', 'label'])['occurred_at'].idxmax()]
                
                total = len(df_atual)
                no_cla = len(df_atual[df_atual['status'] == 'CLÃ'])
                emprestados = total - no_cla

                st.divider()
                st.metric("📦 Itens Totais", total)
                st.metric("🏛️ No Armazém", no_cla)
                st.metric("🔴 Emprestados", emprestados)
                st.divider()
        except Exception:
            st.sidebar.warning("📊 Estatísticas indisponíveis")

        menu = st.radio("Navegação:", ["Inventário", "Registrar Repasse", "Histórico Geral", "Admin"])

    # --- RENDERIZAÇÃO DAS TELAS ---
    if menu == "Inventário":
        exibir_inventario()
    elif menu == "Registrar Repasse":
        exibir_registrar()
    elif menu == "Histórico Geral":
        exibir_historico()
    elif menu == "Admin":
        exibir_adm()

if __name__ == "__main__":
    main()