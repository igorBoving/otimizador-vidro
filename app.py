import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from rectpack import newPacker

st.set_page_config(layout="wide")

# =========================
# CRIAR BASES SE NÃO EXISTIR
# =========================

if not os.path.exists("produtos.csv"):
    pd.DataFrame(columns=[
        "porta","vidro_codigo","tipo_vidro",
        "espessura","largura","altura","quantidade"
    ]).to_csv("produtos.csv",index=False)

if not os.path.exists("chapas.csv"):
    pd.DataFrame(columns=[
        "tipo","espessura","largura","altura"
    ]).to_csv("chapas.csv",index=False)

produtos=pd.read_csv("produtos.csv")
chapas=pd.read_csv("chapas.csv")

# =========================
# FUNÇÃO EXPLODIR PORTAS
# =========================

def explodir(pedido):

    vidros=[]

    for _,p in pedido.iterrows():

        comp=produtos[
            produtos["porta"]==p["porta"]
        ]

        for _,c in comp.iterrows():

            vidros.append({
                "codigo":c["vidro_codigo"],
                "tipo":c["tipo_vidro"],
                "espessura":c["espessura"],
                "largura":c["largura"],
                "altura":c["altura"],
                "quantidade":p["quantidade"]*c["quantidade"]
            })

    df=pd.DataFrame(vidros)

    if len(df)==0:
        return df

    df=df.groupby(
        ["codigo","tipo","espessura","largura","altura"],
        as_index=False
    ).sum()

    return df


# =========================
# OTIMIZAÇÃO
# =========================

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

    area_chapa=w*h

    area_vidro=0

    for _,r in df.iterrows():

        area_vidro+=(
            r["largura"]*
            r["altura"]*
            r["quantidade"]
        )

    chapas_usadas=len(packer)

    if chapas_usadas==0:
        return packer,0

    area_total=chapas_usadas*area_chapa

    sucata=1-(area_vidro/area_total)

    return packer,sucata


# =========================
# DESENHAR CHAPA
# =========================

def desenhar(packer,w,h,i):

    fig,ax=plt.subplots(figsize=(10,5))

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
            fontsize=7
        )

    ax.set_xlim(0,w)
    ax.set_ylim(0,h)
    ax.set_aspect("equal")

    return fig


# =========================
# INTERFACE
# =========================

st.title("Sistema de Otimização de Corte de Vidro")

aba1,aba2,aba3,aba4=st.tabs([
"Produção",
"Cadastrar Porta",
"Produtos",
"Cadastrar Chapas"
])

# =========================
# PRODUÇÃO
# =========================

with aba1:

    st.header("Produção")

    if "lote" not in st.session_state:
        st.session_state.lote=[]

    col1,col2,col3=st.columns(3)

    with col1:
        porta=st.number_input(
            "Código da porta",
            step=1,
            key="porta_producao"
        )

    with col2:
        qtd=st.number_input(
            "Quantidade",
            step=1,
            key="quantidade_producao"
        )

    with col3:
        if st.button("Adicionar ao lote",key="btn_add_lote"):

            st.session_state.lote.append({
                "porta":porta,
                "quantidade":qtd
            })

    lote_df=pd.DataFrame(st.session_state.lote)

    st.dataframe(lote_df)

    if st.button("Limpar lote",key="limpar_lote"):

        st.session_state.lote=[]

    if st.button("Calcular corte",key="calcular_corte"):

        vidros=explodir(lote_df)

        if len(vidros)==0:
            st.warning("Nenhum vidro encontrado")
        else:

            for _,c in chapas.iterrows():

                tipo=c["tipo"]
                esp=c["espessura"]

                df=vidros[
                    (vidros["tipo"]==tipo)&
                    (vidros["espessura"]==esp)
                ]

                if len(df)==0:
                    continue

                packer,sucata=otimizar(
                    df,
                    c["largura"],
                    c["altura"]
                )

                st.subheader(f"{tipo} {esp}mm")

                st.write("Chapas usadas:",len(packer))
                st.write("Sucata:",round(sucata*100,2),"%")

                if len(packer)>0:

                    i=st.slider(
                        "Ver chapa",
                        0,
                        len(packer)-1,
                        0,
                        key=f"slider_{tipo}_{esp}"
                    )

                    fig=desenhar(
                        packer,
                        c["largura"],
                        c["altura"],
                        i
                    )

                    st.pyplot(fig)


# =========================
# CADASTRAR PORTA
# =========================

with aba2:

    st.header("Cadastrar porta")

    porta=st.number_input(
        "Código da porta",
        step=1,
        key="porta_cadastro"
    )

    tipo_porta=st.selectbox(
        "Tipo da porta",
        ["simples","dupla","tripla"],
        key="tipo_porta"
    )

    largura=st.number_input(
        "Largura vidro",
        key="largura_vidro"
    )

    altura=st.number_input(
        "Altura vidro",
        key="altura_vidro"
    )

    esp=st.selectbox(
        "Espessura",
        [4,6,8],
        key="esp_vidro"
    )

    if st.button("Salvar porta",key="salvar_porta"):

        linhas=[]

        if tipo_porta=="simples":

            linhas.append([
                porta,f"{porta}_1",
                "incolor",
                esp,
                largura,
                altura,
                1
            ])

        if tipo_porta=="dupla":

            linhas.append([
                porta,f"{porta}_INC",
                "incolor",
                esp,
                largura,
                altura,
                1
            ])

            linhas.append([
                porta,f"{porta}_TEK",
                "tek",
                esp,
                largura,
                altura,
                1
            ])

        if tipo_porta=="tripla":

            linhas.append([
                porta,f"{porta}_INC1",
                "incolor",
                esp,
                largura,
                altura,
                1
            ])

            linhas.append([
                porta,f"{porta}_INC2",
                "incolor",
                esp,
                largura,
                altura,
                1
            ])

            linhas.append([
                porta,f"{porta}_TEK",
                "tek",
                esp,
                largura,
                altura,
                1
            ])

        novo=pd.DataFrame(
            linhas,
            columns=[
                "porta",
                "vidro_codigo",
                "tipo_vidro",
                "espessura",
                "largura",
                "altura",
                "quantidade"
            ]
        )

        produtos2=pd.concat([produtos,novo])

        produtos2.to_csv(
            "produtos.csv",
            index=False
        )

        st.success("Porta cadastrada")


# =========================
# VER PRODUTOS
# =========================

with aba3:

    st.header("Produtos cadastrados")

    st.dataframe(produtos)


# =========================
# CADASTRAR CHAPAS
# =========================

with aba4:

    st.header("Cadastrar chapas")

    tipo=st.selectbox(
        "Tipo vidro",
        ["incolor","tek"],
        key="tipo_chapa"
    )

    esp=st.selectbox(
        "Espessura",
        [4,6,8],
        key="esp_chapa"
    )

    largura=st.number_input(
        "Largura chapa",
        key="largura_chapa"
    )

    altura=st.number_input(
        "Altura chapa",
        key="altura_chapa"
    )

    if st.button("Salvar chapa",key="salvar_chapa"):

        nova=pd.DataFrame([[
            tipo,
            esp,
            largura,
            altura
        ]],columns=[
            "tipo",
            "espessura",
            "largura",
            "altura"
        ])

        chapas2=pd.concat([chapas,nova])

        chapas2.to_csv(
            "chapas.csv",
            index=False
        )

        st.success("Chapa cadastrada")

    st.subheader("Chapas cadastradas")

    st.dataframe(chapas)
