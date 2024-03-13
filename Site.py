import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Carregar o arquivo Excel
df = pd.read_excel('C:/Program Files (x86)/SanPaolo/Base.Athenas.Novembro.xlsx', sheet_name='base athenas')

# Agrupar os dados pela regional e somar a quantidade de biscoitos produzidos
df_regional = df.groupby('ESTADO')['Quantidade da Produção'].sum().reset_index()

# Criar o gráfico de barras
fig, ax = plt.subplots()
ax.bar(df_regional['ESTADO'], df_regional['ESTADO'], color='skyblue')
ax.set_xlabel('ESTADO')
ax.set_ylabel('Quantidade da Produção')
ax.set_title('Produção de Biscoitos por Regional (Novembro)')
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()

# Mostrar o gráfico no Streamlit
st.pyplot(fig)

