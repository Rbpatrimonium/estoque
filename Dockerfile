# 1. Use uma imagem Python oficial e leve como imagem base
FROM python:3.9-slim

# 2. Defina o diretorio de trabalho dentro do container
WORKDIR /app

# 3. Copie o arquivo de dependencias para o diretorio de trabalho
COPY requirements.txt .

# 4. Instale as dependencias
# O --no-cache-dir garante que o pip nao armazene o cache, reduzindo o tamanho da imagem
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie todos os outros arquivos do projeto (app.py, .csv, etc.)
COPY . .

# 6. Exponha a porta que o Streamlit utiliza
EXPOSE 8501

# 7. Defina a variavel de ambiente para o Streamlit rodar em modo "headless" (sem abrir navegador)
ENV STREAMLIT_SERVER_HEADLESS=true

# 8. O comando para executar a aplicacao quando o container iniciar
# --server.address=0.0.0.0 permite que o app seja acessado de fora do container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
