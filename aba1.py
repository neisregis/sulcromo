import streamlit as st
import pandas as pd
from io import BytesIO

# Função para aplicar os filtros
def filtrar_dados(df, cliente, responsaveis, situacoes):
    if cliente:
        df = df[df['Cliente'].str.contains(cliente, case=False, na=False)]
    if responsaveis:
        df = df[df['Responsável Comercial'].isin(responsaveis)]
    if situacoes:
        df = df[df['Situação'].isin(situacoes)]
    return df

# Função para formatar dados para exibição
def formatar_dados_exibicao(df):
    colunas_data = ['Data Recebimento', 'Data Inicio OS', 'Data Fim OS', 'Data Orçamento', 'Data Solicitação', 
                    'Data Carteira', 'Data Faturamento', 'Data Devolução', 'Data Oficial Faturamento']
    for coluna in colunas_data:
        df[coluna] = pd.to_datetime(df[coluna], errors='coerce').dt.strftime('%d/%m/%Y')
    colunas_valor = ['Valor Bruto', 'Valor Líquido']
    for coluna in colunas_valor:
        df[coluna] = df[coluna].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) and isinstance(x, (int, float)) else x)
    return df

# Função para gerar o arquivo Excel a partir do dataframe
def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Consulta Carteira')
        for column in df:
            col_idx = df.columns.get_loc(column)
            writer.sheets['Consulta Carteira'].set_column(col_idx, col_idx, max(df[column].astype(str).map(len).max(), len(column)))
    output.seek(0)
    return output

# Função para exibir a Aba 1
def exibir_aba1(df):
    st.subheader("Filtros e Resultados")

    col_filtros, col_tabela = st.columns([1, 4])

    with col_filtros:
        st.write("### Filtros")
        
        cliente = st.text_input("Cliente", "", key="cliente_aba1")
        responsaveis = st.multiselect("Responsável Comercial", options=df['Responsável Comercial'].unique(), key="responsaveis_aba1")
        situacoes = st.multiselect("Situação", options=df['Situação'].unique(), key="situacoes_aba1")

    with col_tabela:
        df_filtrado = filtrar_dados(df, cliente, responsaveis, situacoes)

        total_valor_bruto = df_filtrado['Valor Bruto'].sum()
        total_valor_liquido = df_filtrado['Valor Líquido'].sum()

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.metric('Total Valor Bruto', f'R$ {total_valor_bruto:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
        with col2:
            st.metric('Total Valor Líquido', f'R$ {total_valor_liquido:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
        with col3:
            excel_data = gerar_excel(df_filtrado)
            st.download_button(
                label="Exportar para Excel",
                data=excel_data,
                file_name='consulta_carteira_filtrada.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        df_filtrado_formatado = formatar_dados_exibicao(df_filtrado.copy())
        st.dataframe(df_filtrado_formatado, use_container_width=True)
