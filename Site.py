import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


# Criar a conexão com o banco de dados
conn = sqlite3.connect('estoque.db')
c = conn.cursor()

# Criar a tabela de insumos
c.execute('''CREATE TABLE IF NOT EXISTS insumos
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, quantidade REAL)''')

# Criar a tabela de pedidos
c.execute('''CREATE TABLE IF NOT EXISTS pedidos
             (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)''')

# Criar a tabela de detalhes de pedidos
c.execute('''CREATE TABLE IF NOT EXISTS detalhes_pedidos
             (id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER, receita_id INTEGER, quantidade INTEGER,
             FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
             FOREIGN KEY (receita_id) REFERENCES receitas(id))''')

# Criar a tabela de receitas e ingredientes
c.execute('''CREATE TABLE IF NOT EXISTS receitas
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS ingredientes
             (id INTEGER PRIMARY KEY AUTOINCREMENT, receita_id INTEGER, insumo_id INTEGER, quantidade REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS receitas
              (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS detalhes_receitas
              (id INTEGER PRIMARY KEY AUTOINCREMENT, receita_id INTEGER, insumo_id INTEGER, quantidade REAL)''')# Remover espaços em branco nos nomes das receitas
c.execute('UPDATE receitas SET nome = TRIM(nome)')
c.execute('DELETE FROM receitas WHERE id NOT IN (SELECT MIN(id) FROM receitas GROUP BY nome)')

# Commit e fechar a conexão
conn.commit()
conn.close()
def visualizar_itens_receita(nome_receita):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT receita_id, insumo_id, quantidade FROM detalhes_receitas WHERE receita_id = ?', (obter_id_receita(nome_receita),))
    data = c.fetchall()
    conn.close()

    if not data:
        st.warning('Não há itens cadastrados para esta receita.')
    else:
        st.write('### Itens da Receita')

        for receita_id, insumo_id, quantidade in data:
            st.write(f'{receita_id} - {insumo_id} - {quantidade} kg')
def calcular_insumos_pedidos():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()

    # Selecionar todas as receitas dos pedidos
    c.execute('''SELECT receita_id, SUM(quantidade) AS total_receita
                 FROM detalhes_pedidos
                 GROUP BY receita_id''')
    data = c.fetchall()
  

    # Calcular a quantidade total de insumos necessária
    insumos_necessarios = {}
    for receita_id, quantidade in data:
        c.execute('SELECT insumo_id, quantidade FROM detalhes_receitas WHERE receita_id = ?', (receita_id,))
        detalhes_receita = c.fetchall()
        for insumo_id, quantidade_receita in detalhes_receita:
            if insumo_id in insumos_necessarios:
                insumos_necessarios[insumo_id] += quantidade_receita * quantidade
            else:
                insumos_necessarios[insumo_id] = quantidade_receita * quantidade

    conn.close()

    return insumos_necessarios

def excluir_pedidos():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()

    # Excluir todos os pedidos
    c.execute('DELETE FROM pedidos')
    c.execute('DELETE FROM detalhes_pedidos')

    conn.commit()
    conn.close()
def obter_nome_insumo(insumo_id):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT nome FROM insumos WHERE id = ?', (insumo_id,))
    nome = c.fetchone()[0]
    conn.close()
    return nome


def limpar_receitas():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()

    # Remover espaços em branco nos nomes das receitas
    c.execute('UPDATE receitas SET nome = TRIM(nome)')

    # Remover receitas duplicadas, mantendo apenas a primeira ocorrência
    c.execute('DELETE FROM receitas WHERE id NOT IN (SELECT MIN(id) FROM receitas GROUP BY nome)')

    conn.commit()
    conn.close()
def cadastrar_insumo(nome, quantidade):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('INSERT INTO insumos (nome, quantidade) VALUES (?, ?)', (nome, quantidade))
    conn.commit()
    conn.close()
