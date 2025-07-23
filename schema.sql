-- Script para criar o schema do banco de dados para o sistema de controle de estoque.

-- Tabela de usuários
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    grupo VARCHAR(50) NOT NULL
);

-- Tabela de equipamentos
CREATE TABLE equipamentos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    quantidade_minima INTEGER NOT NULL DEFAULT 0,
    quantidade_atual INTEGER NOT NULL DEFAULT 0,
    localizacao VARCHAR(255),
    tipo VARCHAR(50) DEFAULT 'Geral' -- Novo campo para tipo de equipamento (TI, Geral, etc.)
);

-- Tabela de entradas de equipamentos
CREATE TABLE entradas (
    id SERIAL PRIMARY KEY,
    equipamento_id INTEGER REFERENCES equipamentos(id),
    quantidade INTEGER NOT NULL,
    responsavel VARCHAR(100) NOT NULL,
    data TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    localizacao VARCHAR(100) NOT NULL
);

-- Tabela de saídas de equipamentos
CREATE TABLE saidas (
    id SERIAL PRIMARY KEY,
    equipamento_id INTEGER REFERENCES equipamentos(id),
    quantidade INTEGER NOT NULL,
    recebedor VARCHAR(100) NOT NULL,
    data TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Inserir usuário administrador padrão
INSERT INTO usuarios (nome, senha, grupo) VALUES ('admin', '$2b$12$mND.sroMVbT0lptdAkShiuYdnUSljhSgCSIUYUScBXgnkNipgK0EG', 'TI');
