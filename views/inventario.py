import streamlit as st
import pandas as pd
from services.database import SupabaseService
from services.notifications import DiscordService
import datetime

def exibir_inventario():
    st.header("🔍 Inventário Atual")
    db = SupabaseService()
    
    try:
        lista_pessoas, lista_itens, _ = db.get_opcoes_autocomplete()
    except:
        lista_pessoas, lista_itens = [], []

    res = db.buscar_todas_movimentacoes()
    if not res.data:
        st.warning("Nenhuma movimentação encontrada.")
        return

    df = pd.DataFrame(res.data)
    df['occurred_at'] = pd.to_datetime(df['occurred_at'], errors='coerce', utc=True)
    df = df.dropna(subset=['occurred_at'])

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        search_item = st.selectbox("Filtrar por Item:", options=["TODOS"] + lista_itens)
    with col_f2:
        search_person = st.selectbox("Filtrar por Pessoa:", options=["TODOS", "ARMAZÉM DO CLÃ"] + lista_pessoas)

    # Identifica o estado atual de cada par Item + Label
    idx_mais_recente = df.groupby(['item_name', 'label'])['occurred_at'].idxmax()
    df_atual = df.loc[idx_mais_recente].copy()

    if search_item != "TODOS":
        df_atual = df_atual[df_atual['item_name'] == search_item]
    
    df_atual['portador_real'] = df_atual.apply(
        lambda x: "ARMAZÉM DO CLÃ" if x['status'] == 'CLÃ' else x['to_person'], axis=1
    )

    if search_person != "TODOS":
        df_atual = df_atual[df_atual['portador_real'] == search_person]

    st.write("---")
    
    for index, row in df_atual.iterrows():
        # Lógica de Trava: O botão SÓ aparece se o status for exatamente 'EMPRESTADO'
        esta_emprestado = row['status'] == 'EMPRESTADO'
        is_no_cla = row['status'] == 'CLÃ'
        
        bg_color = "#161b22"
        # Borda: Verde para Clã, Azul para Devolvido (Disponível), Vermelho para Emprestado
        if is_no_cla: border_color = "#238636"
        elif esta_emprestado: border_color = "#da3633"
        else: border_color = "#1f6feb" # Azul para status 'DEVOLVIDO'

        data_formatada = row['occurred_at'].strftime('%d/%m/%Y %H:%M')

        with st.container():
            st.markdown(f"""
                <div style="background-color: {bg_color}; border-left: 5px solid {border_color}; padding: 8px 15px; border-radius: 4px; margin-bottom: 5px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 2;">
                            <span style="font-size: 1em; font-weight: bold; color: #adbac7;">{row['item_name']}</span>
                            <span style="color: #768390; font-size: 0.8em; margin-left: 8px;">({row['label']})</span>
                        </div>
                        <div style="flex: 1; text-align: center; color: #768390; font-size: 0.75em;">
                            🕒 {data_formatada}
                        </div>
                        <div style="flex: 1; text-align: right; font-size: 0.9em;">
                            <span style="color: #768390; font-size: 0.8em;">Portador:</span><br>
                            <span style="font-weight: bold; color: {border_color};">
                                {row['portador_real']}
                            </span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botões de Ação: Só aparecem se o item estiver com alguém (EMPRESTADO)
            if esta_emprestado:
                btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 4])
                with btn_col1:
                    if st.button(f"Devolver p/ Clã 🏛️", key=f"cla_{index}"):
                        executar_movimentacao_rapida(db, row['to_person'], "ARMAZÉM DO CLÃ", row, "CLÃ", "Devolução p/ Clã")
                with btn_col2:
                    # Inverte a ação: Devolve para quem emprestou
                    if st.button(f"Devolver p/ {row['from_person']} 👤", key=f"dono_{index}"):
                        executar_movimentacao_rapida(db, row['to_person'], row['from_person'], row, "DEVOLVIDO", f"Retorno p/ dono original")
            else:
                # Se o item está no Clã ou foi Devolvido, mostramos apenas uma etiqueta discreta
                st.caption(f"✅ Item disponível com {row['portador_real']}. Ciclo de empréstimo encerrado.")
            
            st.write("") 

def executar_movimentacao_rapida(db, de, para, row, status, nota):
    agora = datetime.datetime.now().isoformat()
    payload = {
        "from_person": de, "to_person": para, "item_name": row['item_name'],
        "label": row['label'], "status": status, "notes": nota, "occurred_at": agora
    }
    try:
        db.inserir_movimentacao(payload)
        
        # --- NOVO: DISPARO DE NOTIFICAÇÃO NO DISCORD ---
        discord = DiscordService()
        discord.enviar_log_movimentacao(
            item=row['item_name'], 
            de=de, 
            para=para, 
            status=status, 
            label=row['label']
        )
        
        st.toast(f"✅ {row['item_name']} atualizado e notificado!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro: {e}")