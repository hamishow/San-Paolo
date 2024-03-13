import streamlit as st

st.title('Meu Primeiro Aplicativo Streamlit')
st.write("Aqui está um DataFrame de exemplo:")

import pandas as pd
df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [10, 15, 13, 17, 19]
})

st.write(df)
