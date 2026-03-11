import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="Otimizador de Corte de Vidro", layout="wide")

st.title("📐 Otimizador de Corte de Vidro")

arquivo = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

largura_chapa = st.number_input("Largura da chapa (mm)", value=2200)
altura_chapa = st.number_input("Altura da chapa (mm)", value=3210)

tentativas = st.slider("Número de simulações", 100, 10000, 2000)

def expandir_pecas(df):
    return df.loc[df.index.repeat(df["quantidade"])].reset_index(drop=True)

def desenhar_layout(df, largura_chapa, altura_chapa):

    fig, ax = plt.subplots()

    x = 0
    y = 0
    linha_altura = 0

    for _, r in df.iterrows():

        w = r["largura"]
        h = r["altura"]

        if x + w > largura_chapa:
            x = 0
            y += linha_altura
            linha_altura = 0

        rect = plt.Rectangle((x,y), w, h, fill=False)
        ax.add_patch(rect)

        x += w
        linha_altura = max(linha_altura, h)

    ax.set_xlim(0, largura_chapa)
    ax.set_ylim(0, altura_chapa)

    ax.set_aspect('equal')

    return fig


def calcular_layout(df, largura_chapa, altura_chapa):

    x = 0
    y = 0
    linha_altura = 0
    chapas = 1

    for _, r in df.iterrows():

        w = r["largura"]
        h = r["altura"]

        if x + w > largura_chapa:

            x = 0
            y += linha_altura
            linha_altura = 0

        if y + h > altura_chapa:

            chapas += 1
            x = 0
            y = 0
            linha_altura = 0

        x += w
        linha_altura = max(linha_altura, h)

    return chapas


if arquivo:

    df = pd.read_excel(arquivo)

    st.subheader("Planilha carregada")
    st.dataframe(df)

    df = expandir_pecas(df)

    melhor_chapas = 999999
    melhor_layout = None

    for i in range(tentativas):

        df_random = df.sample(frac=1)

        chapas = calcular_layout(df_random, largura_chapa, altura_chapa)

        if chapas < melhor_chapas:

            melhor_chapas = chapas
            melhor_layout = df_random

    st.subheader("Resultado otimizado")

    st.metric("Chapas necessárias", melhor_chapas)

    area_chapa = largura_chapa * altura_chapa
    area_total = (df["largura"] * df["altura"]).sum()

    sucata = melhor_chapas * area_chapa - area_total
    sucata_percent = sucata / (melhor_chapas * area_chapa) * 100

    st.metric("Sucata %", round(sucata_percent,2))

    if st.button("Mostrar melhor layout"):

        fig = desenhar_layout(melhor_layout, largura_chapa, altura_chapa)

        st.pyplot(fig)
