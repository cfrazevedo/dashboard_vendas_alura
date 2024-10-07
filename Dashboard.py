import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# Criando Tabelas
## Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## Quantidade de vendas

venda_estados = dados.groupby('Local da compra')[['Local da compra']].count()
venda_estados.columns = ['Vendas']
venda_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(venda_estados, left_on='Local da compra', right_index=True).sort_values('Vendas', ascending=False)
venda_estados.reset_index(inplace=True, drop=True)

venda_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count().reset_index()
venda_mensal = venda_mensal.rename(columns={'Preço': 'Vendas'})
venda_mensal['Ano'] = venda_mensal['Data da Compra'].dt.year
venda_mensal['Mês'] = venda_mensal['Data da Compra'].dt.month_name()

venda_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)
venda_categorias.columns = ['Vendas']

## Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# Criando Gráficos
## Receita
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por estado') 

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal'
                             )
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                                x = 'Local da compra',
                                y = 'Preço',
                                text_auto = True,
                                title = 'Top estados (receitas)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## Quantidade de vendas
fig_mapa_venda = px.scatter_geo(venda_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Vendas',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Vendas por estado') 

fig_venda_mensal = px.line(venda_mensal,
                             x = 'Mês',
                             y = 'Vendas',
                             markers = True,
                             range_y = (0, venda_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Vendas mensais'
                             )
fig_venda_mensal.update_layout(yaxis_title = 'Vendas')

fig_venda_estados = px.bar(venda_estados.head(),
                                x = 'Local da compra',
                                y = 'Vendas',
                                text_auto = True,
                                title = 'Top estados (receitas)')
fig_venda_estados.update_layout(yaxis_title = 'Vendas')

fig_venda_categorias = px.bar(venda_categorias,
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_venda_categorias.update_layout(yaxis_title = 'Receita')

# VIsualização no Streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendendores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_venda, use_container_width=True)
        st.plotly_chart(fig_venda_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_venda_mensal, use_container_width=True)
        st.plotly_chart(fig_venda_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False ).head(qtd_vendedores),
                                    x = 'sum',
                                    y = vendedores[['sum']].sort_values('sum', ascending=False ).head(qtd_vendedores).index,
                                    text_auto = True,
                                    title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_venda_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False ).head(qtd_vendedores),
                                    x = 'count',
                                    y = vendedores[['count']].sort_values('count', ascending=False ).head(qtd_vendedores).index,
                                    text_auto = True,
                                    title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_venda_vendedores)
        


st.dataframe(dados)