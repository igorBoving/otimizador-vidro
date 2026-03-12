import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# -----------------------------
# CRIAR ARQUIVOS SE NÃO EXISTIREM
# -----------------------------

if not os.path.exists("produtos.csv"):
    pd.DataFrame(columns=[
        "porta","tipo","vidro","espessura","largura","altura"
    ]).to_csv("produtos.csv",index=False)

if not os.path.exists("chapas.csv"):
    pd.DataFrame(columns=[
        "nome","largura","altura","espessura"
    ]).to_csv("chapas.csv",index=False)

# -----------------------------
# CARREGAR DADOS
# -----------------------------

produtos = pd.read_csv("produtos.csv")
chapas = pd.read_csv("chapas.csv")

if "lote" not in st.session_state:
    st.session_state.lote=[]

# -----------------------------
# MENU
# -----------------------------

aba1,aba2,aba3,aba4,aba5=st.tabs([
"Cadastro de portas",
"Importar planilha",
"Portas cadastradas",
"Chapas",
"Lote produção"
])

# ====================================================
# 1 CADASTRAR PORTA
# ====================================================

with aba1:

    st.header("Cadastro de portas")

    porta=st.number_input("Código da porta",step=1)

    tipo=st.selectbox(
        "Tipo",
        ["simples","dupla","tripla"]
    )

    quantidade_vidros={
        "simples":1,
        "dupla":2,
        "tripla":3
    }

    vidros=[]

    for i in range(quantidade_vidros[tipo]):

        st.subheader(f"Vidro {i+1}")

        col1,col2,col3,col4=st.columns(4)

        vidro=col1.selectbox(
            "Tipo vidro",
            ["Incolor","Tek"],
            key=f"vidro{i}"
        )

        espessura=col2.selectbox(
            "Espessura",
            [4,6,8],
            key=f"esp{i}"
        )

        largura=col3.number_input(
            "Largura",
            key=f"larg{i}"
        )

        altura=col4.number_input(
            "Altura",
            key=f"alt{i}"
        )

        vidros.append({
            "porta":porta,
            "tipo":tipo,
            "vidro":vidro,
            "espessura":espessura,
            "largura":largura,
            "altura":altura
        })

    if st.button("Salvar porta"):

        df=pd.DataFrame(vidros)

        produtos2=pd.concat([produtos,df])

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Porta salva")

# ====================================================
# 2 IMPORTAR PLANILHA
# ====================================================

with aba2:

    st.header("Importar planilha")

    arquivo=st.file_uploader("Planilha Excel")

    if arquivo:

        df=pd.read_excel(arquivo)

        produtos2=pd.concat([produtos,df])

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Importado com sucesso")

# ====================================================
# 3 VER PORTAS
# ====================================================

with aba3:

    st.header("Portas cadastradas")

    st.dataframe(produtos)

    st.subheader("Excluir porta")

    cod=st.number_input("Código",step=1)

    if st.button("Excluir"):

        produtos2=produtos[produtos.porta!=cod]

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Porta removida")

    st.subheader("Adicionar ao lote")

    for porta in produtos.porta.unique():

        col1,col2=st.columns([3,1])

        with col1:
            st.write(f"Porta {porta}")

        with col2:

            if st.button("Adicionar",key=f"add{porta}"):

                st.session_state.lote.append({
                    "porta":porta,
                    "quantidade":1
                })

                st.success("Adicionado")

# ====================================================
# 4 CHAPAS
# ====================================================

with aba4:

    st.header("Cadastro de chapas")

    nome=st.text_input("Nome")

    largura=st.number_input("Largura chapa")

    altura=st.number_input("Altura chapa")

    esp=st.selectbox(
        "Espessura",
        [4,6,8]
    )

    if st.button("Salvar chapa"):

        nova=pd.DataFrame([{
            "nome":nome,
            "largura":largura,
            "altura":altura,
            "espessura":esp
        }])

        chapas2=pd.concat([chapas,nova])

        chapas2.to_csv("chapas.csv",index=False)

        st.success("Chapa salva")

    st.dataframe(chapas)

# ====================================================
# 5 LOTE
# ====================================================

with aba5:

    st.header("Lote produção")

    for item in st.session_state.lote:

        col1,col2,col3=st.columns(3)

        col1.write(item["porta"])

        item["quantidade"]=col2.number_input(
            "Quantidade",
            value=item["quantidade"],
            key=f"q{item['porta']}"
        )

        if col3.button("Remover",key=f"r{item['porta']}"):
            st.session_state.lote.remove(item)

    if st.button("Gerar vidros"):

        lista=[]

        for item in st.session_state.lote:

            dados=produtos[
                produtos.porta==item["porta"]
            ]

            for _,r in dados.iterrows():

                for i in range(int(item["quantidade"])):

                    lista.append({
                        "espessura":r["espessura"],
                        "largura":r["largura"],
                        "altura":r["altura"]
                    })

        df=pd.DataFrame(lista)

        st.dataframe(df)
