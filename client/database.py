import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import json

# Carregar variáveis do arquivo .env
load_dotenv()

# Função para conectar ao banco de dados
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        raise Exception(f"Erro ao conectar ao banco de dados: {e}")

# Função para criar ou alterar a tabela usuario
def create_or_alter_user_table():
    conn = connect_to_db()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Criar a tabela se ela não existir
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuario (
                    usuario_nome VARCHAR(256) PRIMARY KEY,
                    senha VARCHAR(256) NOT NULL,
                    posts_enviados JSONB DEFAULT '{}'::JSONB,
                    seguindo JSONB DEFAULT '[]'::JSONB,
                    seguido_por JSONB DEFAULT '[]'::JSONB,
                    mensagens_privadas JSONB DEFAULT '{}'::JSONB
                );
            """)

            # Verificar e adicionar/alterar colunas, se necessário
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'usuario';
            """)
            # existing_columns = [row[0] for row in cur.fetchall()]

            # Adicionar colunas que não existem
            # if 'posts_enviados' not in existing_columns:
            #     cur.execute("ALTER TABLE IF NOT EXISTS usuario ADD COLUMN posts_enviados JSONB DEFAULT '{}'::JSONB;")
            # if 'seguindo' not in existing_columns:
            #     cur.execute("ALTER TABLE IF NOT EXISTS usuario ADD COLUMN seguindo JSONB DEFAULT '[]'::JSONB;")
            # if 'seguido_por' not in existing_columns:
            #     cur.execute("ALTER TABLE IF NOT EXISTS usuario ADD COLUMN seguido_por JSONB DEFAULT '[]'::JSONB;")
            # if 'mensagens_privadas' not in existing_columns:
            #     cur.execute("ALTER TABLE IF NOT EXISTS usuario ADD COLUMN private_messages JSONB DEFAULT '{}'::JSONB;")

            conn.commit()
            print("Tabela 'usuario' criada ou alterada com sucesso.")
    except Exception as e:
        raise Exception(f"Erro ao criar ou alterar a tabela 'usuario': {e}")
    finally:
        conn.close()

def get_mutuals(username):
    conn = connect_to_db()
    try:
        with conn.cursor() as cur:
            # Busca as duas listas JSONB
            cur.execute("""
                SELECT seguindo, seguido_por
                  FROM usuario
                 WHERE usuario_nome = %s
            """, (username,))
            row = cur.fetchone()
            if not row:
                return []

            seguindo, seguido_por = row

            # Se por acaso vier como string, converte a JSON Python
            if isinstance(seguindo, str):
                seguindo = json.loads(seguindo)
            if isinstance(seguido_por, str):
                seguido_por = json.loads(seguido_por)

            # psycopg2 já converte JSONB em lista Python, então geralmente não precisa do loads

            # Intersecção simples em Python
            return [u for u in seguindo if u in seguido_por]
    finally:
        conn.close()



# Chamar a função para criar ou alterar a tabela ao importar o módulo
create_or_alter_user_table()