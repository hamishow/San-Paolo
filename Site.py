import streamlit as st
import sqlite3
import pandas as pd

# Criar a conexão com o banco de dados
conn = sqlite3.connect('estoque.db')
c = conn.cursor()

# Criar a tabela de insumos
c.execute('''CREATE TABLE IF NOT EXISTS insumos
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, quantidade REAL)''')

# Criar a tabela de receitas e ingredientes
c.execute('''CREATE TABLE IF NOT EXISTS receitas
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS ingredientes
             (id INTEGER PRIMARY KEY AUTOINCREMENT, receita_id INTEGER, insumo_id INTEGER, quantidade REAL)''')

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

def visualizar_estoque():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT nome, quantidade FROM insumos')
    data = c.fetchall()
    conn.close()

    if not data:
        st.warning('Não há insumos cadastrados.')
    else:
        st.write('### Quantidade de Insumos')
        df = pd.DataFrame(data, columns=['Nome', 'Quantidade'])
        df['Quantidade'] = df['Quantidade'].astype(str) + ' kg'  # Adiciona "kg" à quantidade
        st.write(df)

def obter_nomes_insumos():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT nome FROM insumos')
    data = c.fetchall()
    conn.close()
    return [nome[0] for nome in data]

def cadastrar_receita():
    st.subheader('Cadastrar Receita')

    nome_receita = st.text_input('Nome da Receita')

    ingredientes = []
    num_ingredientes = st.number_input('Número de Ingredientes', min_value=1, step=1)
    for i in range(num_ingredientes):
        ingrediente_nome = st.selectbox(f'Ingrediente {i+1}', obter_nomes_insumos())
        ingrediente_quantidade = st.number_input(f'Quantidade de {ingrediente_nome} (kg)', min_value=0.0, step=0.1)
        ingredientes.append({'nome': ingrediente_nome, 'quantidade': ingrediente_quantidade})

    if st.button('Cadastrar'):
        conn = sqlite3.connect('estoque.db')
        c = conn.cursor()

        # Inserir a receita na tabela receitas
        c.execute('INSERT INTO receitas (nome) VALUES (?)', (nome_receita,))
        receita_id = c.lastrowid

        # Atualizar a tabela de insumos
        for ingrediente in ingredientes:
            insumo_id = obter_id_insumo(ingrediente['nome'])
            c.execute('INSERT INTO ingredientes (receita_id, insumo_id, quantidade) VALUES (?, ?, ?)', (receita_id, insumo_id, ingrediente['quantidade']))

        conn.commit()
        conn.close()

        st.success('Receita cadastrada com sucesso!')

def obter_id_insumo(nome):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT id FROM insumos WHERE nome = ?', (nome,))
    insumo_id = c.fetchone()[0]
    conn.close()
    return insumo_id

def main():
    st.title('Controle de Estoque')

    operacao = st.sidebar.radio('Operação', ['Visualizar Estoque', 'Cadastrar Insumo', 'Registrar Entrada', 'Registrar Saída', 'Cadastrar Receita'])

    if operacao == 'Cadastrar Insumo':
        nome = st.text_input('Nome do Insumo')
        quantidade = st.number_input('Quantidade', min_value=0.0, step=0.1)
        if st.button('Cadastrar'):
            cadastrar_insumo(nome, quantidade)
            st.success('Insumo cadastrado com sucesso!')

    elif operacao == 'Registrar Entrada':
        nome = st.selectbox('Insumo', obter_nomes_insumos())
        quantidade = st.number_input('Quantidade', min_value=0.0, step=0.1)
        if st.button('Registrar'):
            entrada_insumo(nome, quantidade)
            st.success('Entrada registrada com sucesso!')

    elif operacao == 'Registrar Saída':
        nome = st.selectbox('Insumo', obter_nomes_insumos())
        quantidade = st.number_input('Quantidade', min_value=0.0, step=0.1)
        if st.button('Registrar'):
            saida_insumo(nome, quantidade)
            st.success('Saída registrada com sucesso!')

    elif operacao == 'Visualizar Estoque':
        visualizar_estoque()

    elif operacao == 'Cadastrar Receita':
        cadastrar_receita()

if __name__ == '__main__':
    main()


