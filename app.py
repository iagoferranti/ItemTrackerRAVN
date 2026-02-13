import streamlit as st
from views.registrar import exibir_registrar
from views.inventario import exibir_inventario
from views.historico import exibir_historico

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
    st.sidebar.title("⚔️ RAVN Tracker")
    menu = st.sidebar.radio("Navegação", ["Registrar Movimentação", "Inventário Atual", "Histórico"])

    if menu == "Registrar Movimentação":
        exibir_registrar()
    elif menu == "Inventário Atual":
        exibir_inventario()
    elif menu == "Histórico":
        exibir_historico()

if __name__ == "__main__":
    main()