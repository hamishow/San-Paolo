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
c.execute('''CREATE TABLE IF NOT EXISTS receitas
              (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS detalhes_receitas
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

def produzir_receita():
    st.subheader('Produção de Receita')

    nome_receita = st.selectbox('Selecione a Receita', obter_nomes_receitas())

    quantidade_produzida = st.number_input('Quantidade Produzida (kg)', min_value=0.0, step=0.1)
    num_receitas = st.number_input('Número de Receitas Feitas', min_value=1, step=1)

    if st.button('Produzir'):
        conn = sqlite3.connect('estoque.db')
        c = conn.cursor()

        # Obter os detalhes da receita
        c.execute('SELECT insumo_id, quantidade FROM detalhes_receitas WHERE receita_id = ?', (obter_id_receita(nome_receita),))
        detalhes_receita = c.fetchall()

        # Atualizar a quantidade de cada insumo na tabela de insumos
        for detalhe in detalhes_receita:
            insumo_id, quantidade_por_receita = detalhe
            quantidade_total = quantidade_por_receita * num_receitas * quantidade_produzida
            c.execute('UPDATE insumos SET quantidade = quantidade - ? WHERE id = ?', (quantidade_total, insumo_id))

        # Adicionar a quantidade produzida como um novo insumo na tabela de insumos
        c.execute('INSERT INTO insumos (nome, quantidade) VALUES (?, ?)', (nome_receita, quantidade_produzida))

        conn.commit()
        conn.close()

        st.success(f'{num_receitas} receitas de {nome_receita} produzidas com sucesso!')

def obter_id_insumo(nome):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT id FROM insumos WHERE nome = ?', (nome,))
    insumo_id = c.fetchone()[0]
    conn.close()
    return insumo_id

def main():
    st.title('Controle de Estoque')

    operacao = st.sidebar.radio('Operação', ['Visualizar Estoque', 'Cadastrar Insumo', 'Registrar Entrada', 'Registrar Saída', 'Cadastrar Receita','produzir_receita'])

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
    elif operacao == 'produzir_receita':
        produzir_receita()

if __name__ == '__main__':
    main()


