import streamlit as st
import requests
import pandas as pd
from time import sleep

@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = '✅')
    sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

for ntry in range(5):
    try:
        response = requests.get(url)
        dados = pd.DataFrame.from_dict(response.json())
        break
    except requests.exceptions.RequestException:
        sleep(3)

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

st. sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Categoria do produto'):
    categorias = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 250, (0,5000))
with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Selecione o frete', 0, 250, (0,250))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Nome do vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    estados = st.multiselect('Selecione os estados', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a nota', dados['Avaliação da compra'].min(), dados['Avaliação da compra'].max(),\
                      (dados['Avaliação da compra'].min(), dados['Avaliação da compra'].max()))
with st.sidebar.expander('Tipo de pagamento'):
    pagamento = st.multiselect('Selecione os tipos', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de parcelas'):
    parcelas = st.slider('Selecione os números', dados['Quantidade de parcelas'].min(), dados['Quantidade de parcelas'].max(),\
                      (dados['Quantidade de parcelas'].min(), dados['Quantidade de parcelas'].max()))

query = '''
Produto in @produtos &\
`Categoria do Produto` in @categorias &\
@preco[0] <= Preço <= @preco[1] &\
@frete[0] <= Frete <= @frete[1] &\
@data_compra[0] <= `Data da Compra` <= @data_compra[1] &\
Vendedor in @vendedores &\
`Local da compra` in @estados &\
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] &\
`Tipo de pagamento` in @pagamento &\
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1]
'''
dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em CSV', data=converte_csv(dados_filtrados), file_name=nome_arquivo, mime='text/csv', on_click=mensagem_sucesso)
