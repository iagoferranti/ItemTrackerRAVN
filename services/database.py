import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(url, key)

    def inserir_movimentacao(self, dados: dict):
        """Insere uma nova linha na tabela movimentacoes"""
        return self.client.table("movimentacoes").insert(dados).execute()

    def buscar_status_atual(self):
        """Busca a última movimentação de cada item/label"""
        # Aqui depois faremos a query inteligente com filtros
        return self.client.table("movimentacoes").select("*").order("occurred_at", desc=True).execute()

    def get_nomes_cadastrados(self):
        """Busca nomes de pessoas e itens para o autocomplete"""
        res = self.client.table("movimentacoes").select("from_person, to_person, item_name").execute()
        # Lógica para limpar e retornar listas únicas (faremos a seguir)
        return res.data
    
    def buscar_todas_movimentacoes(self):
        """Retorna todo o histórico para processamento no Python"""
        return self.client.table("movimentacoes").select("*").order("occurred_at", desc=True).execute()
    
    def get_portador_atual(self, item_name, label):
        """Retorna o nome da pessoa que está com o item agora"""
        res = self.client.table("movimentacoes") \
            .select("to_person, status") \
            .eq("item_name", item_name) \
            .eq("label", label) \
            .order("occurred_at", desc=True) \
            .limit(1) \
            .execute()
        
        if res.data:
            linha = res.data[0]
            # Se o último status foi 'CLÃ', o portador é o armazém
            if linha['status'] == 'CLÃ':
                return "ARMAZÉM DO CLÃ"
            return linha['to_person']
        return "[DIGITAR NOVO]" # Caso o item nunca tenha sido registrado

    def get_opcoes_autocomplete(self):
        """Busca nomes únicos de pessoas e itens já cadastrados"""
        res = self.client.table("movimentacoes").select("from_person, to_person, item_name, label").execute()
        
        if not res.data:
            return [], [], ["ÚNICO"]

        pessoas = set()
        itens = set()
        labels = {"ÚNICO"}
        
        for linha in res.data:
            pessoas.add(linha['from_person'])
            pessoas.add(linha['to_person'])
            itens.add(linha['item_name'])
            if linha['label']:
                labels.add(linha['label'])
            
        return sorted(list(pessoas)), sorted(list(itens)), sorted(list(labels))
    

    def buscar_movimentacoes_adm(self):
        """Retorna as últimas 20 movimentações para gestão"""
        return self.client.table("movimentacoes") \
            .select("*") \
            .order("occurred_at", desc=True) \
            .limit(20) \
            .execute()

    def deletar_movimentacao(self, registro_id):
        """Apaga um registro por ID"""
        return self.client.table("movimentacoes") \
            .delete() \
            .eq("id", registro_id) \
            .execute()