def cadastrar_pedido(receitas_quantidades):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()

    # Inserir o pedido na tabela de pedidos
    c.execute('INSERT INTO pedidos (data) VALUES (?)', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
    pedido_id = c.lastrowid

    # Inserir as receitas associadas ao pedido na tabela de detalhes de pedidos
    for receita, quantidade in receitas_quantidades.items():
        c.execute('INSERT INTO detalhes_pedidos (pedido_id, receita_id, quantidade) VALUES (?, ?, ?)', (pedido_id, obter_id_receita(receita), quantidade))

    conn.commit()
    conn.close()
def gestao_pedidos():
    st.title('Gestão de Pedidos')

    # Dicionário para armazenar a quantidade de cada receita
    receitas_quantidades = {}
    num_receitas = st.number_input('Número de Receitas', min_value=1, step=1)
    for i in range(num_receitas):
        receita = st.selectbox(f'Receita {i+1}', obter_nomes_receitas())
        quantidade = st.number_input(f'Quantidade de {receita}', min_value=1, step=1)
        receitas_quantidades[receita] = quantidade

    if st.button('Cadastrar Pedido'):
        cadastrar_pedido(receitas_quantidades)
        st.success('Pedido cadastrado com sucesso!')

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

        # Inserir os detalhes da receita na tabela detalhes_receitas
        for ingrediente in ingredientes:
            insumo_id = obter_id_insumo(ingrediente['nome'])
            c.execute('INSERT INTO detalhes_receitas (receita_id, insumo_id, quantidade) VALUES (?, ?, ?)', (receita_id, insumo_id, ingrediente['quantidade']))

        # Inserir a receita como um novo insumo na tabela de insumos
        c.execute('INSERT INTO insumos (nome, quantidade) VALUES (?, ?)', (nome_receita, 0.0))

        conn.commit()
        conn.close()

        st.success('Receita cadastrada com sucesso!')
def excluir_insumo(nome):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('DELETE FROM insumos WHERE nome = ?', (nome,))
    conn.commit()
    conn.close()
def excluir_receita(nome):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('DELETE FROM receitas WHERE nome = ?', (nome,))
    conn.commit()
    conn.close()
def visualizar_insumos():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT nome, quantidade FROM insumos')
    data = c.fetchall()
    conn.close()

    if not data:
        st.warning('Não há insumos cadastrados.')
    else:
        st.write('### Lista de Insumos')

        # Campo de pesquisa
        pesquisa = st.text_input('Pesquisar Insumo')

        for nome, quantidade in data:
            if pesquisa.lower() in nome.lower():
                col1, col2, col3 = st.columns([1, 2,3])  # Divide a linha em duas colunas
                col1.write(nome)
                col2.write(f'{quantidade} kg')
                if col3.button(f'Excluir {nome}'):
                    excluir_insumo(nome)
                    st.success(f'{nome} excluído com sucesso!')
def visualizar_receitas():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT nome FROM receitas')
    data = c.fetchall()
    conn.close()

    if not data:
        st.warning('Não há receitas cadastradas.')
    else:
        st.write('### Lista de Receitas')

        # Campo de pesquisa
        pesquisa = st.text_input('Pesquisar Receita')

        for nome_tupla in data:
            nome = nome_tupla[0]  # Acessa o primeiro elemento da tupla (nome da receita)
            if pesquisa.lower() in nome.lower():
                col1, col2, col3 = st.columns([1, 2, 3])  # Divide a linha em três colunas
                col1.write(nome)
                # Você pode adicionar aqui a exibição dos ingredientes da receita, se desejar
                if col3.button(f'Excluir {nome}'):
                    excluir_receita(nome)
                    st.success(f'{nome} excluído com sucesso!')


def entrada_insumo(nome, quantidade):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('UPDATE insumos SET quantidade = quantidade + ? WHERE nome = ?', (quantidade, nome))
    conn.commit()
    conn.close()
def obter_id_receita(nome_receita):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT id FROM receitas WHERE nome = ?', (nome_receita,))
    data = c.fetchone()
    conn.close()
    return data[0] if data else None


def saida_insumo(nome, quantidade):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('UPDATE insumos SET quantidade = quantidade - ? WHERE nome = ?', (quantidade, nome))
    conn.commit()
    conn.close()
def visualizar_insumos_necessarios():
    st.title('Insumos Necessários para Produzir Pedidos')

    insumos_necessarios = calcular_insumos_pedidos()

    if not insumos_necessarios:
        st.warning('Não há insumos necessários.')
    else:
        st.write('### Insumos Necessários')
        for insumo_id, quantidade in insumos_necessarios.items():
            nome_insumo = obter_nome_insumo(insumo_id)
            st.write(f'{nome_insumo} - {quantidade} kg')

    if st.button('Excluir Todos os Pedidos'):
        excluir_pedidos()
        st.success('Todos os pedidos foram excluídos com sucesso!')

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
        df['Quantidade'] = df['Quantidade'].round(2)  # Arredonda a quantidade para duas casas decimais
        st.write(df)

        if st.button('Limpar Receitas'):
            limpar_receitas()
            st.success('Receitas limpas com sucesso!')

def obter_nomes_receitas():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT nome FROM receitas')
    data = c.fetchall()
    conn.close()
    return [nome[0] for nome in data]


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
            quantidade_total = quantidade_por_receita * num_receitas
            c.execute('UPDATE insumos SET quantidade = quantidade - ? WHERE id = ?', (quantidade_total, insumo_id))

        # Adicionar a quantidade produzida à quantidade do insumo na tabela de insumos
        c.execute('UPDATE insumos SET quantidade = quantidade + ? WHERE nome = ?', (quantidade_produzida, nome_receita))

        conn.commit()
        conn.close()

        st.success(f'{num_receitas} receitas de {nome_receita} produzidas com sucesso!')


def obter_id_insumo(nome):
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT nome FROM insumos WHERE nome = ?', (nome,))
    insumo_id = c.fetchone()[0]
    conn.close()
    return insumo_id

def main():
    st.title('Controle de Estoque')

    operacao = st.sidebar.selectbox('Operação', ['Estoque', 'Cadastrar', 'Movimentações', 'Configurações', 'Pedidos'])

    if operacao == 'Estoque':
        sub_operacao = st.sidebar.selectbox('Estoque',['Estoque', 'Receitas'])
        if sub_operacao == 'Estoque':
            visualizar_estoque()
        if sub_operacao == 'Receitas':
            nome_receita = st.selectbox('Selecione a Receita', obter_nomes_receitas())
            visualizar_itens_receita(nome_receita)

    elif operacao == 'Cadastrar':
        sub_operacao = st.sidebar.selectbox('Cadastro', ['Cadastrar Insumo', 'Cadastrar Receita'])
        if sub_operacao == 'Cadastrar Insumo':
            nome = st.text_input('Nome do Insumo')
            quantidade = st.number_input('Quantidade', min_value=0.0, step=0.1)
            if st.button('Cadastrar'):
                cadastrar_insumo(nome, quantidade)
                st.success('Insumo cadastrado com sucesso!')
        elif sub_operacao == 'Cadastrar Receita':
            cadastrar_receita()

    elif operacao == 'Movimentações':
        sub_operacao = st.sidebar.selectbox('Movimentações', ['Registrar Entrada', 'Registrar Saída', 'Produzir Receita'])
        if sub_operacao == 'Registrar Entrada':
            nome = st.selectbox('Insumo', obter_nomes_insumos())
            quantidade = st.number_input('Quantidade', min_value=0.0, step=0.1)
            if st.button('Registrar'):
                entrada_insumo(nome, quantidade)
                st.success('Entrada registrada com sucesso!')
        elif sub_operacao == 'Registrar Saída':
            nome = st.selectbox('Insumo', obter_nomes_insumos())
            quantidade = st.number_input('Quantidade', min_value=0.0, step=0.1)
            if st.button('Registrar'):
                saida_insumo(nome, quantidade)
                st.success('Saída registrada com sucesso!')
        elif sub_operacao == 'Produzir Receita':
            produzir_receita()

    elif operacao == 'Configurações':
        sub_op = st.sidebar.selectbox('Configurações', ['Insumos','Receitas'])
        if sub_op == 'Insumos':
            visualizar_insumos()
        if sub_op == 'Receitas':
            visualizar_receitas()
    elif operacao == 'Pedidos':
        sub_op = st.sidebar.selectbox('Pedidos', ['Cadastrar Pedido','Gestão de Pedido', 'Excluir Todos os Pedidos'])
        if sub_op == 'Cadastrar Pedido':
            gestao_pedidos()
        elif sub_op == 'Gestão de Pedido':
            visualizar_insumos_necessarios()
        elif opcao_gestao_pedidos == 'Excluir Todos os Pedidos':
            if st.button('Excluir Todos os Pedidos'):
                excluir_pedidos()
                st.success('Todos os pedidos foram excluídos com sucesso!')

if __name__ == '__main__':
    main()



