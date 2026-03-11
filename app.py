import streamlit as st
import pandas as pd
import os

ARQUIVO = "estrutura_produto.csv"


# ----------------------------
# BANCO DE DADOS
# ----------------------------

def carregar():

    if os.path.exists(ARQUIVO):
        return pd.read_csv(ARQUIVO)

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


# ----------------------------
# EXPLODIR PORTAS → VIDROS
# ----------------------------

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


# ----------------------------
# APP
# ----------------------------

st.title("📐 Otimizador de Corte de Vidro")

estrutura = carregar()

aba1, aba2, aba3 = st.tabs([
    "Produção",
    "Cadastrar Porta",
    "Gerenciar Itens"
])

# ----------------------------
# PRODUÇÃO
# ----------------------------

with aba1:

    st.header("Pedido de produção")

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

        normal = vidros[vidros["tipo"] == "normal"]
        tek = vidros[vidros["tipo"] == "tek"]

        st.subheader("Resumo")

        st.write("Vidros normais:", normal["quantidade"].sum())
        st.write("Vidros tek:", tek["quantidade"].sum())


# ----------------------------
# CADASTRAR PORTA
# ----------------------------

with aba2:

    st.header("Cadastrar porta")

    porta = st.number_input("Código do pacote")

    tipo = st.selectbox(
        "Tipo de porta",
        ["Simples", "Duplo", "Triplo"]
    )

    novos = []

    if tipo == "Simples":

        tipo_vidro = st.selectbox("Tipo vidro", ["normal", "tek"])

        largura = st.number_input("largura")

        altura = st.number_input("altura")

        if st.button("Salvar porta"):

            novos.append({
                "porta": porta,
                "vidro_codigo": porta*10+1,
                "tipo_vidro": tipo_vidro,
                "largura": largura,
                "altura": altura,
                "quantidade": 1
            })


    if tipo == "Duplo":

        st.write("Vidro normal")

        largura1 = st.number_input("largura normal")
        altura1 = st.number_input("altura normal")

        st.write("Vidro tek")

        largura2 = st.number_input("largura tek")
        altura2 = st.number_input("altura tek")

        if st.button("Salvar porta"):

            novos.append({
                "porta": porta,
                "vidro_codigo": porta*10+1,
                "tipo_vidro": "normal",
                "largura": largura1,
                "altura": altura1,
                "quantidade": 1
            })

            novos.append({
                "porta": porta,
                "vidro_codigo": porta*10+2,
                "tipo_vidro": "tek",
                "largura": largura2,
                "altura": altura2,
                "quantidade": 1
            })


    if tipo == "Triplo":

        st.write("Vidro normal 1")

        largura1 = st.number_input("largura normal 1")
        altura1 = st.number_input("altura normal 1")

        st.write("Vidro normal 2")

        largura2 = st.number_input("largura normal 2")
        altura2 = st.number_input("altura normal 2")

        st.write("Vidro tek")

        largura3 = st.number_input("largura tek")
        altura3 = st.number_input("altura tek")

        if st.button("Salvar porta"):

            novos.append({
                "porta": porta,
                "vidro_codigo": porta*10+1,
                "tipo_vidro": "normal",
                "largura": largura1,
                "altura": altura1,
                "quantidade": 1
            })

            novos.append({
                "porta": porta,
                "vidro_codigo": porta*10+2,
                "tipo_vidro": "normal",
                "largura": largura2,
                "altura": altura2,
                "quantidade": 1
            })

            novos.append({
                "porta": porta,
                "vidro_codigo": porta*10+3,
                "tipo_vidro": "tek",
                "largura": largura3,
                "altura": altura3,
                "quantidade": 1
            })


    if len(novos) > 0:

        estrutura = pd.concat([estrutura, pd.DataFrame(novos)])

        salvar(estrutura)

        st.success("Porta cadastrada!")


# ----------------------------
# GERENCIAR
# ----------------------------

with aba3:

    st.header("Itens cadastrados")

    st.dataframe(estrutura)

    codigo = st.number_input("Código da porta para excluir")

    if st.button("Excluir porta"):

        estrutura = estrutura[estrutura["porta"] != codigo]

        salvar(estrutura)

        st.success("Porta removida!")
