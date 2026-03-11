import streamlit as st
import pandas as pd
import os

ARQUIVO = "estrutura_produto.csv"


def carregar():

    if os.path.exists(ARQUIVO):
        return pd.read_csv(ARQUIVO)

    else:
        df = pd.DataFrame(columns=[
            "porta",
            "vidro_codigo",
            "tipo_vidro",
            "largura",
            "altura",
            "quantidade"
        ])
        df.to_csv(ARQUIVO, index=False)
        return df


def salvar(df):
    df.to_csv(ARQUIVO, index=False)


def explodir_portas(pedido, estrutura):

    vidros = []

    for _, p in pedido.iterrows():

        porta = p["porta"]
        qtd_portas = p["quantidade"]

        comp = estrutura[estrutura["porta"] == porta]

        for _, c in comp.iterrows():

            qtd_vidro = qtd_portas * c["quantidade"]

            vidros.append({
                "codigo": c["vidro_codigo"],
                "tipo": c["tipo_vidro"],
                "largura": c["largura"],
                "altura": c["altura"],
                "quantidade": qtd_vidro
            })

    return pd.DataFrame(vidros)


st.title("📐 Otimizador de Corte de Vidro")

estrutura = carregar()

aba1, aba2, aba3 = st.tabs(["Produção", "Cadastrar Vidro", "Excluir"])

# -------------------
# PRODUÇÃO
# -------------------

with aba1:

    st.header("Pedido de portas")

    porta = st.number_input("Código da porta", step=1)

    qtd = st.number_input("Quantidade", step=1)

    if st.button("Calcular vidros"):

        pedido = pd.DataFrame({
            "porta": [porta],
            "quantidade": [qtd]
        })

        vidros = explodir_portas(pedido, estrutura)

        st.subheader("Vidros necessários")

        st.dataframe(vidros)

        insulado = vidros[vidros["tipo"] == "insulado"]

        tek = vidros[vidros["tipo"] == "tek"]

        st.subheader("Resumo")

        st.write("Insulado:", len(insulado))
        st.write("Tek:", len(tek))


# -------------------
# CADASTRAR
# -------------------

with aba2:

    st.header("Cadastrar novo vidro")

    porta = st.number_input("Código da porta", step=1, key="p")

    vidro = st.number_input("Código do vidro", step=1)

    tipo = st.selectbox("Tipo", ["insulado", "tek"])

    largura = st.number_input("Largura")

    altura = st.number_input("Altura")

    quantidade = st.number_input("Quantidade na porta", step=1)

    if st.button("Salvar vidro"):

        novo = pd.DataFrame({

            "porta": [porta],
            "vidro_codigo": [vidro],
            "tipo_vidro": [tipo],
            "largura": [largura],
            "altura": [altura],
            "quantidade": [quantidade]

        })

        estrutura = pd.concat([estrutura, novo])

        salvar(estrutura)

        st.success("Vidro cadastrado!")


# -------------------
# EXCLUIR
# -------------------

with aba3:

    st.header("Excluir item")

    st.dataframe(estrutura)

    codigo = st.number_input("Código do vidro para excluir")

    if st.button("Excluir"):

        estrutura = estrutura[estrutura["vidro_codigo"] != codigo]

        salvar(estrutura)

        st.success("Item removido!")
