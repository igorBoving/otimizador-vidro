import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from rectpack import newPacker

st.set_page_config(page_title="Otimizador de Corte de Vidro", layout="wide")

st.title("📐 Otimizador de Corte de Vidro")

arquivo = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

largura_chapa = st.number_input("Largura da chapa (mm)", value=2200)
altura_chapa = st.number_input("Altura da chapa (mm)", value=3210)


def expandir_pecas(df):
    return df.loc[df.index.repeat(df["quantidade"])].reset_index(drop=True)


def otimizar(df, largura_chapa, altura_chapa):

    packer = newPacker(rotation=True)

    for _, r in df.iterrows():
        packer.add_rect(r["largura"], r["altura"])

    packer.add_bin(largura_chapa, altura_chapa, float("inf"))

    packer.pack()

    return packer


def desenhar_chapa(packer, largura_chapa, altura_chapa, indice_chapa):

    fig, ax = plt.subplots()

    abin = packer[indice_chapa]

    for rect in abin:

        x = rect.x
        y = rect.y
        w = rect.width
        h = rect.height

        r = plt.Rectangle((x, y), w, h, fill=False)

        ax.add_patch(r)

        ax.text(
            x + w / 2,
            y + h / 2,
            f"{round(w)}x{round(h)}",
            ha="center",
            va="center",
            fontsize=8
        )

    ax.set_xlim(0, largura_chapa)
    ax.set_ylim(0, altura_chapa)

    ax.set_aspect('equal')

    return fig


if arquivo:

    df = pd.read_excel(arquivo)

    st.subheader("Planilha carregada")
    st.dataframe(df)

    df = expandir_pecas(df)

    packer = otimizar(df, largura_chapa, altura_chapa)

    chapas = len(packer)

    area_chapa = largura_chapa * altura_chapa
    area_total = (df["largura"] * df["altura"]).sum()

    sucata = chapas * area_chapa - area_total
    sucata_percent = sucata / (chapas * area_chapa) * 100

    st.subheader("Resultado")

    col1, col2 = st.columns(2)

    col1.metric("Chapas necessárias", chapas)
    col2.metric("Sucata %", round(sucata_percent, 2))

    st.subheader("Visualização das chapas")

    indice = st.number_input(
        "Escolher chapa",
        min_value=0,
        max_value=chapas - 1,
        value=0
    )

    if st.button("Mostrar layout"):

        fig = desenhar_chapa(packer, largura_chapa, altura_chapa, indice)

        st.pyplot(fig)
