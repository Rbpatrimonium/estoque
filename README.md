# Guia de Execução e Acesso - Sistema de Controle de Estoque

Este guia descreve como configurar e executar a aplicação de controle de estoque.

## 1. Pré-requisitos

- **Python 3.8+**: Certifique-se de ter o Python instalado. Você pode baixá-lo em [python.org](https://python.org).
- **PostgreSQL**: É necessário ter um servidor PostgreSQL em execução. Você pode instalá-lo a partir do [site oficial](https://www.postgresql.org/download/).

## 2. Configuração do Banco de Dados

1.  **Crie o Banco de Dados**:
    - Abra uma ferramenta de administração do PostgreSQL (como o `psql` ou pgAdmin).
    - Crie um novo banco de dados. O nome pode ser `estoque-db`, conforme sugerido no arquivo `.env`.

    ```sql
    CREATE DATABASE "estoque-db";
    ```

2.  **Execute o Script `schema.sql`**:
    - Conecte-se ao banco de dados recém-criado.
    - Execute o conteúdo do arquivo `schema.sql` para criar as tabelas e o usuário administrador padrão. Você pode usar o seguinte comando se tiver o `psql` instalado:

    ```bash
    psql -h SEU_HOST -p SEU_PORTA -U SEU_USUARIO -d estoque-db -f schema.sql
    ```

## 3. Configuração do Projeto

1.  **Crie um Ambiente Virtual**:
    É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

    ```bash
    python -m venv venv
    ```

2.  **Ative o Ambiente Virtual**:
    - **Windows**:
      ```bash
      .\venv\Scripts\activate
      ```
    - **macOS/Linux**:
      ```bash
      source venv/bin/activate
      ```

3.  **Instale as Dependências**:
    Com o ambiente virtual ativado, instale as bibliotecas necessárias a partir do `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Crie e Preencha o Arquivo `.env`**:
    Crie um arquivo chamado `.env` na raiz do projeto e adicione as credenciais de acesso ao seu banco de dados PostgreSQL. Substitua os valores conforme necessário.

    ```
    DB_HOST=147.93.12.64
    DB_PORT=5433
    DB_NAME=estoque-db
    DB_USER=postgres
    DB_PASSWORD=5d05366e653c2379b17c
    ```

## 4. Como Executar a Aplicação

Com o ambiente virtual ativado e o arquivo `.env` configurado, inicie a aplicação Streamlit com o seguinte comando:

```bash
streamlit run app.py
```

A aplicação estará acessível no seu navegador no endereço fornecido pelo Streamlit (geralmente `http://localhost:8501`).

## 5. Dados de Acesso Padrão

- **Usuário**: `admin`
- **Senha**: `admin123`
- **Grupo**: `TI`
