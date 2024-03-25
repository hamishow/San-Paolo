import streamlit as st
import sqlite3
import pandas as pd


# Criar a conexão com o banco de dados
conn = sqlite3.connect('estoque.db')
c = conn.cursor()

# Criar a tabela de insumos
c.execute('''CREATE TABLE IF NOT EXISTS insumos
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, quantidade INTEGER)''')

# Commit e fechar a conexão
conn.commit()
conn.close()
def cadastrar_insumo(nome, quantidade):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('INSERT INTO insumos (nome, quantidade) VALUES (?, ?)', (nome, quantidade))
    conn.commit()
    conn.close()

def entrada_insumo(nome, quantidade):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('UPDATE insumos SET quantidade = quantidade + ? WHERE nome = ?', (quantidade, nome))
    conn.commit()
    conn.close()

def saida_insumo(nome, quantidade):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('UPDATE insumos SET quantidade = quantidade - ? WHERE nome = ?', (quantidade, nome))
    conn.commit()
    conn.close()
def main():
    st.title('Controle de Estoque')

    opcao_cadastrar = st.button('Cadastrar Insumo')
    opcao_entrada = st.button('Registrar Entrada')
    opcao_saida = st.button('Registrar Saída')
    opcao_visualizar = st.button('Visualizar Estoque')

    if opcao_cadastrar:
        nome = st.text_input('Nome do Insumo')
        quantidade = st.number_input('Quantidade', min_value=0.0, step=0.1)
        if st.button('Cadastrar'):
            cadastrar_insumo(nome, quantidade)
            st.success('Insumo cadastrado com sucesso!')

    elif opcao_entrada:
        nome = st.selectbox('Insumo', obter_nomes_insumos())
        quantidade = st.number_input('Quantidade', min_value=0.0, step=0.1)
        if st.button('Registrar'):
            entrada_insumo(nome, quantidade)
            st.success('Entrada registrada com sucesso!')

    elif opcao_saida:
        nome = st.selectbox('Insumo', obter_nomes_insumos())
        quantidade = st.number_input('Quantidade', min_value=0.0, step=0.1)
        if st.button('Registrar'):
            saida_insumo(nome, quantidade)
            st.success('Saída registrada com sucesso!')

    elif opcao_visualizar:
        visualizar_estoque()

def obter_nomes_insumos():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT nome FROM insumos')
    data = c.fetchall()
    conn.close()
    return [nome[0] for nome in data]



if __name__ == '__main__':
    main()


