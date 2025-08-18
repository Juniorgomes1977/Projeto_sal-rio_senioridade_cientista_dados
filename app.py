import pandas as pd
import streamlit as st
import plotly.express as px

# __ Configurações da pagina __
# Define o título da página, o icone e layout para ocupar a largura inteira
st.set_page_config(
    page_title="Dashboard de Análise de salários na Área de Dados", 
    page_icon=":bar_chart:", 
    layout="wide"
    )

# __ Carregamento dos dados __
# Carrega os dados de um arquivo CSV
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# __ Barras lateral (filtros) __
# Cria um filtro para selecionar o cargo
st.sidebar.header("Filtros")

# Filtros dos anos
anos_disponiveis = sorted(df["ano"].unique()) # pega o dataframe os dados anos (unicos)
anos_selecionados = st.sidebar.multiselect("Anos:", anos_disponiveis, default=anos_disponiveis)

# filtro de senioridades
senioridades_disponiveis = sorted(df["senioridade"].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade:", senioridades_disponiveis, default=senioridades_disponiveis)

# filtro por tipo de contrato
contratos_disponiveis = sorted(df["contrato"].unique())
contratos_selecionados = st.sidebar.multiselect("Tipos de Contrato:", contratos_disponiveis, default=contratos_disponiveis)

# filtro por tamanho da empresa
tamanhos_disponiveis = sorted(df["tamanho_empresa"].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa:", tamanhos_disponiveis, default=tamanhos_disponiveis)

# __ Filtragem do dataframe __
# O dataframe principal é filtrado com base nos seletores da barra lateral
df_filtrado = df[
    (df["ano"].isin(anos_selecionados)) &
    (df["senioridade"].isin(senioridades_selecionadas)) &
    (df["contrato"].isin(contratos_selecionados)) &
    (df["tamanho_empresa"].isin(tamanhos_selecionados))
]

# __ Conteúdo principal __
st.title("Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados de salários na área de dados, nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# __ Metricas Principais (KPIs) __
st.subheader("Métricas Gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado["usd"].mean()
    salario_maximo = df_filtrado["usd"].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:  
    salario_medio, salario_madiano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"US${salario_medio:.2f}")
col2.metric("Salário Máximo", f"US${salario_maximo:.2f}")
col3.metric("Total de Registros", total_registros)
col4.metric("Cargo Mais Comum", cargo_mais_frequente)


st.markdown("---")

# __ Análise visual com plotly __
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby("cargo")["usd"].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 Cargos por Salário Médio',
            labels={'usd': "Média salarial anual (usd)", 'cargo': ""}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")
        
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            title='Distribuição dos Salários Anuais',
            labels={'usd': "Faixa Salarial (usd)", 'count': ""}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
       remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
       remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
       grafico_remoto = px.pie(
           remoto_contagem,
           names='tipo_trabalho',
           values='quantidade',
           title='Proporção dos tipos de trabalho',
           hole=0.5
       )
       grafico_remoto.update_traces( textinfo='percent+label')
       grafico_remoto.update_layout(title_x=0.1)
       st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
       st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Science']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            locationmode='ISO-3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário Médio de Ciêntista de Dados por País',
            labels={'usd': "Salário Médio (USD)", 'residencia_iso3': "País"}
        )
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de país.")
        
# __ Tabela de dados detalhados __
st.subheader("Tabela de Dados Detalhados")
st.dataframe(df_filtrado)
