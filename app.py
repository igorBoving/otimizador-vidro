import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Otimizador de Corte de Vidro")

arquivo = st.file_uploader("Envie o Excel com as portas", type=["xlsx"])

largura_chapa = st.number_input("Largura da chapa (mm)", value=2200)
altura_chapa = st.number_input("Altura da chapa (mm)", value=3210)

if arquivo:
    df = pd.read_excel(arquivo)

    st.write("Dados carregados")
    st.dataframe(df)

    df["area"] = df["largura"] * df["altura"]

    area_total = df["area"].sum()
    area_chapa = largura_chapa * altura_chapa

    sucata = area_chapa - area_total
    sucata_percent = (sucata / area_chapa) * 100

    st.write("Área da chapa:", area_chapa)
    st.write("Área usada:", area_total)
    st.write("Sucata:", sucata)
    st.write("Sucata %:", round(sucata_percent,2))
