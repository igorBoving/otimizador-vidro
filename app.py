import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(layout="wide")

# -----------------------------
# SESSION
# -----------------------------

if "portas" not in st.session_state:
    st.session_state.portas = []

if "chapas" not in st.session_state:
    st.session_state.chapas = []

if "lote" not in st.session_state:
    st.session_state.lote = []

# -----------------------------
# FUNÇÕES NOVAS
# -----------------------------

def mapear_material(vidro, esp):

    if vidro == "Incolor":
        return f"JUMBO_{esp}MM"

    if vidro == "Tek":
        return f"TEK_{esp}MM"

    return f"JUMBO_{esp}MM"


def exportar_ascii(pecas):

    data = datetime.now().strftime("%d%m%Y")
    total = len(pecas)

    linhas = []

    cabecalho = f"LOTEVIDRO{' ' * 23}{data}{' ' * 8}{str(total).zfill(8)}V4"
    linhas.append(cabecalho)

    linhas.append(str(total).zfill(8))

    pos = 1

    for p in pecas:

        material = mapear_material(p["vidro"], p["esp"]).ljust(16)

        posicao = str(pos).zfill(5)
        cliente = "PRODUCAO".ljust(12)
        pedido = "INTERNO".ljust(12)

        shape = "RECT".ljust(8)
        grind = "0000.0000"
        prioridade = "000"
        rot = "Y"
        qtd = "00000001"

        x = f"{p['larg']:08.3f}"
        y = f"{p['alt']:08.3f}"

        linha = (
            f"{material}"
            f"{posicao}"
            f"{cliente}"
            f"{pedido}"
            f"{shape}"
            f"{grind}"
            f"{prioridade}"
            f"{rot}"
            f"{qtd}"
            f"{'0'*8}"
            f"{x}"
            f"{y}"
        )

        linhas.append(linha)
        linhas.append("+CUT")

        pos += 1

    return "\n".join(linhas)

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
# IMPORTAR
# -----------------------------

if menu == "Importar Portas Excel":

    st.title("Importar portas")

    arquivo = st.file_uploader("Excel", type=["xlsx"])

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

        st.success("Importado")

# -----------------------------
# CHAPAS
# -----------------------------

if menu == "Cadastro de Chapas":

    st.title("Chapas")

    col1,col2 = st.columns(2)

    vidro = col1.selectbox("Vidro",["Incolor","Tek"])
    esp = col2.selectbox("Esp",[4,6,8])

    col3,col4 = st.columns(2)

    largura = col3.number_input("Largura",value=6000)
    altura = col4.number_input("Altura",value=3210)

    if st.button("Cadastrar"):
        st.session_state.chapas.append({
            "vidro":vidro,
            "esp":esp,
            "largura":largura,
            "altura":altura
        })

    for i,c in enumerate(st.session_state.chapas):

        col1,col2,col3 = st.columns([3,3,1])

        col1.write(f"{c['vidro']} {c['esp']}mm")
        col2.write(f"{c['largura']} x {c['altura']}")

        if col3.button("Excluir",key=f"exc{i}"):
            st.session_state.chapas.pop(i)
            st.rerun()

# -----------------------------
# PORTAS
# -----------------------------

if menu == "Cadastro de Portas":

    st.title("Cadastro Porta")

    codigo = st.number_input("Código",step=1)

    tipo = st.selectbox("Tipo",["Simples","Dupla","Tripla"])
    n = {"Simples":1,"Dupla":2,"Tripla":3}[tipo]

    dados=[]

    for i in range(n):

        st.subheader(f"Lâmina {i+1}")

        col1,col2,col3,col4 = st.columns(4)

        vidro = col1.selectbox("Vidro",["Incolor","Tek"],key=f"v{i}")
        esp = col2.selectbox("Esp",[4,6,8],key=f"e{i}")
        larg = col3.number_input("Larg",key=f"l{i}")
        alt = col4.number_input("Alt",key=f"a{i}")

        dados.append({
            "vidro":vidro,
            "esp":esp,
            "larg":larg,
            "alt":alt
        })

    if st.button("Salvar"):
        st.session_state.portas.append({
            "codigo":codigo,
            "laminas":dados
        })

# -----------------------------
# PORTAS LISTA
# -----------------------------

if menu == "Portas Cadastradas":

    for i,p in enumerate(st.session_state.portas):

        col1,col2,col3 = st.columns([3,2,1])

        col1.write(f"Porta {p.get('codigo')}")

        if col2.button("Adicionar",key=f"add{i}"):

            st.session_state.lote.append({
                "codigo":p["codigo"],
                "laminas":p["laminas"],
                "qtd":1
            })

        if col3.button("Excluir",key=f"exc{i}"):

            st.session_state.portas.pop(i)
            st.rerun()

# -----------------------------
# LOTE + CORTE
# -----------------------------

if menu == "Lote de Produção":

    st.title("Lote")

    for i,p in enumerate(st.session_state.lote):

        col1,col2,col3,col4 = st.columns([4,1,1,1])

        col1.write(f"Porta {p['codigo']}")

        if col2.button("-",key=f"m{i}"):
            if p["qtd"]>1:
                p["qtd"]-=1

        col3.write(p["qtd"])

        if col4.button("+",key=f"p{i}"):
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
                st.warning("Sem chapa")
                continue

            W=chapa["largura"]
            H=chapa["altura"]

            dados["area"]=dados["larg"]*dados["alt"]
            dados=dados.sort_values(by="area",ascending=False)

            livre=[(0,0,W,H)]
            chapas=[]
            layout=[]

            for _,r in dados.iterrows():

                w=r["larg"]
                h=r["alt"]

                colocado=False

                for i,(x,y,L,A) in enumerate(livre):

                    for pw,ph in [(w,h),(h,w)]:

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

            if layout:
                chapas.append(layout)

            # DESENHO + %
            for i,ch in enumerate(chapas):

                st.subheader(f"Chapa {i+1}")

                fig,ax=plt.subplots()

                ax.set_xlim(0,W)
                ax.set_ylim(0,H)

                area=0

                for x,y,w,h in ch:

                    rect=plt.Rectangle((x,y),w,h,fill=None)
                    ax.add_patch(rect)

                    ax.text(x+w/2,y+h/2,f"{int(w)}x{int(h)}",
                            ha="center",va="center",fontsize=8)

                    area+=w*h

                st.pyplot(fig)

                aproveitamento = area/(W*H)*100
                sucata = 100 - aproveitamento

                st.write(f"Aproveitamento: {aproveitamento:.1f}%")
                st.write(f"Sucata: {sucata:.1f}%")

        # EXPORTAÇÃO
        arquivo = exportar_ascii(pecas)

        st.download_button(
            "Exportar para máquina",
            arquivo,
            file_name="corte_finoglass.asc"
        )
