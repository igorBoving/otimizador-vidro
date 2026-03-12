import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide")

# -------------------------
# CRIAR ARQUIVOS
# -------------------------

if not os.path.exists("produtos.csv"):
    pd.DataFrame(columns=[
        "porta","tipo","vidro","espessura","largura","altura"
    ]).to_csv("produtos.csv",index=False)

if not os.path.exists("chapas.csv"):
    pd.DataFrame(columns=[
        "nome","vidro","espessura","largura","altura"
    ]).to_csv("chapas.csv",index=False)

# -------------------------
# CARREGAR DADOS
# -------------------------

produtos=pd.read_csv("produtos.csv")
chapas=pd.read_csv("chapas.csv")

if "lote" not in st.session_state:
    st.session_state.lote=[]

# -------------------------
# MENU
# -------------------------

aba1,aba2,aba3,aba4,aba5=st.tabs([
"Cadastro portas",
"Importar portas",
"Portas cadastradas",
"Chapas",
"Lote produção"
])

# =====================================================
# CADASTRO DE PORTAS
# =====================================================

with aba1:

    st.header("Cadastro de portas")

    porta=st.number_input(
        "Código da porta",
        step=1,
        key="cadastro_porta"
    )

    tipo=st.selectbox(
        "Tipo",
        ["simples","dupla","tripla"],
        key="tipo_porta"
    )

    qtd_vidros={
        "simples":1,
        "dupla":2,
        "tripla":3
    }

    vidros=[]

    for i in range(qtd_vidros[tipo]):

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

    if st.button("Salvar porta",key="salvar_porta"):

        df=pd.DataFrame(vidros)

        produtos2=pd.concat([produtos,df])

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Porta cadastrada")

# =====================================================
# IMPORTAR PLANILHA
# =====================================================

with aba2:

    st.header("Importar planilha Excel")

    arquivo=st.file_uploader(
        "Selecione a planilha",
        key="importar_planilha"
    )

    if arquivo:

        df=pd.read_excel(arquivo)

        produtos2=pd.concat([produtos,df])

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Portas importadas")

# =====================================================
# PORTAS CADASTRADAS
# =====================================================

with aba3:

    st.header("Portas cadastradas")

    st.dataframe(produtos)

    st.subheader("Excluir porta")

    codigo=st.number_input(
        "Código da porta",
        step=1,
        key="excluir_porta"
    )

    if st.button("Excluir porta",key="botao_excluir"):

        produtos2=produtos[
            produtos.porta!=codigo
        ]

        produtos2.to_csv(
            "produtos.csv",
            index=False
        )

        st.success("Porta excluída")

    st.subheader("Adicionar ao lote")

    codigo_lote=st.number_input(
        "Código porta lote",
        step=1,
        key="porta_lote"
    )

    quantidade=st.number_input(
        "Quantidade",
        step=1,
        value=1,
        key="quantidade_lote"
    )

    if st.button("Adicionar ao lote",key="add_lote"):

        st.session_state.lote.append({
            "porta":codigo_lote,
            "quantidade":quantidade
        })

        st.success("Adicionado ao lote")

# =====================================================
# CHAPAS
# =====================================================

with aba4:

    st.header("Cadastro chapas")

    nome=st.text_input("Nome chapa",key="nome_chapa")

    vidro=st.selectbox(
        "Tipo vidro",
        ["Incolor","Tek"],
        key="tipo_vidro_chapa"
    )

    espessura=st.selectbox(
        "Espessura",
        [4,6,8],
        key="esp_chapa"
    )

    largura=st.number_input("Largura",key="larg_chapa")

    altura=st.number_input("Altura",key="alt_chapa")

    if st.button("Salvar chapa",key="salvar_chapa"):

        nova=pd.DataFrame([{
            "nome":nome,
            "vidro":vidro,
            "espessura":espessura,
            "largura":largura,
            "altura":altura
        }])

        chapas2=pd.concat([chapas,nova])

        chapas2.to_csv("chapas.csv",index=False)

        st.success("Chapa salva")

    st.dataframe(chapas)

# =====================================================
# LOTE PRODUÇÃO
# =====================================================

with aba5:

    st.header("Produção lote")

    for i,item in enumerate(st.session_state.lote):

        col1,col2,col3=st.columns(3)

        col1.write(f"Porta {item['porta']}")

        item["quantidade"]=col2.number_input(
            "Qtd",
            value=item["quantidade"],
            key=f"q{i}"
        )

        if col3.button("Remover",key=f"r{i}"):
            st.session_state.lote.remove(item)

    if st.button("Gerar vidros",key="gerar_vidros"):

        lista=[]

        for item in st.session_state.lote:

            dados=produtos[
                produtos.porta==item["porta"]
            ]

            for _,r in dados.iterrows():

                for i in range(int(item["quantidade"])):

                    lista.append({
                        "vidro":r["vidro"],
                        "espessura":r["espessura"],
                        "largura":r["largura"],
                        "altura":r["altura"]
                    })

        df=pd.DataFrame(lista)

        st.subheader("Vidros do lote")

        st.dataframe(df)

        if len(chapas)>0:

            chapa=chapas.iloc[0]

            fig,ax=plt.subplots()

            ax.add_patch(
                plt.Rectangle(
                    (0,0),
                    chapa.largura,
                    chapa.altura,
                    fill=False
                )
            )

            x=0
            y=0

            area_vidros=0

            for _,v in df.iterrows():

                ax.add_patch(
                    plt.Rectangle(
                        (x,y),
                        v.largura,
                        v.altura
                    )
                )

                area_vidros+=v.largura*v.altura

                x+=v.largura

                if x>chapa.largura:

                    x=0
                    y+=v.altura

            ax.set_xlim(0,chapa.largura)
            ax.set_ylim(0,chapa.altura)

            st.pyplot(fig)

            area_chapa=chapa.largura*chapa.altura

            aproveitamento=(area_vidros/area_chapa)*100

            sucata=100-aproveitamento

            st.write(f"Aproveitamento: {aproveitamento:.2f}%")
            st.write(f"Sucata: {sucata:.2f}%")
