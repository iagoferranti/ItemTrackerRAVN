from services.database import SupabaseService

def testar():
    try:
        db = SupabaseService()
        # Tenta buscar qualquer dado da tabela (mesmo que esteja vazia)
        res = db.client.table("movimentacoes").select("*", count="exact").limit(1).execute()
        print("✅ Conexão estabelecida com sucesso!")
        print(f"Linhas encontradas na tabela: {res.count}")
    except Exception as e:
        print("❌ Erro de conexão!")
        print(f"Detalhes: {e}")

if __name__ == "__main__":
    testar()