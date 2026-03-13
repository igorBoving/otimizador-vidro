import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide")

COL_PRODUTOS=["porta","tipo","vidro","espessura","largura","altura"]
COL_CHAPAS=["nome","vidro","espessura","largura","altura"]

# =============================
# CRIAR ARQUIVOS
# =============================

if not os.path.exists("produtos.csv"):
    pd.DataFrame(columns=COL_PRODUTOS).to_csv("produtos.csv",index=False)

if not os.path.exists("chapas.csv"):
    pd.DataFrame(columns=COL_CHAPAS).to_csv("chapas.csv",index=False)

produtos=pd.read_csv("produtos.csv")
chapas=pd.read_csv("chapas.csv")

for c in COL_PRODUTOS:
    if c not in produtos.columns:
        produtos[c]=""

for c in COL_CHAPAS:
    if c not in chapas.columns:
        chapas[c]=""

produtos=produtos[COL_PRODUTOS]
chapas=chapas[COL_CHAPAS]

if "lote" not in st.session_state:
    st.session_state.lote=[]

# =============================
# TABS
# =============================

aba1,aba2,aba3,aba4,aba5=st.tabs([
"Cadastro portas",
"Importar portas",
"Portas cadastradas",
"Chapas",
"Lote produção"
])

# =============================
# CADASTRO PORTA
# =============================

with aba1:

    st.header("Cadastrar porta")

    porta=st.number_input(
        "Código da porta",
        step=1,
        key="cad_porta"
    )

    tipo=st.selectbox(
        "Tipo",
        ["simples","dupla","tripla"],
        key="cad_tipo"
    )

    qtd={"simples":1,"dupla":2,"tripla":3}

    lista=[]

    for i in range(qtd[tipo]):

        st.subheader(f"Vidro {i+1}")

        c1,c2,c3,c4=st.columns(4)

        vidro=c1.selectbox(
            "Tipo vidro",
            ["Incolor","Tek"],
            key=f"cad_vidro{i}"
        )

        esp=c2.selectbox(
            "Espessura",
            [4,6,8],
            key=f"cad_esp{i}"
        )

        larg=c3.number_input(
            "Largura",
            key=f"cad_larg{i}"
        )

        alt=c4.number_input(
            "Altura",
            key=f"cad_alt{i}"
        )

        lista.append({
            "porta":porta,
            "tipo":tipo,
            "vidro":vidro,
            "espessura":esp,
            "largura":larg,
            "altura":alt
        })

    if st.button("Salvar porta",key="btn_salvar_porta"):

        df=pd.DataFrame(lista)

        produtos2=pd.concat([produtos,df])

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Porta cadastrada")

# =============================
# IMPORTAR
# =============================

with aba2:

    st.header("Importar Excel")

    arquivo=st.file_uploader(
        "Selecionar planilha",
        key="import_excel"
    )

    if arquivo:

        df=pd.read_excel(arquivo)

        for c in COL_PRODUTOS:
            if c not in df.columns:
                df[c]=""

        df=df[COL_PRODUTOS]

        produtos2=pd.concat([produtos,df])

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Planilha importada")

# =============================
# PORTAS CADASTRADAS
# =============================

with aba3:

    st.header("Portas cadastradas")

    st.dataframe(produtos)

    cod=st.number_input(
        "Excluir porta",
        step=1,
        key="excluir_porta"
    )

    if st.button("Excluir",key="btn_excluir"):

        produtos2=produtos[produtos["porta"]!=cod]

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Porta excluída")

    st.subheader("Adicionar ao lote")

    cod_lote=st.number_input(
        "Código porta lote",
        step=1,
        key="lote_porta"
    )

    qtd=st.number_input(
        "Quantidade",
        step=1,
        value=1,
        key="lote_qtd"
    )

    if st.button("Adicionar ao lote",key="btn_add_lote"):

        st.session_state.lote.append({
            "porta":cod_lote,
            "quantidade":qtd
        })

        st.success("Adicionado ao lote")

# =============================
# CHAPAS
# =============================

with aba4:

    st.header("Cadastro chapas")

    nome=st.text_input("Nome",key="chapa_nome")

    vidro=st.selectbox(
        "Tipo vidro",
        ["Incolor","Tek"],
        key="chapa_vidro"
    )

    esp=st.selectbox(
        "Espessura",
        [4,6,8],
        key="chapa_esp"
    )

    larg=st.number_input("Largura",key="chapa_larg")

    alt=st.number_input("Altura",key="chapa_alt")

    if st.button("Salvar chapa",key="btn_salvar_chapa"):

        nova=pd.DataFrame([{
            "nome":nome,
            "vidro":vidro,
            "espessura":esp,
            "largura":larg,
            "altura":alt
        }])

        chapas2=pd.concat([chapas,nova])

        chapas2.to_csv("chapas.csv",index=False)

        st.success("Chapa cadastrada")

    st.dataframe(chapas)

# =============================
# LOTE PRODUÇÃO
# =============================

with aba5:

    st.header("Lote produção")

    for i,item in enumerate(st.session_state.lote):

        c1,c2,c3=st.columns(3)

        c1.write(f"Porta {item['porta']}")

        item["quantidade"]=c2.number_input(
            "Qtd",
            value=item["quantidade"],
            key=f"lote_q{i}"
        )

        if c3.button("Remover",key=f"rem{i}"):
            st.session_state.lote.remove(item)

    if st.button("Gerar vidros",key="btn_gerar_vidros"):

        lista=[]

        for item in st.session_state.lote:

            dados=produtos[produtos["porta"]==item["porta"]]

            for _,r in dados.iterrows():

                larg=float(r["largura"])
                alt=float(r["altura"])

                for i in range(int(item["quantidade"])):

                    lista.append({
                        "largura":larg,
                        "altura":alt
                    })

        df=pd.DataFrame(lista)

        st.subheader("Vidros do lote")

        st.dataframe(df)

        if len(chapas)==0:
            st.warning("Nenhuma chapa cadastrada")
            st.stop()

        chapa=chapas.iloc[0]

        largura=float(chapa["largura"])
        altura=float(chapa["altura"])

        fig,ax=plt.subplots()

        ax.add_patch(
            plt.Rectangle((0,0),largura,altura,fill=False,linewidth=2)
        )

        x=0
        y=0

        area_vidros=0

        for _,v in df.iterrows():

            w=float(v["largura"])
            h=float(v["altura"])

            if x+w>largura:
                x=0
                y+=h

            if y+h>altura:
                break

            ax.add_patch(plt.Rectangle((x,y),w,h))

            area_vidros+=w*h

            x+=w

        ax.set_xlim(0,largura)
        ax.set_ylim(0,altura)

        st.pyplot(fig)

        area_chapa=largura*altura

        aproveitamento=(area_vidros/area_chapa)*100

        sucata=100-aproveitamento

        st.write(f"Aproveitamento: {aproveitamento:.2f}%")
        st.write(f"Sucata: {sucata:.2f}%")
