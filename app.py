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

    st.markdown("""
    <style>
    /* Estilização do Botão Confirmar */
    div.stButton > button:first-child {
        background-color: #238636;
        color: white;
        border: 1px solid #2ea043;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #2ea043;
        border-color: #3fb950;
        transform: scale(1.02);
    }
    /* Melhora o contraste dos labels (nomes dos campos) */
    .stMarkdown p {
        color: #adbac7 !important;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

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

                # Agora 'Disponíveis' engloba o que está no Clã e o que voltou para o Dono
                disponiveis = len(df_atual[df_atual['status'].isin(['CLÃ', 'DEVOLVIDO'])])
                no_cla = len(df_atual[df_atual['status'] == 'CLÃ'])
                emprestados = total - disponiveis

                st.divider()
                # st.metric("📦 Itens Totais", total)
                # st.metric("🏛️ Disponíveis (Clã/Dono)", disponiveis)
                st.metric("🔴 Emprestados", emprestados)
                st.divider()
        except Exception:
            st.sidebar.warning("📊 Estatísticas indisponíveis")

        menu = st.radio("Navegação:", ["Inventário", "Registrar Repasse", "Histórico Geral", "Admin"])

    # --- ÁREA PRINCIPAL DE RENDERIZAÇÃO ---st.divider()
    st.subheader("⚠️ Pendências Ativas")

    pendentes = db.buscar_itens_pendentes()

    if not pendentes:
        st.success("Tudo em ordem no armazém!")
    else:
        for p in pendentes:
            # Cálculo dos dias
            hoje = pd.Timestamp.now(tz='UTC')
            data_mov = pd.to_datetime(p['occurred_at'], utc=True)
            dias = (hoje - data_mov).days
            
            # Cor do alerta baseada no tempo
            if dias < 3:
                emoji_tempo = "🟢"
            elif dias < 7:
                emoji_tempo = "🟡"
            else:
                emoji_tempo = "🔴"
                
            with st.expander(f"{emoji_tempo} {p['to_person']}"):
                st.caption(f"**Item:** {p['item_name']}")
                st.caption(f"**Tempo:** {dias} dia(s) fora")
                st.caption(f"**Desde:** {data_mov.strftime('%d/%m')}")

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