import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DiscordService:
    def __init__(self):
        # No Streamlit Cloud, ele busca das 'Secrets' automaticamente
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    def enviar_log_movimentacao(self, item, de, para, status, label):
        """Envia um card formatado para o Discord com lógica de status"""
        if not self.webhook_url:
            return

        # Lógica de Cores e Ícones baseada no Status
        if status == 'EMPRESTADO':
            color = 15158332  # Vermelho
            emoji = "🔴"
            titulo = f"Novo Empréstimo: {item}"
        elif status == 'CLÃ':
            color = 3066993   # Verde
            emoji = "🏛️"
            titulo = f"Devolução para o Clã: {item}"
        else:  # Status 'DEVOLVIDO' (Dono original)
            color = 3447003   # Azul
            emoji = "👤"
            titulo = f"Retorno ao Dono: {item}"

        payload = {
            "embeds": [{
                "title": f"{emoji} {titulo}",
                "color": color,
                "fields": [
                    {"name": "De", "value": f"{de}", "inline": True},
                    {"name": "Para", "value": f"{para}", "inline": True},
                    {"name": "Status", "value": f"**{status}**", "inline": False},
                    {"name": "Label", "value": f"🏷️ {label}", "inline": True}
                ],
                "footer": {"text": "RAVN Item Tracker • Sistema de Notificações"},
            }]
        }

        try:
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            print(f"Erro ao enviar para Discord: {e}")