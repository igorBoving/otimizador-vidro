import streamlit as st
import pandas as pd
from cadastro import carregar_modelos, salvar_modelo
from otimizador import otimizar_corte
from layout import desenhar_chapa
from historico import salvar_hist, carregar_hist

st.set_page_config(layout="wide")

st.title("Sistema de Corte de Vidro")

menu = st.sidebar.selectbox(
"Menu",
[
"Cadastrar modelos",
"Otimização",
"Histórico"
]
)

if menu == "Cadastrar modelos":

    st.header("Cadastro de portas")

    codigo = st.text_input("Código da porta")

    largura = st.number_input("Largura")
    altura = st.number_input("Altura")

    if st.button("Salvar modelo"):

        salvar_modelo(codigo, largura, altura)

        st.success("Modelo salvo")

    st.subheader("Modelos cadastrados")

    df = carregar_modelos()

    st.dataframe(df)

# -----------------------

if menu == "Otimização":

    df_modelos = carregar_modelos()

    st.subheader("Selecionar portas")

    pedido = []

    for _, r in df_modelos.iterrows():

        qtd = st.number_input(
            f"{r['codigo']} ({r['largura']}x{r['altura']})",
            min_value=0,
            step=1
        )

        if qtd > 0:

            pedido.append({
                "codigo": r["codigo"],
                "largura": r["largura"],
                "altura": r["altura"],
                "quantidade": qtd
            })

    largura_chapa = st.number_input("Largura chapa", value=2200)
    altura_chapa = st.number_input("Altura chapa", value=3210)

    if st.button("Calcular corte"):

        df = pd.DataFrame(pedido)

        df = df.loc[df.index.repeat(df["quantidade"])].reset_index(drop=True)

        packer = otimizar_corte(df, largura_chapa, altura_chapa)

        chapas = len(packer)

        area_chapa = largura_chapa * altura_chapa
        area_total = (df["largura"] * df["altura"]).sum()

        sucata = chapas * area_chapa - area_total
        sucata_percent = sucata / (chapas * area_chapa) * 100

        st.metric("Chapas necessárias", chapas)
        st.metric("Sucata %", round(sucata_percent,2))

        indice = st.number_input(
            "Escolher chapa",
            0,
            chapas-1,
            0
        )

        fig = desenhar_chapa(packer, largura_chapa, altura_chapa, indice)

        st.pyplot(fig)

        salvar_hist({
            "chapas": chapas,
            "sucata": sucata_percent
        })

# -----------------------

if menu == "Histórico":

    st.header("Histórico de produção")

    hist = carregar_hist()

    st.dataframe(hist)
