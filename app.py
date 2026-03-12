import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from rectpack import newPacker
import numpy as np
import random

st.set_page_config(layout="wide")

# -----------------------------
# CARREGAR DADOS
# -----------------------------

produtos=pd.read_csv("produtos.csv")
chapas=pd.read_csv("chapas.csv")

# -----------------------------
# EXPLODIR PORTAS
# -----------------------------

def explodir(pedido):

    vidros=[]

    for _,p in pedido.iterrows():

        porta=p["porta"]
        qtd=p["quantidade"]

        comp=produtos[produtos["porta"]==porta]

        for _,c in comp.iterrows():

            qtd_vidro=qtd*c["quantidade"]

            vidros.append({
                "codigo":c["vidro_codigo"],
                "tipo":c["tipo_vidro"],
                "largura":c["largura"],
                "altura":c["altura"],
                "quantidade":qtd_vidro
            })

    return pd.DataFrame(vidros)

# -----------------------------
# OTIMIZAÇÃO INDUSTRIAL
# -----------------------------

def otimizar(df,largura,altura,tentativas=200):

    melhor=None
    melhor_sucata=999

    area_chapa=largura*altura

    for t in range(tentativas):

        packer=newPacker(rotation=True)

        df2=df.sample(frac=1)

        for _,r in df2.iterrows():

            for i in range(int(r["quantidade"])):

                packer.add_rect(
                    r["largura"],
                    r["altura"],
                    rid=r["codigo"]
                )

        packer.add_bin(largura,altura,float("inf"))

        packer.pack()

        chapas=len(packer)

        area_vidros=0

        for _,r in df.iterrows():

            area_vidros+=(
                r["largura"]*
                r["altura"]*
                r["quantidade"]
            )

        area_total=chapas*area_chapa

        sucata=1-(area_vidros/area_total)

        if sucata<melhor_sucata:

            melhor_sucata=sucata
            melhor=packer

    return melhor,melhor_sucata

# -----------------------------
# DESENHAR CHAPA
# -----------------------------

def desenhar(packer,largura,altura,indice):

    fig,ax=plt.subplots(figsize=(8,4))

    abin=packer[indice]

    for rect in abin:

        x=rect.x
        y=rect.y
        w=rect.width
        h=rect.height

        cor=np.random.rand(3,)

        r=plt.Rectangle(
            (x,y),
            w,
            h,
            facecolor=cor,
            edgecolor="black"
        )

        ax.add_patch(r)

        ax.text(
            x+w/2,
            y+h/2,
            rect.rid,
            ha="center",
            va="center",
            fontsize=8
        )

    ax.set_xlim(0,largura)
    ax.set_ylim(0,altura)

    ax.set_title("Layout da chapa")

    ax.set_aspect("equal")

    return fig

# -----------------------------
# INTERFACE
# -----------------------------

st.title("🏭 Otimizador Industrial de Corte de Vidro")

aba1,aba2,aba3=st.tabs([
"Produção",
"Cadastrar Porta",
"Produtos"
])

# -----------------------------
# PRODUÇÃO
# -----------------------------

with aba1:

    st.header("Pedido de produção")

    if "pedido" not in st.session_state:

        st.session_state.pedido=[]

    porta=st.number_input(
        "Código da porta",
        step=1
    )

    qtd=st.number_input(
        "Quantidade",
        step=1
    )

    if st.button("Adicionar pedido"):

        st.session_state.pedido.append({
            "porta":porta,
            "quantidade":qtd
        })

    pedido_df=pd.DataFrame(
        st.session_state.pedido
    )

    st.subheader("Lote atual")

    st.dataframe(pedido_df)

    if st.button("Calcular produção"):

        vidros=explodir(pedido_df)

        st.subheader("Vidros necessários")

        st.dataframe(vidros)

        for _,ch in chapas.iterrows():

            tipo=ch["tipo"]

            largura=ch["largura"]
            altura=ch["altura"]

            df_tipo=vidros[
                vidros["tipo"]==tipo
            ]

            if len(df_tipo)==0:
                continue

            st.subheader(
                f"Otimização {tipo}"
            )

            packer,sucata=otimizar(
                df_tipo,
                largura,
                altura,
                300
            )

            st.write(
                "Chapas necessárias:",
                len(packer)
            )

            st.write(
                "Sucata:",
                round(sucata*100,2),
                "%"
            )

            indice=st.slider(
                f"Chapa {tipo}",
                0,
                len(packer)-1,
                0
            )

            fig=desenhar(
                packer,
                largura,
                altura,
                indice
            )

            st.pyplot(fig)

# -----------------------------
# CADASTRO
# -----------------------------

with aba2:

    st.header("Cadastrar porta")

    porta=st.number_input(
        "Código da porta",
        step=1,
        key="cad"
    )

    tipo=st.selectbox(
        "Tipo",
        ["simples","duplo","triplo"]
    )

    dados=[]

    if tipo=="simples":

        vidro=st.selectbox(
            "tipo vidro",
            ["insulado","tek"]
        )

        largura=st.number_input(
            "largura"
        )

        altura=st.number_input(
            "altura"
        )

        if st.button("Salvar"):

            dados.append([
                porta,
                porta*10+1,
                vidro,
                largura,
                altura,
                1
            ])

    if tipo=="duplo":

        st.write("vidro insulado")

        l1=st.number_input("largura1")
        a1=st.number_input("altura1")

        st.write("vidro tek")

        l2=st.number_input("largura2")
        a2=st.number_input("altura2")

        if st.button("Salvar"):

            dados.append([
                porta,
                porta*10+1,
                "insulado",
                l1,
                a1,
                1
            ])

            dados.append([
                porta,
                porta*10+2,
                "tek",
                l2,
                a2,
                1
            ])

    if tipo=="triplo":

        st.write("2 vidros insulados")

        l1=st.number_input("largura1")
        a1=st.number_input("altura1")

        l2=st.number_input("largura2")
        a2=st.number_input("altura2")

        st.write("vidro tek")

        l3=st.number_input("largura3")
        a3=st.number_input("altura3")

        if st.button("Salvar"):

            dados.append([
                porta,
                porta*10+1,
                "insulado",
                l1,
                a1,
                1
            ])

            dados.append([
                porta,
                porta*10+2,
                "insulado",
                l2,
                a2,
                1
            ])

            dados.append([
                porta,
                porta*10+3,
                "tek",
                l3,
                a3,
                1
            ])

    if len(dados)>0:

        df=pd.DataFrame(
            dados,
            columns=[
                "porta",
                "vidro_codigo",
                "tipo_vidro",
                "largura",
                "altura",
                "quantidade"
            ]
        )

        produtos2=pd.concat(
            [produtos,df]
        )

        produtos2.to_csv(
            "produtos.csv",
            index=False
        )

        st.success("Porta cadastrada")

# -----------------------------
# PRODUTOS
# -----------------------------

with aba3:

    st.header("Produtos cadastrados")

    st.dataframe(produtos)
