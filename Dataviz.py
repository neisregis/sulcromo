import streamlit as st
import pandas as pd
from aba1 import exibir_aba1
from aba2 import exibir_aba2
import mysql.connector

# Função para obter dados do banco de dados
from config import config

# Função para obter dados a partir do banco de dados
def obter_dados():
    try:
        conexao = mysql.connector.connect(**config())  # Passa os parâmetros do dicionário corretamente
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM VW_CONSULTA_GERAL vc")
        resultados = cursor.fetchall()
        cursor.close()
        conexao.close()
        return resultados
    except Exception as e:
        st.error(f"Erro ao obter dados: {e}")
        return []

# Aplicação principal
def main():
    st.set_page_config(layout="wide")  # Define o layout para preencher toda a largura

    st.title('Consulta Carteira')

    # Obter dados da consulta
    dados = obter_dados()
    df = pd.DataFrame(dados, columns=[
        'Cliente', 'Tipo Orçamento', 'Peça', 'Rastreabilidade', 'Quantidade', 'Data Recebimento', 
        'Data Inicio OS', 'Data Fim OS', 'Valor Bruto', 'Valor Líquido', 'Responsável Comercial', 
        'Status OS', 'Numero NF', 'Codigo OS', 'Orçamento', 'Data Orçamento', 'Representante', 
        'OC Cliente', 'Situação', 'Setor', 'Tipo Faturamento', 'Data Solicitação', 'Data Carteira',
        'NF Faturamento', 'Data Faturamento', 'NF Devolução', 'Data Devolução', 'Data Oficial Faturamento'
    ])

    # Criar abas
    aba1, aba2 = st.tabs(["Faturamento e Tabela", "Gráfico por Responsável"])

    # Chamar a função para exibir a aba 1
    with aba1:
        exibir_aba1(df)

    # Chamar a função para exibir a aba 2
    with aba2:
        exibir_aba2(df)

if __name__ == "__main__":
    main()
