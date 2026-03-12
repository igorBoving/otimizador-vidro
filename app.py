import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from rectpack import newPacker
import os
import random

ARQUIVO="estrutura_produto.csv"

# -----------------------
# BANCO DE DADOS
# -----------------------

def carregar():

    if os.path.exists(ARQUIVO):

        return pd.read_csv(ARQUIVO)

    df=pd.DataFrame(columns=[
        "porta",
        "vidro_codigo",
        "tipo_vidro",
        "largura",
        "altura",
        "quantidade"
    ])

    df.to_csv(ARQUIVO,index=False)

    return df


def salvar(df):

    df.to_csv(ARQUIVO,index=False)

# -----------------------
# EXPLODIR PORTAS
# -----------------------

def explodir_portas(pedido,estrutura):

    vidros=[]

    for _,p in pedido.iterrows():

        porta=p["porta"]
        qtd=p["quantidade"]

        comp=estrutura[estrutura["porta"]==porta]

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

# -----------------------
# OTIMIZAÇÃO
# -----------------------

def otimizar(df,largura,altura,tentativas=30):

    melhor=None
    menor_chapas=999999

    for t in range(tentativas):

        packer=newPacker(rotation=True)

        linhas=df.sample(frac=1)

        for _,r in linhas.iterrows():

            for i in range(int(r["quantidade"])):

                packer.add_rect(
                    r["largura"],
                    r["altura"],
                    rid=r["codigo"]
                )

        packer.add_bin(largura,altura,float("inf"))

        packer.pack()

        chapas=len(packer)

        if chapas<menor_chapas:

            menor_chapas=chapas
            melhor=packer

    return melhor

# -----------------------
# DESENHO CHAPA
# -----------------------

def desenhar(packer,largura,altura,indice):

    fig,ax=plt.subplots()

    abin=packer[indice]

    for rect in abin:

        x=rect.x
        y=rect.y
        w=rect.width
        h=rect.height

        r=plt.Rectangle((x,y),w,h,fill=False)

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

    ax.set_aspect('equal')

    return fig

# -----------------------
# APP
# -----------------------

st.title("📐 Otimizador de Corte de Vidro")

estrutura=carregar()

aba1,aba2,aba3=st.tabs([
"Produção",
"Cadastrar Porta",
"Gerenciar"
])

# -----------------------
# PRODUÇÃO
# -----------------------

with aba1:

    st.header("Lote de produçã
