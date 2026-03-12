import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from rectpack import newPacker

st.set_page_config(layout="wide")

# =====================
# CRIAR ARQUIVOS
# =====================

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

# =====================
# EXPLODIR PORTAS
# =====================

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

    df=df.groupby(
        ["codigo","tipo","espessura","largura","altura"],
        as_index=False
    ).sum()

    return df


# =====================
# OTIMIZAÇÃO
# =====================

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

    area_total=chapas_usadas*area_chapa

    sucata=1-(area_vidro/area_total)

    return packer,sucata


# =====================
# DESENHAR CHAPA
# =====================

def desenhar(packer,w,h,i):

    fig,ax=plt.subplots(figsize=(9,4))

    abin=packer[i]

    for rect in abin:

        x=rect.x
        y=rect.y
        rw=rect.width
        rh=rect.height

        r=plt.Rectangle(
            (x,y),rw,rh,
            edgecolor="black",
            facecolor=np.random.rand(3,)
        )

        ax.add_patch(r)

        ax.text(
            x+rw/2,y+rh/2,
            rect.rid,
            ha="center",
            va="center",
            fontsize=7
        )

    ax.set_xlim(0,w)
    ax.set_ylim(0,h)

    ax.set_aspect("equal")

    return fig


# =====================
# INTERFACE
# =====================

st.title("Sistema Industrial de Corte de Vidro")

aba1,aba2,aba3,aba4,aba5,aba6,aba7=st.tabs([
"Produção",
"Cadastrar Porta",
"Produtos",
"Cadastrar Chapas",
"Importar Produtos",
"Importar Chapas",
"Importar Pedidos"
])

# =====================
# PRODUÇÃO
# =====================

with aba1:

    st.header("Lote de produção")

    if "lote" not in st.session_state:
        st.session_state.lote=[]

    col1,col2,col3=st.columns(3)

    with col1:
        porta=st.number_input("Código porta",step=1)

    with col2:
        qtd=st.number_input("Quantidade",step=1)

    with col3:
        if st.button("Adicionar ao lote"):
            st.session_state.lote.append({
                "porta":porta,
                "quantidade":qtd
            })

    lote_df=pd.DataFrame(st.session_state.lote)

    st.dataframe(lote_df)

    if st.button("Limpar lote"):
        st.session_state.lote=[]

    if st.button("Calcular corte"):

        vidros=explodir(lote_df)

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

            i=st.slider(
                f"Layout {tipo}{esp}",
                0,len(packer)-1,0
            )

            fig=desenhar(
                packer,
                c["largura"],
                c["altura"],
                i
            )

            st.pyplot(fig)


# =====================
# CADASTRAR PORTA
# =====================

with aba2:

    st.header("Cadastrar porta")

    porta=st.number_input("Código da porta",step=1)

    vidro_codigo=st.number_input("Código vidro",step=1)

    tipo=st.selectbox("Tipo vidro",["incolor","tek"])

    esp=st.selectbox("Espessura",[4,6,8])

    largura=st.number_input("Largura")

    altura=st.number_input("Altura")

    quantidade=st.number_input("Quantidade vidro na porta",1)

    if st.button("Salvar porta"):

        novo=pd.DataFrame([[
            porta,
            vidro_codigo,
            tipo,
            esp,
            largura,
            altura,
            quantidade
        ]],columns=[
            "porta","vidro_codigo","tipo_vidro",
            "espessura","largura","altura","quantidade"
        ])

        produtos2=pd.concat([produtos,novo])

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Porta cadastrada")


# =====================
# VER PRODUTOS
# =====================

with aba3:

    st.header("Produtos cadastrados")

    st.dataframe(produtos)


# =====================
# CADASTRAR CHAPAS
# =====================

with aba4:

    st.header("Cadastrar chapa")

    tipo=st.selectbox("Tipo vidro chapa",["incolor","tek"])

    esp=st.selectbox("Espessura chapa",[4,6,8])

    largura=st.number_input("Largura chapa")

    altura=st.number_input("Altura chapa")

    if st.button("Salvar chapa"):

        nova=pd.DataFrame([[
            tipo,
            esp,
            largura,
            altura
        ]],columns=[
            "tipo","espessura","largura","altura"
        ])

        chapas2=pd.concat([chapas,nova])

        chapas2.to_csv("chapas.csv",index=False)

        st.success("Chapa cadastrada")

    st.subheader("Chapas cadastradas")

    st.dataframe(chapas)


# =====================
# IMPORTAR PRODUTOS
# =====================

with aba5:

    file=st.file_uploader("Importar produtos Excel")

    if file:

        df=pd.read_excel(file)

        st.dataframe(df)

        if st.button("Salvar produtos"):

            df.to_csv("produtos.csv",index=False)

            st.success("Produtos importados")


# =====================
# IMPORTAR CHAPAS
# =====================

with aba6:

    file=st.file_uploader("Importar chapas Excel")

    if file:

        df=pd.read_excel(file)

        st.dataframe(df)

        if st.button("Salvar chapas"):

            df.to_csv("chapas.csv",index=False)

            st.success("Chapas importadas")


# =====================
# IMPORTAR PEDIDOS
# =====================

with aba7:

    file=st.file_uploader("Importar pedidos Excel")

    if file:

        df=pd.read_excel(file)

        st.dataframe(df)

        if st.button("Adicionar ao lote"):

            for _,r in df.iterrows():

                st.session_state.lote.append({
                    "porta":r["porta"],
                    "quantidade":r["quantidade"]
                })

            st.success("Pedidos adicionados")
