
import streamlit as st
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import bcrypt
import pandas as pd

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# --- Conexão com o Banco de Dados ---
def get_db_connection():
    """Estabelece e retorna uma conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error(f"Erro de conexão com o banco de dados: {e}")
        return None

# --- Funções de Autenticação ---
def hash_password(password):
    """Gera o hash de uma senha usando bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(username, password):
    """Autentica o usuário, retornando o grupo se as credenciais forem válidas."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT senha, grupo FROM usuarios WHERE nome = %s", (username,))
            result = cur.fetchone()
        conn.close()
        if result and check_password(password, result[0]):
            return result[1] # Retorna o grupo do usuário
    return None

def add_user(nome, senha, grupo):
    """Adiciona um novo usuário ao banco de dados."""
    conn = get_db_connection()
    if conn:
        try:
            hashed_password = hash_password(senha)
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuarios (nome, senha, grupo) VALUES (%s, %s, %s)",
                    (nome, hashed_password, grupo)
                )
                conn.commit()
            return True
        except psycopg2.IntegrityError:
            st.error(f"Erro: Usuário '{nome}' já existe.")
            return False
        except Exception as e:
            st.error(f"Erro ao adicionar usuário: {e}")
            return False
        finally:
            conn.close()
    return False

# --- Funções de Banco de Dados (CRUD) ---

# Equipamentos
def add_equipment(nome, marca, modelo, quantidade_minima, localizacao, tipo):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO equipamentos (nome, marca, modelo, quantidade_minima, localizacao, tipo) VALUES (%s, %s, %s, %s, %s, %s)",
                (nome, marca, modelo, quantidade_minima, localizacao, tipo)
            )
            conn.commit()
        conn.close()
        return True
    return False

def get_all_equipment():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, marca, modelo, quantidade_atual, quantidade_minima, localizacao, tipo FROM equipamentos ORDER BY nome")
            data = cur.fetchall()
        conn.close()
        return data
    return []

# Entradas
def register_entry(equipamento_id, quantidade, responsavel, localizacao):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            # Adiciona o registro de entrada
            cur.execute(
                "INSERT INTO entradas (equipamento_id, quantidade, responsavel, localizacao) VALUES (%s, %s, %s, %s)",
                (equipamento_id, quantidade, responsavel, localizacao)
            )
            # Atualiza a quantidade em estoque
            cur.execute(
                "UPDATE equipamentos SET quantidade_atual = quantidade_atual + %s WHERE id = %s",
                (quantidade, equipamento_id)
            )
            conn.commit()
        conn.close()
        return True
    return False

# Saídas
def register_exit(equipamento_id, quantidade, recebedor):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            # Verifica se há estoque suficiente
            cur.execute("SELECT quantidade_atual FROM equipamentos WHERE id = %s", (equipamento_id,))
            available_quantity = cur.fetchone()[0]
            if available_quantity >= quantidade:
                # Adiciona o registro de saída
                cur.execute(
                    "INSERT INTO saidas (equipamento_id, quantidade, recebedor) VALUES (%s, %s, %s)",
                    (equipamento_id, quantidade, recebedor)
                )
                # Atualiza a quantidade em estoque
                cur.execute(
                    "UPDATE equipamentos SET quantidade_atual = quantidade_atual - %s WHERE id = %s",
                    (quantidade, equipamento_id)
                )
                conn.commit()
                conn.close()
                return True, "Saída registrada com sucesso."
            else:
                conn.close()
                return False, f"Estoque insuficiente. Quantidade disponível: {available_quantity}"
    return False, "Erro de conexão com o banco de dados."


# --- Interface Streamlit ---

def login_page():
    """Renderiza a página de login."""
    st.header("Login do Sistema de Controle de Estoque")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user_group = authenticate_user(username, password)
        if user_group:
            st.session_state['logged_in'] = True
            st.session_state['user_group'] = user_group
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

def main_app():
    """Renderiza a aplicação principal após o login."""
    st.sidebar.title(f"Bem-vindo, {st.session_state['username']}!")
    if st.session_state['user_group'] == 'TI':
        st.sidebar.write(f"Grupo: {st.session_state['user_group']}")

    # Navegação baseada no grupo do usuário
    if st.session_state['user_group'] == 'TI':
        pages = {
            "Dashboard de Estoque": dashboard_page,
            "Cadastro de Equipamentos": equipment_registration_page,
            "Registrar Entrada": entry_registration_page,
            "Registrar Saída": exit_registration_page,
            "Cadastro de Usuários": user_registration_page # Nova página
        }
    else: # Usuario
        pages = {
            "Dashboard de Estoque": dashboard_page,
            "Cadastro de Equipamentos": equipment_registration_page, # Added for Usuario
            "Registrar Entrada": entry_registration_page, # Added for Usuario
            "Registrar Saída": exit_registration_page # Added for Usuario
        }

    selection = st.sidebar.radio("Navegar", list(pages.keys()))
    pages[selection]()

    if st.sidebar.button("Sair"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def dashboard_page():
    """Exibe o dashboard com o status do estoque."""
    st.title("Dashboard de Estoque")
    equipments = get_all_equipment()

    # Filtrar equipamentos com base no grupo do usuário
    if st.session_state['user_group'] == 'Usuario':
        equipments = [eq for eq in equipments if eq[7] == 'Geral'] # Usuários veem apenas itens 'Geral'
    elif st.session_state['user_group'] == 'TI':
        # Por padrão, TI vê apenas itens 'TI'
        initial_equipments = equipments
        equipments = [eq for eq in initial_equipments if eq[7] == 'TI']

        show_general_items = st.checkbox("Mostrar Itens Gerais")
        if show_general_items:
            # Se o checkbox for marcado, inclui também os itens 'Geral'
            equipments = [eq for eq in initial_equipments if eq[7] == 'TI' or eq[7] == 'Geral']

    if equipments:
        column_names = ["ID", "Nome", "Marca", "Modelo", "Quantidade Atual", "Quantidade Mínima", "Localização", "Tipo"]
        df = pd.DataFrame(equipments, columns=column_names)
        df_display = df.drop(columns=["ID"])

        # Exibe em formato de tabela
        st.dataframe(df_display, hide_index=True)

        # Alertas de estoque baixo
        low_stock_items = df[df["Quantidade Atual"] < df["Quantidade Mínima"]]
        if not low_stock_items.empty:
            st.warning("Alerta de Estoque Baixo!")
            for index, item in low_stock_items.iterrows():
                st.error(f"O item '{item["Nome"]}' está com estoque baixo! Quantidade atual: {item["Quantidade Atual"]}, Mínima: {item["Quantidade Mínima"]}")
    else:
        st.info("Nenhum equipamento cadastrado.")

def equipment_registration_page():
    """Página para cadastrar novos equipamentos."""
    st.title("Cadastro de Equipamentos")
    with st.form("new_equipment_form"):
        nome = st.text_input("Nome do Equipamento")
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        localizacao = st.text_input("Localização do Equipamento") # Novo campo

        if st.session_state['user_group'] == 'TI':
            tipo = st.selectbox("Tipo de Equipamento", ['Geral', 'TI'], index=1) # 'TI' como padrão
        else:
            tipo = 'Geral' # Default for 'Usuario' group

        quantidade_minima = st.number_input("Quantidade Mínima", min_value=0, step=1)
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            if nome:
                if add_equipment(nome, marca, modelo, quantidade_minima, localizacao, tipo):
                    st.success("Equipamento cadastrado com sucesso!")
                else:
                    st.error("Erro ao cadastrar o equipamento.")
            else:
                st.warning("O nome do equipamento é obrigatório.")

def entry_registration_page():
    """Página para registrar a entrada de equipamentos."""
    st.title("Registrar Entrada de Equipamento")
    equipments = get_all_equipment()

    # Filtrar equipamentos para usuários do grupo 'Usuario'
    if st.session_state['user_group'] == 'Usuario':
        equipments = [eq for eq in equipments if eq[7] == 'Geral'] # eq[7] é o campo 'tipo'

    # Modificado para exibir Nome Marca Modelo
    equipment_options = {f"{eq[1]} {eq[2]} {eq[3]} (ID: {eq[0]})": eq[0] for eq in equipments} 

    with st.form("entry_form"):
        selected_equipment_str = st.selectbox("Selecione o Equipamento", options=list(equipment_options.keys()))
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        responsavel = st.text_input("Responsável pela Entrada", value=st.session_state.get('username', ''))
        localizacao = st.text_input("Localização/Armazenamento")
        submitted = st.form_submit_button("Registrar Entrada")

        if submitted:
            equipamento_id = equipment_options[selected_equipment_str]
            if register_entry(equipamento_id, quantidade, responsavel, localizacao):
                st.success("Entrada registrada com sucesso!")
            else:
                st.error("Erro ao registrar a entrada.")

def exit_registration_page():
    """Página para registrar a saída de equipamentos."""
    st.title("Registrar Saída de Equipamento")
    equipments = get_all_equipment()

    # Filtrar equipamentos para usuários do grupo 'Usuario'
    if st.session_state['user_group'] == 'Usuario':
        equipments = [eq for eq in equipments if eq[7] == 'Geral'] # eq[7] é o campo 'tipo'

    # Modificado para exibir Nome Marca Modelo
    equipment_options = {f"{eq[1]} {eq[2]} {eq[3]} (ID: {eq[0]})": eq[0] for eq in equipments}

    with st.form("exit_form"):
        selected_equipment_str = st.selectbox("Selecione o Equipamento", options=list(equipment_options.keys()))
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        recebedor = st.text_input("Recebedor")
        submitted = st.form_submit_button("Registrar Saída")

        if submitted:
            if recebedor:
                equipamento_id = equipment_options[selected_equipment_str]
                success, message = register_exit(equipamento_id, quantidade, recebedor)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("O nome do recebedor é obrigatório.")

def user_registration_page():
    """Página para cadastrar novos usuários (apenas para administradores)."""
    st.title("Cadastro de Usuários")
    if st.session_state['user_group'] != 'TI':
        st.warning("Você não tem permissão para acessar esta página.")
        return

    with st.form("new_user_form"):
        username = st.text_input("Nome de Usuário")
        password = st.text_input("Senha", type="password")
        group = st.selectbox("Grupo", ['TI', 'Usuario']) # Alterado de 'Administrador' para 'TI'
        submitted = st.form_submit_button("Cadastrar Usuário")

        if submitted:
            if username and password:
                if add_user(username, password, group):
                    st.success(f"Usuário '{username}' cadastrado com sucesso no grupo '{group}'!")
                else:
                    st.error("Erro ao cadastrar usuário.")
            else:
                st.warning("Nome de usuário e senha são obrigatórios.")

# --- Controle de Fluxo Principal ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_app()
else:
    login_page()
