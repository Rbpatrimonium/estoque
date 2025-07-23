
import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- Detalhes da Conexão ---
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def execute_sql_command(command):
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        
        with conn.cursor() as cur:
            cur.execute(command)
            print(f"Comando SQL executado com sucesso: {command}")

    except psycopg2.OperationalError as e:
        print(f"Erro de conexão com o banco de dados: {e}")
    except Exception as e:
        print(f"Ocorreu um erro ao executar o comando SQL: {e}")
    finally:
        if conn:
            conn.close()

# Comando para adicionar a coluna 'tipo'
execute_sql_command("ALTER TABLE equipamentos ADD COLUMN IF NOT EXISTS tipo VARCHAR(50) DEFAULT 'Geral';")
