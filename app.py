import streamlit as st
import pandas as pd
from otimizador import otimizar_corte
from layout import desenhar_chapa
from historico import salvar_producao, carregar_historico

st.set_page_config(layout="wide")

st.title("Sistema de Otimização de Corte de Vidro")

menu = st.sidebar.selectbox(
"Menu",
[
"Otimização",
"Histórico produção"
]
)

if menu == "Otimização":

    arquivo = st.file_uploader("Enviar pedido Excel", type=["xlsx"])

    largura_chapa = st.number_input("Largura chapa", value=2200)
    altura_chapa = st.number_input("Altura chapa", value=3210)

    if arquivo:

        df = pd.read_excel(arquivo)

        df = df.loc[df.index.repeat(df["quantidade"])].reset_index(drop=True)

        packer = otimizar_corte(df, largura_chapa, altura_chapa)

        chapas = len(packer)

        area_chapa = largura_chapa * altura_chapa
        area_total = (df["largura"] * df["altura"]).sum()

        sucata = chapas * area_chapa - area_total
        sucata_percent = sucata / (chapas * area_chapa) * 100

        col1, col2 = st.columns(2)

        col1.metric("Chapas necessárias", chapas)
        col2.metric("Sucata %", round(sucata_percent,2))

        if st.button("Mostrar layout"):

            fig = desenhar_chapa(packer, largura_chapa, altura_chapa)

            st.pyplot(fig)

        if st.button("Salvar produção"):

            salvar_producao(
                {
                    "chapas": chapas,
                    "sucata_percent": sucata_percent
                }
            )

if menu == "Histórico produção":

    hist = carregar_historico()

    st.dataframe(hist)
