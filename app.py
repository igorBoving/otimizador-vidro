import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

if "portas" not in st.session_state:
    st.session_state.portas = []

if "chapas" not in st.session_state:
    st.session_state.chapas = []

if "lote" not in st.session_state:
    st.session_state.lote = []


menu = st.sidebar.selectbox(
    "Menu",
    [
        "Importar Portas Excel",
        "Cadastro de Chapas",
        "Cadastro de Portas",
        "Portas Cadastradas",
        "Lote de Produção"
    ]
)

# -----------------------------
# IMPORTAR EXCEL
# -----------------------------

if menu == "Importar Portas Excel":

    st.title("Importar portas")

    arquivo = st.file_uploader("Planilha Excel", type=["xlsx"])

    if arquivo:

        df = pd.read_excel(arquivo)

        grupos = df.groupby("codigo")

        for cod, dados in grupos:

            laminas = []

            for _, r in dados.iterrows():

                laminas.append({
                    "vidro": str(r["vidro"]).capitalize(),
                    "esp": int(r["espessura"]),
                    "larg": float(r["largura"]),
                    "alt": float(r["altura"])
                })

            st.session_state.portas.append({
                "codigo": cod,
                "laminas": laminas
            })

        st.success("Importação concluída")


# -----------------------------
# CADASTRO CHAPAS
# -----------------------------

if menu == "Cadastro de Chapas":

    st.title("Cadastro de chapas")

    col1,col2 = st.columns(2)

    vidro = col1.selectbox("Vidro",["Incolor","Tek"])
    esp = col2.selectbox("Espessura",[4,6,8])

    col3,col4 = st.columns(2)

    largura = col3.number_input("Largura",value=6000)
    altura = col4.number_input("Altura",value=3210)

    if st.button("Cadastrar chapa"):

        st.session_state.chapas.append({
            "vidro":vidro,
            "esp":esp,
            "largura":largura,
            "altura":altura
        })

    st.subheader("Chapas cadastradas")

    for i,c in enumerate(st.session_state.chapas):

        col1,col2,col3 = st.columns([3,3,1])

        col1.write(f"{c['vidro']} {c['esp']}mm")
        col2.write(f"{c['largura']} x {c['altura']}")

        if col3.button("Excluir",key=f"ex{i}"):

            st.session_state.chapas.pop(i)
            st.rerun()


# -----------------------------
# CADASTRO PORTAS
# -----------------------------

if menu == "Cadastro de Portas":

    st.title("Cadastro de porta")

    codigo = st.number_input("Código",step=1)

    tipo = st.selectbox("Tipo",["Simples","Dupla","Tripla"])

    qtd = {"Simples":1,"Dupla":2,"Tripla":3}[tipo]

    laminas=[]

    for i in range(qtd):

        st.subheader(f"Lâmina {i+1}")

        col1,col2,col3,col4 = st.columns(4)

        vidro = col1.selectbox("Vidro",["Incolor","Tek"],key=f"v{i}")
        esp = col2.selectbox("Espessura",[4,6,8],key=f"e{i}")
        larg = col3.number_input("Largura",key=f"l{i}")
        alt = col4.number_input("Altura",key=f"a{i}")

        laminas.append({
            "vidro":vidro,
            "esp":esp,
            "larg":larg,
            "alt":alt
        })

    if st.button("Salvar"):

        st.session_state.portas.append({
            "codigo":codigo,
            "laminas":laminas
        })

        st.success("Porta cadastrada")


# -----------------------------
# PORTAS CADASTRADAS
# -----------------------------

if menu == "Portas Cadastradas":

    st.title("Portas cadastradas")

    for i,p in enumerate(st.session_state.portas):

        col1,col2,col3 = st.columns([4,2,1])

        col1.write(f"Porta {p['codigo']}")

        if col2.button("Adicionar ao lote",key=f"add{i}"):

            st.session_state.lote.append({
                "codigo":p["codigo"],
                "laminas":p["laminas"],
                "qtd":1
            })

        if col3.button("Excluir",key=f"del{i}"):

            st.session_state.portas.pop(i)
            st.rerun()


# -----------------------------
# LOTE
# -----------------------------

if menu == "Lote de Produção":

    st.title("Lote de produção")

    for i,p in enumerate(st.session_state.lote):

        col1,col2,col3,col4 = st.columns([4,1,1,1])

        col1.write(f"Porta {p['codigo']}")

        if col2.button("-",key=f"menos{i}"):

            if p["qtd"]>1:
                p["qtd"]-=1

        col3.write(p["qtd"])

        if col4.button("+",key=f"mais{i}"):

            p["qtd"]+=1


    if st.button("Gerar Corte"):

        pecas=[]

        for porta in st.session_state.lote:

            for _ in range(porta["qtd"]):

                for l in porta["laminas"]:

                    pecas.append(l)

        df = pd.DataFrame(pecas)

        grupos = df.groupby(["vidro","esp"])


        for g,dados in grupos:

            vidro,esp=g

            st.header(f"{vidro} {esp}mm")

            chapa=None

            for c in st.session_state.chapas:

                if c["vidro"]==vidro and c["esp"]==esp:
                    chapa=c

            if chapa is None:

                st.warning("Chapa não cadastrada")
                continue


            W=chapa["largura"]
            H=chapa["altura"]

            dados["area"]=dados["larg"]*dados["alt"]

            dados=dados.sort_values(by="area",ascending=False)

            chapas=[]

            livres=[(0,0,W,H)]

            atual=[]

            for _,r in dados.iterrows():

                colocado=False

                for i,(x,y,w,h) in enumerate(livres):

                    pw=r["larg"]
                    ph=r["alt"]

                    if pw<=w and ph<=h:

                        atual.append((x,y,pw,ph))

                        livres.pop(i)

                        livres.append((x+pw,y,w-pw,ph))
                        livres.append((x,y+ph,w,h-ph))

                        colocado=True
                        break

                    if ph<=w and pw<=h:

                        atual.append((x,y,ph,pw))

                        livres.pop(i)

                        livres.append((x+ph,y,w-ph,pw))
                        livres.append((x,y+pw,w,h-pw))

                        colocado=True
                        break

                if not colocado:

                    chapas.append(atual)

                    livres=[(0,0,W,H)]

                    atual=[(0,0,r["larg"],r["alt"])]

            if atual:
                chapas.append(atual)


            st.write("Peças:",len(dados))
            st.write("Chapas:",len(chapas))


            for i,ch in enumerate(chapas):

                st.subheader(f"Chapa {i+1}")

                fig,ax=plt.subplots()

                ax.set_xlim(0,W)
                ax.set_ylim(0,H)

                for x,y,w,h in ch:

                    rect=plt.Rectangle((x,y),w,h,fill=None)

                    ax.add_patch(rect)

                    ax.text(
                        x+w/2,
                        y+h/2,
                        f"{int(w)}x{int(h)}",
                        ha="center",
                        va="center",
                        fontsize=8
                    )

                st.pyplot(fig)
