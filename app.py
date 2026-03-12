import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from rectpack import newPacker

st.set_page_config(layout="wide")

# =========================
# CRIAR BANCO SE NÃO EXISTIR
# =========================

if not os.path.exists("produtos.csv"):
    pd.DataFrame(columns=[
        "porta",
        "vidro_codigo",
        "tipo_vidro",
        "espessura",
        "largura",
        "altura",
        "quantidade"
    ]).to_csv("produtos.csv",index=False)

if not os.path.exists("chapas.csv"):
    pd.DataFrame([
        ["incolor",4,6000,3210],
        ["incolor",6,6000,3210],
        ["incolor",8,6000,3210],
        ["tek",4,3300,2134],
        ["tek",6,3300,2134],
        ["tek",8,3300,2134]
    ],columns=[
        "tipo",
        "espessura",
        "largura",
        "altura"
    ]).to_csv("chapas.csv",index=False)

produtos=pd.read_csv("produtos.csv")
chapas=pd.read_csv("chapas.csv")

# =========================
# EXPLODIR PORTAS
# =========================

def explodir(pedido):

    vidros=[]

    for _,p in pedido.iterrows():

        porta=p["porta"]
        qtd=p["quantidade"]

        comp=produtos[
            produtos["porta"]==porta
        ]

        for _,c in comp.iterrows():

            vidros.append({
                "codigo":c["vidro_codigo"],
                "tipo":c["tipo_vidro"],
                "espessura":c["espessura"],
                "largura":c["largura"],
                "altura":c["altura"],
                "quantidade":qtd*c["quantidade"]
            })

    df=pd.DataFrame(vidros)

    df=df.groupby(
        ["codigo","tipo","espessura","largura","altura"],
        as_index=False
    ).sum()

    return df

# =========================
# OTIMIZAR CORTE
# =========================

def otimizar(df,w,h,tentativas=200):

    melhor=None
    melhor_sucata=999

    area_chapa=w*h

    for _ in range(tentativas):

        packer=newPacker(rotation=True)

        df2=df.sample(frac=1)

        for _,r in df2.iterrows():

            for i in range(int(r["quantidade"])):

                packer.add_rect(
                    r["largura"],
                    r["altura"],
                    rid=f'{r["codigo"]}\n{r["espessura"]}mm'
                )

        packer.add_bin(w,h,float("inf"))

        packer.pack()

        chapas_usadas=len(packer)

        area_vidros=0

        for _,r in df.iterrows():

            area_vidros+=(
                r["largura"]*
                r["altura"]*
                r["quantidade"]
            )

        area_total=chapas_usadas*area_chapa

        sucata=1-(area_vidros/area_total)

        if sucata<melhor_sucata:

            melhor_sucata=sucata
            melhor=packer

    return melhor,melhor_sucata

# =========================
# DESENHAR CHAPA
# =========================

def desenhar(packer,w,h,i):

    fig,ax=plt.subplots(figsize=(9,4))

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
"Produtos",
"Cadastrar Porta",
"Importar Excel"
])

# =========================
# PRODUÇÃO
# =========================

