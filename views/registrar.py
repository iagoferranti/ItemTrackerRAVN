import streamlit as st
from services.database import SupabaseService
from services.notifications import DiscordService
import datetime

def exibir_registrar():
    db = SupabaseService()
    st.header("📦 Registrar Novo Repasse")
    
    # --- FEEDBACK DO ÚLTIMO REGISTRO ---
    if "ultimo_registro" in st.session_state:
        reg = st.session_state.ultimo_registro
        st.info(f"✨ **Último registro:** {reg['item']} ({reg['label']}) -> **{reg['to']}**")

    # Busca as listas para o autocomplete no banco de dados
    lista_pessoas, lista_itens, lista_labels = db.get_opcoes_autocomplete()

    # --- BLOCO 1: IDENTIFICAÇÃO DO ITEM ---
    with st.container(border=True):
        st.subheader("🔍 Informações do Item")
        col_item1, col_item2 = st.columns(2)
        
        with col_item1:
            item_sel = st.selectbox("Selecione o Item:", options=["[DIGITAR NOVO]"] + lista_itens)
            if item_sel == "[DIGITAR NOVO]":
                item = st.text_input("Nome do Novo Item:").upper().strip()
                portador_sugerido = "[DIGITAR NOVO]"
            else:
                item = item_sel
                st.info(f"Item: **{item}**")

        with col_item2:
            if item_sel == "[DIGITAR NOVO]":
                label = st.text_input("Nova Label (ex: +12, XP-01):", value="ÚNICO").upper().strip()
            else:
                label_sel = st.selectbox("Selecione a Label:", options=lista_labels)
                label = label_sel
                # Busca quem é o dono atual desse item específico
                portador_sugerido = db.get_portador_atual(item, label)

    st.write("") 

    # --- BLOCO 2: DETALHES DA MOVIMENTAÇÃO ---
    with st.container(border=True):
        st.subheader("🔄 Detalhes do Repasse")
        col_mov1, col_mov2 = st.columns(2)
        
        with col_mov1:
            st.markdown("**ORIGEM**")
            
            # --- CORREÇÃO DA DUPLICIDADE ---
            # Começamos a lista com o portador sugerido pelo banco
            opcoes_origem = [portador_sugerido]
            # Adicionamos o resto das pessoas da lista
            for p in lista_pessoas:
                if p != portador_sugerido:
                    opcoes_origem.append(p)
            # Só adicionamos o "[DIGITAR NOVO]" ao final se ele já não for o sugerido
            if "[DIGITAR NOVO]" not in opcoes_origem:
                opcoes_origem.append("[DIGITAR NOVO]")

            from_p_sel = st.selectbox(
                "Quem está passando o item:", 
                options=opcoes_origem,
                key="from_sel"
            )
            
            from_p_novo = ""
            if from_p_sel == "[DIGITAR NOVO]":
                from_p_novo = st.text_input("👉 Digite AQUI o nome do NOVO Portador:").upper().strip()
                from_p = from_p_novo
            else:
                from_p = from_p_sel
                if from_p != "[DIGITAR NOVO]":
                    st.success(f"Confirmado: **{from_p}**")

            status = st.selectbox("Status da Ação:", ["EMPRESTADO", "DEVOLVIDO", "CLÃ"])

        with col_mov2:
            st.markdown("**DESTINO**")
            # Para o destino, a lista é simples, sem sugestão inteligente
            to_p_sel = st.selectbox(
                "Quem vai receber o item:", 
                options=["[DIGITAR NOVO]"] + lista_pessoas,
                key="to_sel"
            )
            
            to_p_novo = ""
            if to_p_sel == "[DIGITAR NOVO]":
                to_p_novo = st.text_input("👉 Digite AQUI o nome do NOVO Destinatário:").upper().strip()
                to_p = to_p_novo
            else:
                to_p = to_p_sel
                if to_p != "[DIGITAR NOVO]":
                    st.success(f"Confirmado: **{to_p}**")
                
            data_evento = st.date_input("Data do Evento:", datetime.date.today())

        notes = st.text_area("Observações Adicionais (Opcional):")

    # --- BOTÃO DE SALVAMENTO COM TRAVA DE SEGURANÇA ---
    if st.button("💾 Confirmar Registro de Movimentação", use_container_width=True):
        erro_novo_de = from_p_sel == "[DIGITAR NOVO]" and not from_p_novo
        erro_novo_para = to_p_sel == "[DIGITAR NOVO]" and not to_p_novo
        
        if erro_novo_de or erro_novo_para:
            st.error("❌ Erro de Preenchimento: Você selecionou '[DIGITAR NOVO]', mas esqueceu de escrever o nome na caixa de texto.")
        elif not from_p or not to_p or not item or from_p == "[DIGITAR NOVO]" or to_p == "[DIGITAR NOVO]":
            st.error("⚠️ Erro: Os campos de 'Portador', 'Destinatário' e 'Item' precisam ser preenchidos corretamente.")
        else:
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

                # Notificação Discord
                discord = DiscordService()
                discord.enviar_log_movimentacao(item, from_p, to_p, status, label)
                
                # Feedback e Reset
                st.session_state.ultimo_registro = {
                    "item": item, "to": to_p, "label": label
                }
                
                st.toast(f"✅ {item} registrado com sucesso!", icon='🚀')
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar no banco de dados: {e}")