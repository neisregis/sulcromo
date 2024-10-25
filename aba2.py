import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Reutilizando as funções de filtro e exibição
from aba1 import filtrar_dados

# Função para formatar os valores monetários no padrão "R$ 1.000,00"
def formatar_valor_brasileiro(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para adicionar labels no final das barras, dependendo da orientação
def adicionar_labels(fig, orientation, df):
    if orientation == 'h':
        # Formatar os valores dos labels no padrão brasileiro
        fig.update_traces(texttemplate=df.apply(lambda x: formatar_valor_brasileiro(x['Valor Líquido']), axis=1), textposition='outside')
        fig.update_layout(yaxis={'autorange': 'reversed'})  # Garantir que os maiores valores fiquem no topo
    else:
        fig.update_traces(texttemplate=df.apply(lambda x: formatar_valor_brasileiro(x['Valor Líquido']), axis=1), textposition='outside')
    return fig

# Função para exibir a Aba 2 com filtros e gráficos dinâmicos
def exibir_aba2(df):
    st.subheader("Filtros e Gráficos")

    # Filtro de Mês/Ano da "Data Oficial Faturamento"
    df['Data Oficial Faturamento'] = pd.to_datetime(df['Data Oficial Faturamento'], errors='coerce')
    df = df.dropna(subset=['Data Oficial Faturamento'])
    meses_disponiveis = df['Data Oficial Faturamento'].dt.to_period('M').unique().strftime('%m/%Y')

    # Filtro padrão para o mês atual e os próximos meses
    mes_atual = datetime.now().strftime('%m/%Y')
    meses_filtrados = st.multiselect(
        "Mês (Data Oficial Faturamento)",
        options=meses_disponiveis,
        default=[mes for mes in meses_disponiveis if mes >= mes_atual]
    )

    col_filtros, col_tabela = st.columns([1, 4])  # Layout ajustado: 1 parte filtros, 4 partes gráficos

    with col_filtros:
        st.write("### Filtros")
        
        cliente = st.text_input("Cliente", "", key="cliente_aba2")
        responsaveis = st.multiselect("Responsável Comercial", options=df['Responsável Comercial'].dropna().unique(), key="responsaveis_aba2")  # Remover NaN
        situacoes = st.multiselect("Situação", options=df['Situação'].dropna().unique(), key="situacoes_aba2")  # Remover NaN

    with col_tabela:
        # Aplicar filtros de cliente, responsável e situação
        df_filtrado = filtrar_dados(df, cliente, responsaveis, situacoes)
    
        # Aplicar filtro de mês
        df_filtrado = df_filtrado[df_filtrado['Data Oficial Faturamento'].dt.strftime('%m/%Y').isin(meses_filtrados)]

        # Gráfico 1: Valor Líquido por Tipo de Orçamento
        grafico_tipo_orcamento = df_filtrado.groupby('Tipo Orçamento')['Valor Líquido'].sum().reset_index()
        grafico_tipo_orcamento = grafico_tipo_orcamento.sort_values(by='Valor Líquido', ascending=False)  # Ordenar do maior para o menor
        fig1 = px.bar(
            grafico_tipo_orcamento, 
            x='Valor Líquido', 
            y='Tipo Orçamento', 
            orientation='h', 
            title="Valor Líquido por Tipo de Orçamento",
            width=None, height=400
        )
        fig1 = adicionar_labels(fig1, 'h', grafico_tipo_orcamento)

        # Gráfico 2: Valor Líquido por Situação
        grafico_situacao = df_filtrado.groupby('Situação')['Valor Líquido'].sum().reset_index()
        grafico_situacao = grafico_situacao.sort_values(by='Valor Líquido', ascending=False)  # Ordenar do maior para o menor
        fig2 = px.bar(
            grafico_situacao, 
            x='Valor Líquido', 
            y='Situação', 
            orientation='h', 
            title="Valor Líquido por Situação",
            width=None, height=400
        )
        fig2 = adicionar_labels(fig2, 'h', grafico_situacao)

        # Gráfico 3: Valor Líquido por Cliente (limitar a 20 clientes e usar barra de rolagem)
        grafico_cliente = df_filtrado.groupby('Cliente')['Valor Líquido'].sum().reset_index()
        grafico_cliente = grafico_cliente.sort_values(by='Valor Líquido', ascending=False).head(20)  # Limitar a 20 clientes
        fig3 = px.bar(
            grafico_cliente, 
            x='Valor Líquido', 
            y='Cliente', 
            orientation='h', 
            title="Valor Líquido por Cliente (Top 20)",
            width=None, height=400
        )
        fig3 = adicionar_labels(fig3, 'h', grafico_cliente)

        # Gráfico 4: Valor Líquido por Mês/Ano (Data Oficial Faturamento)
        grafico_mes_ano = df_filtrado.groupby(df_filtrado['Data Oficial Faturamento'].dt.to_period('M'))['Valor Líquido'].sum().reset_index()
        grafico_mes_ano['Data Oficial Faturamento'] = grafico_mes_ano['Data Oficial Faturamento'].dt.strftime('%m/%Y')
        fig4 = px.bar(
            grafico_mes_ano, 
            x='Data Oficial Faturamento', 
            y='Valor Líquido', 
            title="Valor Líquido por Mês/Ano (Data Oficial Faturamento)",
            labels={'Data Oficial Faturamento': 'Mês/Ano'},
            width=None, height=400
        )
        fig4 = adicionar_labels(fig4, 'v', grafico_mes_ano)

        # Exibir os gráficos em uma grade 2x2 com keys únicos para cada gráfico
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True, key="grafico1")
            st.plotly_chart(fig3, use_container_width=True, key="grafico3")
        with col2:
            st.plotly_chart(fig2, use_container_width=True, key="grafico2")
            st.plotly_chart(fig4, use_container_width=True, key="grafico4")