with aba1:

    st.header("Lote de Produção")

    if "lote" not in st.session_state:
        st.session_state.lote=[]

    col1,col2,col3=st.columns(3)

    with col1:
        porta=st.number_input(
            "Código da porta",
            step=1
        )

    with col2:
        qtd=st.number_input(
            "Quantidade",
            step=1
        )

    with col3:
        if st.button("Adicionar ao lote"):

            st.session_state.lote.append({
                "porta":porta,
                "quantidade":qtd
            })

    lote_df=pd.DataFrame(
        st.session_state.lote
    )

    st.dataframe(lote_df)

    if st.button("Limpar lote"):
        st.session_state.lote=[]

    if "resultado" not in st.session_state:
        st.session_state.resultado=None

    if st.button("Calcular corte"):

        vidros=explodir(lote_df)

        resultado={}

        for _,c in chapas.iterrows():

            tipo=c["tipo"]
            esp=c["espessura"]

            df=vidros[
                (vidros["tipo"]==tipo) &
                (vidros["espessura"]==esp)
            ]

            if len(df)==0:
                continue

            packer,sucata=otimizar(
                df,
                c["largura"],
                c["altura"]
            )

            resultado[f"{tipo}_{esp}"]={
                "packer":packer,
                "sucata":sucata,
                "largura":c["largura"],
                "altura":c["altura"],
                "tipo":tipo,
                "esp":esp
            }

        st.session_state.resultado=resultado

    if st.session_state.resultado:

        for chave,dados in st.session_state.resultado.items():

            st.subheader(
                f'{dados["tipo"]} {dados["esp"]}mm'
            )

            packer=dados["packer"]

            st.write(
                "Chapas usadas:",
                len(packer)
            )

            st.write(
                "Sucata:",
                round(dados["sucata"]*100,2),
                "%"
            )

            i=st.slider(
                f'Layout {chave}',
                0,
                len(packer)-1,
                0
            )

            fig=desenhar(
                packer,
                dados["largura"],
                dados["altura"],
                i
            )

            st.pyplot(fig)

# =========================
# PRODUTOS
# =========================

with aba2:

    st.header("Produtos cadastrados")

    st.dataframe(produtos)

# =========================
# CADASTRAR PORTA
# =========================

with aba3:

    st.header("Cadastrar nova porta")

    porta=st.number_input(
        "Código da porta",
        step=1,
        key="cadastro"
    )

    tipo=st.selectbox(
        "Tipo da porta",
        ["simples","duplo","triplo"]
    )

    dados=[]

    if tipo=="simples":

        vidro=st.selectbox(
            "Tipo vidro",
            ["incolor","tek"]
        )

        esp=st.selectbox(
            "Espessura",
            [4,6,8]
        )

        l=st.number_input("largura")
        a=st.number_input("altura")

        if st.button("Salvar"):

            dados.append([
                porta,
                porta*10+1,
                vidro,
                esp,
                l,
                a,
                1
            ])

    if tipo=="duplo":

        st.write("Vidro 1")

        vidro1=st.selectbox(
            "tipo1",
            ["incolor","tek"]
        )

        esp1=st.selectbox(
            "esp1",
            [4,6,8]
        )

        l1=st.number_input("largura1")
        a1=st.number_input("altura1")

        st.write("Vidro 2")

        vidro2=st.selectbox(
            "tipo2",
            ["incolor","tek"]
        )

        esp2=st.selectbox(
            "esp2",
            [4,6,8]
        )

        l2=st.number_input("largura2")
        a2=st.number_input("altura2")

        if st.button("Salvar"):

            dados.append([
                porta,
                porta*10+1,
                vidro1,
                esp1,
                l1,
                a1,
                1
            ])

            dados.append([
                porta,
                porta*10+2,
                vidro2,
                esp2,
                l2,
                a2,
                1
            ])

    if tipo=="triplo":

        for i in range(3):

            st.write(f"Vidro {i+1}")

            vidro=st.selectbox(
                f"tipo{i}",
                ["incolor","tek"]
            )

            esp=st.selectbox(
                f"esp{i}",
                [4,6,8]
            )

            l=st.number_input(
                f"largura{i}"
            )

            a=st.number_input(
                f"altura{i}"
            )

            dados.append([
                porta,
                porta*10+i,
                vidro,
                esp,
                l,
                a,
                1
            ])

        if st.button("Salvar"):

            pass

    if len(dados)>0:

        df=pd.DataFrame(
            dados,
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

        produtos2=pd.concat(
            [produtos,df]
        )

        produtos2.to_csv(
            "produtos.csv",
            index=False
        )

        st.success("Porta cadastrada")

# =========================
# IMPORTAR EXCEL
# =========================

with aba4:

    st.header("Importar pedido")

    file=st.file_uploader("Excel")

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
