import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# -----------------------------
# SESSION STATE
# -----------------------------

if "portas" not in st.session_state:
    st.session_state.portas = []

if "chapas" not in st.session_state:
    st.session_state.chapas = []

if "lote" not in st.session_state:
    st.session_state.lote = []

# -----------------------------
# MENU
# -----------------------------

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

    st.title("Importar portas do Excel")

    arquivo = st.file_uploader("Selecione a planilha", type=["xlsx"])

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

        st.success("Portas importadas")

# -----------------------------
# CADASTRO CHAPAS
# -----------------------------

if menu == "Cadastro de Chapas":

    st.title("Cadastro de Chapas")

    col1,col2 = st.columns(2)

    vidro = col1.selectbox("Vidro",["Incolor","Tek"])
    esp = col2.selectbox("Espessura",[4,6,8])

    col3,col4 = st.columns(2)

    largura = col3.number_input("Largura chapa",value=6000)
    altura = col4.number_input("Altura chapa",value=3210)

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

        if col3.button("Excluir",key=f"exc{i}"):

            st.session_state.chapas.pop(i)
            st.rerun()

# -----------------------------
# CADASTRO PORTAS
# -----------------------------

if menu == "Cadastro de Portas":

    st.title("Cadastro de Porta")

    codigo = st.number_input("Código",step=1)

    tipo = st.selectbox("Tipo",["Simples","Dupla","Tripla"])

    laminas = {"Simples":1,"Dupla":2,"Tripla":3}[tipo]

    dados=[]

    for i in range(laminas):

        st.subheader(f"Lâmina {i+1}")

        col1,col2,col3,col4 = st.columns(4)

        vidro = col1.selectbox("Vidro",["Incolor","Tek"],key=f"vidro{i}")
        esp = col2.selectbox("Espessura",[4,6,8],key=f"esp{i}")
        larg = col3.number_input("Largura",key=f"larg{i}")
        alt = col4.number_input("Altura",key=f"alt{i}")

        dados.append({
            "vidro":vidro,
            "esp":esp,
            "larg":larg,
            "alt":alt
        })

    if st.button("Salvar porta"):

        st.session_state.portas.append({
            "codigo":codigo,
            "laminas":dados
        })

        st.success("Porta cadastrada")

# -----------------------------
# PORTAS CADASTRADAS
# -----------------------------

if menu == "Portas Cadastradas":

    st.title("Portas cadastradas")

    for i,p in enumerate(st.session_state.portas):

        col1,col2,col3 = st.columns([3,2,1])

        col1.write(f"Código {p.get('codigo','SEM CODIGO')}")

        if col2.button("Adicionar ao lote",key=f"add{i}"):

            st.session_state.lote.append({
                "codigo":p.get("codigo","SEM CODIGO"),
                "laminas":p["laminas"],
                "qtd":1
            })

        if col3.button("Excluir",key=f"exc{i}"):

            st.session_state.portas.pop(i)
            st.rerun()

# -----------------------------
# LOTE PRODUÇÃO
# -----------------------------

if menu == "Lote de Produção":

    st.title("Lote de produção")

    for i,p in enumerate(st.session_state.lote):

        col1,col2,col3,col4 = st.columns([4,1,1,1])

        col1.write(f"Porta {p.get('codigo','SEM CODIGO')}")

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

        df=pd.DataFrame(pecas)

        grupos=df.groupby(["vidro","esp"])

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
            livre=[(0,0,W,H)]

            layout=[]

            for _,r in dados.iterrows():

                w=r["larg"]
                h=r["alt"]

                colocado=False

                for i,(x,y,L,A) in enumerate(livre):

                    for rot in [(w,h),(h,w)]:

                        pw,ph=rot

                        if pw<=L and ph<=A:

                            layout.append((x,y,pw,ph))

                            livre.pop(i)

                            livre.append((x+pw,y,L-pw,ph))
                            livre.append((x,y+ph,L,A-ph))

                            colocado=True
                            break

                    if colocado:
                        break

                if not colocado:

                    chapas.append(layout)

                    livre=[(0,0,W,H)]
                    layout=[]

                    layout.append((0,0,w,h))

                    livre.append((w,0,W-w,h))
                    livre.append((0,h,W,H-h))

            if layout:
                chapas.append(layout)

            st.write("Peças:",len(dados))
            st.write("Chapas:",len(chapas))

            for i,ch in enumerate(chapas):

                st.subheader(f"Chapa {i+1}")

                fig,ax=plt.subplots()

                ax.set_xlim(0,W)
                ax.set_ylim(0,H)

                area=0

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

                    area+=w*h

                st.pyplot(fig)

                aproveitamento=area/(W*H)*100

                st.write(f"Aproveitamento {aproveitamento:.1f}%")
