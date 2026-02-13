import streamlit as st
from services.database import SupabaseService
from services.notifications import DiscordService
import datetime

from services.notifications import DiscordService

def exibir_registrar():
    db = SupabaseService()
    st.header("📦 Registrar Novo Repasse")
    
    # --- FEEDBACK DO ÚLTIMO REGISTRO ---
    # Mantém uma faixa informativa caso uma ação tenha acabado de ser realizada
    if "ultimo_registro" in st.session_state:
        reg = st.session_state.ultimo_registro
        st.info(f"✨ **Último registro:** {reg['item']} ({reg['label']}) -> **{reg['to']}**")

    # Busca as listas para o autocomplete no banco de dados
    lista_pessoas, lista_itens, lista_labels = db.get_opcoes_autocomplete()

    # --- BLOCO 1: IDENTIFICAÇÃO DO ITEM ---
    # Usamos um container com borda para separar visualmente a seção do item
    with st.container(border=True):
        st.subheader("🔍 Informações do Item")
        col_item1, col_item2 = st.columns(2)
        
        with col_item1:
            item_sel = st.selectbox("Selecione o Item:", options=["[DIGITAR NOVO]"] + lista_itens)
            if item_sel == "[DIGITAR NOVO]":
                item = st.text_input("Nome do Novo Item:").upper().strip()
                portador_sugerido = "[DIGITAR NOVO]" # Item novo não tem portador antigo
            else:
                item = item_sel
                st.info(f"Item: **{item}**")

        with col_item2:
            if item_sel == "[DIGITAR NOVO]":
                label = st.text_input("Nova Label (ex: +12, XP-01):", value="ÚNICO").upper().strip()
            else:
                label_sel = st.selectbox("Selecione a Label:", options=lista_labels)
                label = label_sel
                # INTELIGÊNCIA: Busca quem é o dono atual desse item específico
                portador_sugerido = db.get_portador_atual(item, label)

    st.write("") # Espaçador visual

    # --- BLOCO 2: DETALHES DA MOVIMENTAÇÃO ---
    with st.container(border=True):
        st.subheader("🔄 Detalhes do Repasse")
        col_mov1, col_mov2 = st.columns(2)
        
        with col_mov1:
            # O campo 'De' já sugere quem o banco de dados indicou como portador atual
            from_p_sel = st.selectbox("De (Quem está passando):", 
                                      options=[portador_sugerido] + [p for p in lista_pessoas if p != portador_sugerido])
            
            if from_p_sel == "[DIGITAR NOVO]":
                from_p = st.text_input("Nome do novo Portador:").upper().strip()
            else:
                from_p = from_p_sel
                if portador_sugerido != "[DIGITAR NOVO]":
                    st.caption(f"💡 Sugestão automática: **{portador_sugerido}**")

            status = st.selectbox("Status da Ação:", ["EMPRESTADO", "DEVOLVIDO", "CLÃ"])

        with col_mov2:
            to_p_sel = st.selectbox("Para (Quem está recebendo):", options=["[DIGITAR NOVO]"] + lista_pessoas)
            if to_p_sel == "[DIGITAR NOVO]":
                to_p = st.text_input("Nome do novo Destinatário:").upper().strip()
            else:
                to_p = to_p_sel
                
            data_evento = st.date_input("Data do Evento:", datetime.date.today())

        notes = st.text_area("Observações Adicionais (Opcional):")

    # --- BOTÃO DE SALVAMENTO ---
    # use_container_width faz o botão ocupar a largura toda, ficando mais fácil de clicar no mobile
    if st.button("💾 Confirmar Registro de Movimentação", use_container_width=True):
        if not from_p or not to_p or not item:
            st.error("⚠️ Erro: Os campos 'De', 'Para' e 'Item' são obrigatórios.")
        else:
            # Combina a data selecionada com o horário atual para precisão no histórico
            agora = datetime.datetime.now().time()
            dt_combinada = datetime.datetime.combine(data_evento, agora).isoformat()
            
            payload = {
                "from_person": from_p, 
                "to_person": to_p, 
                "item_name": item,
                "label": label, 
                "status": status, 
                "notes": notes, 
                "occurred_at": dt_combinada
            }
            
            try:
                db.inserir_movimentacao(payload)

                discord = DiscordService()
                discord.enviar_log_movimentacao(item, from_p, to_p, status, label)
                
                # Salva no estado da sessão para mostrar o feedback após o refresh
                st.session_state.ultimo_registro = {
                    "item": item, "to": to_p, "label": label
                }
                
                st.toast(f"✅ {item} registrado com sucesso!", icon='🚀')
                st.balloons()
                
                # Recarrega a página para limpar os campos e atualizar as listas de sugestão
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar no banco de dados: {e}")