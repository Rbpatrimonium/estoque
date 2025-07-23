
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

def execute_sql_file(filepath):
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True # Para comandos DDL como CREATE TABLE
        
        with conn.cursor() as cur:
            with open(filepath, 'r') as f:
                sql_commands = f.read()
            
            # Executa todos os comandos SQL do arquivo
            cur.execute(sql_commands)
            print(f"Script {filepath} executado com sucesso no banco de dados {DB_NAME}.")

    except psycopg2.OperationalError as e:
        print(f"Erro de conexão com o banco de dados: {e}")
    except Exception as e:
        print(f"Ocorreu um erro ao executar o script SQL: {e}")
    finally:
        if conn:
            conn.close()

# Executa o script schema.sql
execute_sql_file('schema.sql')
