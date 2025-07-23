

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- Detalhes da Conexão (sem especificar um DB que não existe) ---
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_TO_CREATE = os.getenv("DB_NAME")

conn = None
try:
    # Conecta-se ao banco de dados de manutenção padrão (postgres)
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname='postgres'  # Conecta-se a um DB existente para criar um novo
    )
    conn.autocommit = True  # CREATE DATABASE não pode ser executado em uma transação
    
    with conn.cursor() as cur:
        # Verifica se o banco de dados já existe antes de tentar criar
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_TO_CREATE}'")
        if cur.fetchone():
            print(f"O banco de dados '{DB_TO_CREATE}' já existe.")
        else:
            print(f"Criando o banco de dados '{DB_TO_CREATE}'...")
            cur.execute(f"CREATE DATABASE \"{DB_TO_CREATE}\"")
            print(f"Banco de dados '{DB_TO_CREATE}' criado com sucesso.")

except psycopg2.OperationalError as e:
    print(f"Erro de conexão: {e}")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
finally:
    if conn:
        conn.close()

