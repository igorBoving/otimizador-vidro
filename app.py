import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="Otimizador de Corte de Vidro", layout="wide")

st.title("📐 Otimizador de Corte de Vidro")

arquivo = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

largura_chapa = st.number_input("Largura da chapa (mm)", value=2200)
altura_chapa = st.number_input("Altura da chapa (mm)", value=3210)

def expandir_pecas(df):
    df_expandido = df.loc[df.index.repeat(df["quantidade"])].reset_index(drop=True)
    return df_expandido

def calcular_area(df):
    df["area"] = df["largura"] * df["altura"]
    return df

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

if arquivo:

    df = pd.read_excel(arquivo)

    st.subheader("Planilha carregada")

    st.dataframe(df)

    df = expandir_pecas(df)

    df = calcular_area(df)

    area_total = df["area"].sum()

    area_chapa = largura_chapa * altura_chapa

    sucata = area_chapa - area_total

    sucata_percent = (sucata / area_chapa) * 100

    st.subheader("Resultado")

    col1, col2, col3 = st.columns(3)

    col1.metric("Área da chapa", round(area_chapa,2))
    col2.metric("Área usada", round(area_total,2))
    col3.metric("Sucata %", round(sucata_percent,2))

    if st.button("Gerar layout de corte"):

        df_random = df.sample(frac=1)

        fig = desenhar_layout(df_random, largura_chapa, altura_chapa)

        st.pyplot(fig)

