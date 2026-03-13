import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide")

# =============================
# COLUNAS PADRÃO
# =============================

COL_PRODUTOS=["porta","tipo","vidro","espessura","largura","altura"]
COL_CHAPAS=["nome","vidro","espessura","largura","altura"]

# =============================
# CRIAR ARQUIVOS SE NÃO EXISTIR
# =============================

if not os.path.exists("produtos.csv"):
    pd.DataFrame(columns=COL_PRODUTOS).to_csv("produtos.csv",index=False)

if not os.path.exists("chapas.csv"):
    pd.DataFrame(columns=COL_CHAPAS).to_csv("chapas.csv",index=False)

produtos=pd.read_csv("produtos.csv")
chapas=pd.read_csv("chapas.csv")

# garantir colunas
for c in COL_PRODUTOS:
    if c not in produtos.columns:
        produtos[c]=""

for c in COL_CHAPAS:
    if c not in chapas.columns:
        chapas[c]=""

produtos=produtos[COL_PRODUTOS]
chapas=chapas[COL_CHAPAS]

# =============================
# SESSION
# =============================

if "lote" not in st.session_state:
    st.session_state.lote=[]

# =============================
# MENU
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

    porta=st.number_input("Código da porta",step=1)

    tipo=st.selectbox("Tipo",["simples","dupla","tripla"])

    qtd_vidro={
        "simples":1,
        "dupla":2,
        "tripla":3
    }

    lista=[]

    for i in range(qtd_vidro[tipo]):

        st.subheader(f"Vidro {i+1}")

        c1,c2,c3,c4=st.columns(4)

        vidro=c1.selectbox(
            "Tipo vidro",
            ["Incolor","Tek"],
            key=f"vidro{i}"
        )

        esp=c2.selectbox(
            "Espessura",
            [4,6,8],
            key=f"esp{i}"
        )

        larg=c3.number_input(
            "Largura",
            key=f"larg{i}"
        )

        alt=c4.number_input(
            "Altura",
            key=f"alt{i}"
        )

        lista.append({
            "porta":porta,
            "tipo":tipo,
            "vidro":vidro,
            "espessura":esp,
            "largura":larg,
            "altura":alt
        })

    if st.button("Salvar porta"):

        df=pd.DataFrame(lista)

        produtos2=pd.concat([produtos,df])

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Porta cadastrada")

# =============================
# IMPORTAR PLANILHA
# =============================

with aba2:

    st.header("Importar planilha Excel")

    arquivo=st.file_uploader("Selecionar arquivo")

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

    st.subheader("Excluir porta")

    cod=st.number_input("Código da porta",step=1)

    if st.button("Excluir"):

        produtos2=produtos[produtos["porta"]!=cod]

        produtos2.to_csv("produtos.csv",index=False)

        st.success("Porta excluída")

    st.subheader("Adicionar ao lote")

    cod_lote=st.number_input("Código porta lote",step=1)

    qtd=st.number_input("Quantidade",step=1,value=1)

    if st.button("Adicionar ao lote"):

        st.session_state.lote.append({
            "porta":cod_lote,
            "quantidade":qtd
        })

        st.success("Adicionado")

# =============================
# CHAPAS
# =============================

with aba4:

    st.header("Cadastro chapas")

    nome=st.text_input("Nome chapa")

    vidro=st.selectbox("Tipo vidro",["Incolor","Tek"])

    esp=st.selectbox("Espessura",[4,6,8])

    larg=st.number_input("Largura")

    alt=st.number_input("Altura")

    if st.button("Salvar chapa"):

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
            key=f"q{i}"
        )

        if c3.button("Remover",key=f"r{i}"):
            st.session_state.lote.remove(item)

    if st.button("Gerar vidros"):

        lista=[]

        for item in st.session_state.lote:

            dados=produtos[produtos["porta"]==item["porta"]]

            for _,r in dados.iterrows():

                vidro=str(r.get("vidro","Incolor"))
                esp=float(r.get("espessura",4))

                try:
                    larg=float(r.get("largura",0))
                    alt=float(r.get("altura",0))
                except:
                    larg=0
                    alt=0

                if larg==0 or alt==0:
                    continue

                for i in range(int(item["quantidade"])):

                    lista.append({
                        "vidro":vidro,
                        "espessura":esp,
                        "largura":larg,
                        "altura":alt
                    })

        df=pd.DataFrame(lista)

        if df.empty:
            st.error("Nenhum vidro válido encontrado")
            st.stop()

        st.subheader("Vidros do lote")

        st.dataframe(df)

        if len(chapas)==0:
            st.warning("Nenhuma chapa cadastrada")
            st.stop()

        chapa=chapas.iloc[0]

        largura_chapa=float(chapa["largura"])
        altura_chapa=float(chapa["altura"])

        fig,ax=plt.subplots()

        ax.add_patch(
            plt.Rectangle(
                (0,0),
                largura_chapa,
                altura_chapa,
                fill=False,
                linewidth=2
            )
        )

        x=0
        y=0

        area_vidros=0

        for _,v in df.iterrows():

            w=float(v["largura"])
            h=float(v["altura"])

            if x+w>largura_chapa:
                x=0
                y+=h

            if y+h>altura_chapa:
                break

            ax.add_patch(
                plt.Rectangle((x,y),w,h)
            )

            area_vidros+=w*h

            x+=w

        ax.set_xlim(0,largura_chapa)
        ax.set_ylim(0,altura_chapa)

        ax.set_title("Layout da chapa")

        st.pyplot(fig)

        area_chapa=largura_chapa*altura_chapa

        aproveitamento=(area_vidros/area_chapa)*100

        sucata=100-aproveitamento

        st.write(f"Aproveitamento: {aproveitamento:.2f}%")
        st.write(f"Sucata: {sucata:.2f}%")
