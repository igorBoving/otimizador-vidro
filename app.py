import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from rectpack import newPacker
import numpy as np
import os

st.set_page_config(layout="wide")

# -----------------------
# CRIAR CSV SE NÃO EXISTIR
# -----------------------

if not os.path.exists("produtos.csv"):
    df=pd.DataFrame(columns=[
        "porta","vidro_codigo",
        "tipo_vidro","largura",
        "altura","quantidade"
    ])
    df.to_csv("produtos.csv",index=False)

# -----------------------
# CARREGAR DADOS
# -----------------------

produtos=pd.read_csv("produtos.csv")
chapas=pd.read_csv("chapas.csv")

# -----------------------
# EXPLODIR PORTAS
# -----------------------

def explodir(pedido):

    vidros=[]

    for _,p in pedido.iterrows():

        porta=p["porta"]
        qtd=p["quantidade"]

        comp=produtos[produtos["porta"]==porta]

        for _,c in comp.iterrows():

            vidros.append({
                "codigo":c["vidro_codigo"],
                "tipo":c["tipo_vidro"],
                "largura":c["largura"],
                "altura":c["altura"],
                "quantidade":qtd*c["quantidade"]
            })

    return pd.DataFrame(vidros)

# -----------------------
# OTIMIZAÇÃO
# -----------------------

def otimizar(df,w,h):

    packer=newPacker(rotation=True)

    for _,r in df.iterrows():

        for i in range(int(r["quantidade"])):

            packer.add_rect(
                r["largura"],
                r["altura"],
                rid=r["codigo"]
            )

    packer.add_bin(w,h,float("inf"))

    packer.pack()

    return packer

# -----------------------
# DESENHAR CHAPA
# -----------------------

def desenhar(packer,w,h,i):

    fig,ax=plt.subplots(figsize=(8,4))

    abin=packer[i]

    for rect in abin:

        x=rect.x
        y=rect.y
        rw=rect.width
        rh=rect.height

        r=plt.Rectangle(
            (x,y),
            rw,
            rh,
            edgecolor="black",
            facecolor=np.random.rand(3,)
        )

        ax.add_patch(r)

        ax.text(
            x+rw/2,
            y+rh/2,
            rect.rid,
            ha="center",
            va="center",
            fontsize=8
        )

    ax.set_xlim(0,w)
    ax.set_ylim(0,h)
    ax.set_aspect("equal")

    return fig

# -----------------------
# INTERFACE
# -----------------------

st.title("🏭 Sistema Industrial de Corte de Vidro")

aba1,aba2,aba3,aba4=st.tabs([
"Produção",
"Produtos",
"Cadastrar",
"Importar Excel"
])

# -----------------------
# PRODUÇÃO
# -----------------------

with aba1:

    st.header("Simulação de produção")

    porta=st.number_input("porta",step=1)

    qtd=st.number_input("quantidade",step=1)

    if st.button("Calcular"):

        pedido=pd.DataFrame([{
            "porta":porta,
            "quantidade":qtd
        }])

        vidros=explodir(pedido)

        st.write("Vidros necessários")
        st.dataframe(vidros)

        for _,c in chapas.iterrows():

            tipo=c["tipo"]

            df=vidros[
                vidros["tipo"]==tipo
            ]

            if len(df)==0:
                continue

            packer=otimizar(
                df,
                c["largura"],
                c["altura"]
            )

            st.subheader(tipo)

            st.write(
                "chapas:",
                len(packer)
            )

            i=st.slider(
                "ver chapa",
                0,
                len(packer)-1,
                0
            )

            fig=desenhar(
                packer,
                c["largura"],
                c["altura"],
                i
            )

            st.pyplot(fig)

# -----------------------
# PRODUTOS
# -----------------------

with aba2:

    st.header("Produtos cadastrados")

    st.dataframe(produtos)

    porta_del=st.number_input(
        "codigo para excluir",
        step=1,
        key="del"
    )

    if st.button("Excluir"):

        produtos2=produtos[
            produtos["porta"]!=porta_del
        ]

        produtos2.to_csv(
            "produtos.csv",
            index=False
        )

        st.success("produto excluído")

# -----------------------
# CADASTRO
# -----------------------

with aba3:

    st.header("Cadastrar porta")

    porta=st.number_input(
        "codigo porta",
        step=1,
        key="cad"
    )

    tipo=st.selectbox(
        "tipo",
        ["simples","duplo","triplo"]
    )

    dados=[]

    if tipo=="simples":

        vidro=st.selectbox(
            "tipo vidro",
            ["insulado","tek"]
        )

        l=st.number_input("largura")
        a=st.number_input("altura")

        if st.button("Salvar"):

            dados.append([
                porta,
                porta*10+1,
                vidro,
                l,
                a,
                1
            ])

    if tipo=="duplo":

        st.write("insulado")

        l1=st.number_input("largura1")
        a1=st.number_input("altura1")

        st.write("tek")

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

        st.write("2 insulados")

        l1=st.number_input("largura1")
        a1=st.number_input("altura1")

        l2=st.number_input("largura2")
        a2=st.number_input("altura2")

        st.write("tek")

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

        st.success("porta cadastrada")

# -----------------------
# IMPORTAR EXCEL
# -----------------------

with aba4:

    st.header("Importar pedidos")

    file=st.file_uploader(
        "arquivo excel"
    )

    if file:

        df=pd.read_excel(file)

        st.dataframe(df)

        if st.button("calcular produção"):

            vidros=explodir(df)

            st.write(vidros)
