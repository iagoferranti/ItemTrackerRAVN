import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DiscordService:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    def enviar_log_movimentacao(self, item, de, para, status, label):
        """Envia um card formatado para o Discord"""
        if not self.webhook_url:
            return

        # Define a cor do card (Verde para Clã/Devolução, Vermelho para Empréstimo)
        color = 3066993 if status != 'EMPRESTADO' else 15158332

        payload = {
            "embeds": [{
                "title": f"🔄 Movimentação de Item: {item}",
                "color": color,
                "fields": [
                    {"name": "De", "value": f"👤 {de}", "inline": True},
                    {"name": "Para", "value": f"👤 {para}", "inline": True},
                    {"name": "Status", "value": f"📌 {status}", "inline": False},
                    {"name": "Label", "value": f"🏷️ {label}", "inline": True}
                ],
                "footer": {"text": "RAVN Item Tracker"},
                "timestamp": None # O Discord já coloca o tempo da mensagem
            }]
        }

        try:
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            print(f"Erro ao enviar para Discord: {e}")