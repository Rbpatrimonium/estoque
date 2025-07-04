import streamlit as st
import pandas as pd

# Funcao para carregar os dados do estoque
def carregar_dados(caminho_arquivo):
    try:
        return pd.read_csv(caminho_arquivo)
    except FileNotFoundError:
        st.error(f"Arquivo nao encontrado: {caminho_arquivo}")
        return pd.DataFrame()

# Funcao para salvar os dados do estoque
def salvar_dados(df, caminho_arquivo):
    df.to_csv(caminho_arquivo, index=False)
    st.success("Dados salvos com sucesso!")

# Funcao para verificar as credenciais
def verificar_credenciais(usuario, senha):
    try:
        usuarios_df = pd.read_csv("usuarios.csv")
        usuario_info = usuarios_df[
            (usuarios_df["usuario"] == usuario) & (usuarios_df["senha"] == senha)
        ]
        if not usuario_info.empty:
            return True, usuario_info.iloc[0]["grupo"]
        return False, None
    except FileNotFoundError:
        # Se o arquivo nao existe, cria um com o admin padrao
        dados = {'usuario': ['admin'], 'senha': ['admin'], 'grupo': ['TI']}
        df_usuarios = pd.DataFrame(dados)
        df_usuarios.to_csv("usuarios.csv", index=False)
        st.info("Arquivo de usuarios nao encontrado. Criado 'usuarios.csv' com usuario 'admin' e senha 'admin'.")
        return verificar_credenciais(usuario, senha)


# --- Tela de Login ---
def tela_login():
    st.title("Login - Controle de Estoque")
    
    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            autenticado, grupo = verificar_credenciais(usuario, senha)
            if autenticado:
                st.session_state["autenticado"] = True
                st.session_state["grupo_usuario"] = grupo
                st.session_state["usuario"] = usuario
                st.rerun()
            else:
                st.error("Usuario ou senha incorretos.")

# --- Aplicacao Principal ---
def main():
    st.set_page_config(page_title="Controle de Estoque", layout="wide")

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        tela_login()
    else:
        st.sidebar.title(f"Bem-vindo, {st.session_state['usuario']}!")
        
        grupo_usuario = st.session_state["grupo_usuario"]
        
        # Logica de selecao de estoque baseada no grupo
        if grupo_usuario == "TI":
            st.sidebar.write(f"Grupo: {st.session_state['grupo_usuario']}")
            tipo_estoque = st.sidebar.radio(
                "Selecione o Estoque:",
                ("Estoque TI", "Estoque Empresa"),
                key="selecao_estoque"
            )
        else: # Colaborador
            tipo_estoque = "Estoque Empresa"
            # Nenhuma informacao extra na barra lateral para o colaborador

        st.title(f"Gerenciamento de Estoque") # Titulo generico para o colaborador

        # Define o caminho do arquivo com base na selecao
        if tipo_estoque == "Estoque TI":
            caminho_arquivo = "estoque_ti.csv"
        else:
            caminho_arquivo = "estoque_empresa.csv"

        # Carrega os dados
        df = carregar_dados(caminho_arquivo)

        if not df.empty:
            st.subheader("Visualizar e Editar Estoque")
            # Usando o data_editor para visualizacao e edicao
            df_editado = st.data_editor(df, num_rows="dynamic", key=f"editor_{tipo_estoque}")

            # Botao para salvar as alteracoes
            if st.button("Salvar Alteracoes", key=f"salvar_{tipo_estoque}"):
                salvar_dados(df_editado, caminho_arquivo)
        
        # --- Cadastrar Novo Equipamento ---
        st.subheader("Cadastrar Novo Equipamento")
        with st.form(f"cadastro_form_{tipo_estoque}", clear_on_submit=True):
            novo_equipamento = st.text_input("Nome do Equipamento")
            nova_quantidade = st.number_input("Quantidade", min_value=0, step=1)
            
            # O campo extra (Localizacao/Setor) muda conforme o estoque
            if tipo_estoque == "Estoque TI":
                novo_extra = st.text_input("Localizacao")
                colunas = ["Equipamento", "Quantidade", "Localizacao"]
            else:
                novo_extra = st.text_input("Setor")
                colunas = ["Equipamento", "Quantidade", "Setor"]

            submit_cadastro = st.form_submit_button("Cadastrar")

            if submit_cadastro:
                if novo_equipamento: # Verifica se o nome do equipamento foi preenchido
                    nova_linha = pd.DataFrame([[novo_equipamento, nova_quantidade, novo_extra]], columns=colunas)
                    
                    # Carrega os dados mais recentes antes de concatenar
                    df_recente = carregar_dados(caminho_arquivo)
                    df_atualizado = pd.concat([df_recente, nova_linha], ignore_index=True)
                    
                    salvar_dados(df_atualizado, caminho_arquivo)
                    st.rerun() # Recarrega para mostrar a tabela atualizada
                else:
                    st.warning("O nome do equipamento e obrigatorio.")

        # Botao de Logout
        if st.sidebar.button("Logout"):
            st.session_state["autenticado"] = False
            st.session_state.pop("grupo_usuario", None)
            st.session_state.pop("usuario", None)
            st.rerun()


if __name__ == "__main__":
    main()
