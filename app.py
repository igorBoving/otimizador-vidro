import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ------------------------------
# Inicialização
# ------------------------------

if "portas" not in st.session_state:
    st.session_state.portas = []

if "chapas" not in st.session_state:
    st.session_state.chapas = []

if "lote" not in st.session_state:
    st.session_state.lote = []


# ------------------------------
# MENU
# ------------------------------

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Cadastro de Chapas",
        "Cadastro de Portas",
        "Portas Cadastradas",
        "Lote de Produção"
    ]
)

# ------------------------------
# CADASTRO DE CHAPAS
# ------------------------------

if menu == "Cadastro de Chapas":

    st.title("Cadastro de Chapas")

    col1, col2 = st.columns(2)

    with col1:
        tipo_vidro = st.selectbox(
            "Tipo de vidro",
            ["Incolor", "Tek"],
            key="tipo_chapa"
        )

        espessura = st.selectbox(
            "Espessura (mm)",
            [4,6,8],
            key="esp_chapa"
        )

    with col2:
        largura = st.number_input(
            "Largura da chapa (mm)",
            value=6000
        )

        altura = st.number_input(
            "Altura da chapa (mm)",
            value=3210
        )

    if st.button("Cadastrar chapa"):

        st.session_state.chapas.append({
            "vidro": tipo_vidro,
            "esp": espessura,
            "largura": largura,
            "altura": altura
        })

    st.subheader("Chapas cadastradas")

    for i, c in enumerate(st.session_state.chapas):

        col1,col2,col3 = st.columns([3,3,1])

        col1.write(f"{c['vidro']} {c['esp']}mm")
        col2.write(f"{c['largura']} x {c['altura']}")

        if col3.button("Excluir", key=f"exc_chapa{i}"):
            st.session_state.chapas.pop(i)
            st.rerun()


# ------------------------------
# CADASTRO DE PORTAS
# ------------------------------

if menu == "Cadastro de Portas":

    st.title("Cadastro de Porta")

    codigo = st.number_input(
        "Código da porta",
        step=1,
        key="cod_porta"
    )

    tipo_porta = st.selectbox(
        "Tipo",
        ["Simples","Dupla","Tripla"]
    )

    laminas = 1
    if tipo_porta == "Dupla":
        laminas = 2
    if tipo_porta == "Tripla":
        laminas = 3

    dados = []

    for i in range(laminas):

        st.subheader(f"Lâmina {i+1}")

        col1,col2,col3,col4 = st.columns(4)

        vidro = col1.selectbox(
            "Vidro",
            ["Incolor","Tek"],
            key=f"vidro{i}"
        )

        esp = col2.selectbox(
            "Espessura",
            [4,6,8],
            key=f"esp{i}"
        )

        larg = col3.number_input(
            "Largura",
            key=f"larg{i}"
        )

        alt = col4.number_input(
            "Altura",
            key=f"alt{i}"
        )

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


# ------------------------------
# LISTA DE PORTAS
# ------------------------------

if menu == "Portas Cadastradas":

    st.title("Portas cadastradas")

    for i,p in enumerate(st.session_state.portas):

        col1,col2,col3 = st.columns([3,2,1])

        col1.write(f"Código {p['codigo']}")

        if col2.button(
            "Adicionar ao lote",
            key=f"lote{i}"
        ):
            st.session_state.lote.append(p)

        if col3.button(
            "Excluir",
            key=f"exc_porta{i}"
        ):
            st.session_state.portas.pop(i)
            st.rerun()


# ------------------------------
# LOTE DE PRODUÇÃO
# ------------------------------

if menu == "Lote de Produção":

    st.title("Lote de produção")

    if len(st.session_state.lote) == 0:
        st.info("Nenhuma porta no lote")

    for i,p in enumerate(st.session_state.lote):

        col1,col2 = st.columns([4,1])

        col1.write(f"Porta {p['codigo']}")

        if col2.button(
            "Remover",
            key=f"rem{i}"
        ):
            st.session_state.lote.pop(i)
            st.rerun()

    if st.button("Gerar corte"):

        pecas = []

        for porta in st.session_state.lote:
            for l in porta["laminas"]:

                pecas.append({
                    "vidro":l["vidro"],
                    "esp":l["esp"],
                    "larg":l["larg"],
                    "alt":l["alt"]
                })

        df = pd.DataFrame(pecas)

        grupos = df.groupby(["vidro","esp"])

        for g,dados in grupos:

            vidro,esp = g

            st.subheader(f"{vidro} {esp}mm")

            chapa = None

            for c in st.session_state.chapas:

                if c["vidro"]==vidro and c["esp"]==esp:
                    chapa=c

            if chapa is None:
                st.warning("Sem chapa cadastrada")
                continue

            largura = chapa["largura"]
            altura = chapa["altura"]

            fig,ax = plt.subplots()

            ax.set_xlim(0,largura)
            ax.set_ylim(0,altura)

            x=0
            y=0
            linha_alt=0

            area_usada=0

            for _,r in dados.iterrows():

                w=r["larg"]
                h=r["alt"]

                if x+w>largura:
                    x=0
                    y+=linha_alt
                    linha_alt=0

                if y+h>altura:
                    break

                rect = plt.Rectangle(
                    (x,y),
                    w,
                    h,
                    fill=None,
                    edgecolor="blue"
                )

                ax.add_patch(rect)

                x+=w

                linha_alt=max(linha_alt,h)

                area_usada+=w*h

            area_total=largura*altura

            aproveitamento=area_usada/area_total*100

            st.pyplot(fig)

            st.write(
                f"Aproveitamento: {aproveitamento:.1f}%"
            )

            st.write(
                f"Sucata: {100-aproveitamento:.1f}%"
            )
