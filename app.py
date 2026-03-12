import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from rectpack import newPacker
import numpy as np
import random
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

    df=pd.DataFrame(vidros)

    df=df.groupby(
        ["codigo","tipo","largura","altura"],
        as_index=False
    ).sum()

    return df

# -----------------------
# OTIMIZAÇÃO INDUSTRIAL
# -----------------------

def otimizar(df,w,h,tentativas=1000):

    melhor=None
    melhor_sucata=999

    area_chapa=w*h

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

        packer.add_bin(w,h,float("inf"))

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

st.title("🏭 Otimizador Industrial de Corte de Vidro")

aba1,aba2,aba3,aba4=st.tabs([
"Produção",
"Produtos",
"Cadastrar",
"Importar Excel"
])

# -----------------------
# PRODUÇÃO COM LOTE
# -----------------------

with aba1:

    st.header("Lote de produção")

    if "lote" not in st.session_state:
        st.session_state.lote=[]

    col1,col2,col3=st.columns(3)

    with col1:
        porta=st.number_input("codigo porta",step=1)

    with col2:
        qtd=st.number_input("quantidade",step=1)

    with col3:
        if st.button("Adicionar ao lote"):

            st.session_state.lote.append({
                "porta":porta,
                "quantidade":qtd
            })

    lote_df=pd.DataFrame(st.session_state.lote)

    st.subheader("Lote atual")

    st.dataframe(lote_df)

    if st.button("Limpar lote"):
        st.session_state.lote=[]

    if st.button("Calcular lote"):

        vidros=explodir(lote_df)

        st.subheader("Vidros necessários")

        st.dataframe(vidros)

        for _,c in chapas.iterrows():

            tipo=c["tipo"]

            df=vidros[
                vidros["tipo"]==tipo
            ]

            if len(df)==0:
                continue

            st.subheader(f"Otimização {tipo}")

            packer,sucata=otimizar(
                df,
                c["largura"],
                c["altura"]
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

            i=st.slider(
                f"Ver chapa {tipo}",
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
        step=1
    )

    if st.button("Excluir produto"):

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

        if st.button("Salvar porta"):

            dados.append([
                porta,
                porta*10+1,
                vidro,
                l,
                a,
                1
            ])

    if tipo=="duplo":

        st.write("vidro insulado")

        l1=st.number_input("largura1")
        a1=st.number_input("altura1")

        st.write("vidro tek")

        l2=st.number_input("largura2")
        a2=st.number_input("altura2")

        if st.button("Salvar porta"):

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

        if st.button("Salvar porta"):

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

        if st.button("Adicionar ao lote"):

            for _,r in df.iterrows():

                st.session_state.lote.append({
                    "porta":r["porta"],
                    "quantidade":r["quantidade"]
                })

            st.success("Pedidos adicionados ao lote")
