import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# =========================
# ESTADO
# =========================
if "portas" not in st.session_state:
    st.session_state.portas = []

if "chapas" not in st.session_state:
    st.session_state.chapas = []

if "quantidades" not in st.session_state:
    st.session_state.quantidades = {}

# =========================
# MENU
# =========================
menu = st.sidebar.selectbox("Menu", ["Lote de Produção"])

# =========================
# FUNÇÃO TETRIS
# =========================
def otimizar_chapa(pecas, W, H):
    pecas = sorted(pecas, key=lambda x: x[0]*x[1], reverse=True)

    livres = [(0, 0, W, H)]
    ocupados = []

    for peca in pecas:
        w, h = peca
        melhor_idx = -1
        melhor_area = None
        melhor_rot = False

        for i, (x, y, lw, lh) in enumerate(livres):
            # normal
            if w <= lw and h <= lh:
                sobra = lw*lh - w*h
                if melhor_area is None or sobra < melhor_area:
                    melhor_idx = i
                    melhor_area = sobra
                    melhor_rot = False

            # rotacionado
            if h <= lw and w <= lh:
                sobra = lw*lh - h*w
                if melhor_area is None or sobra < melhor_area:
                    melhor_idx = i
                    melhor_area = sobra
                    melhor_rot = True

        if melhor_idx == -1:
            continue

        x, y, lw, lh = livres.pop(melhor_idx)

        if melhor_rot:
            w, h = h, w

        ocupados.append((x, y, w, h))

        # novos espaços
        direita = (x + w, y, lw - w, h)
        baixo = (x, y + h, lw, lh - h)

        if direita[2] > 0 and direita[3] > 0:
            livres.append(direita)

        if baixo[2] > 0 and baixo[3] > 0:
            livres.append(baixo)

    return ocupados

# =========================
# DESENHAR CHAPA
# =========================
def desenhar_layout(pecas, W, H, titulo):
    fig, ax = plt.subplots()

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)

    area_total = W * H
    area_usada = 0

    for i, (x, y, w, h) in enumerate(pecas):
        rect = plt.Rectangle((x, y), w, h, fill=False)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, f"{w}x{h}", ha='center')
        area_usada += w * h

    aproveitamento = (area_usada / area_total) * 100
    sucata = 100 - aproveitamento

    ax.set_title(f"{titulo}\nAproveitamento: {aproveitamento:.1f}% | Sucata: {sucata:.1f}%")

    st.pyplot(fig)

# =========================
# LOTE
# =========================
if menu == "Lote de Produção":

    st.title("Lote de produção")

    # =====================
    # IMPORTAR PORTAS
    # =====================
    arquivo = st.file_uploader("Importar portas (Excel)", type=["xlsx"])

    if arquivo:
        df = pd.read_excel(arquivo)
        st.session_state.portas = df.to_dict("records")

        for i in range(len(st.session_state.portas)):
            st.session_state.quantidades[i] = 1

    # =====================
    # LISTA DE PORTAS
    # =====================
    for i, p in enumerate(st.session_state.portas):
        col1, col2, col3 = st.columns([3,1,1])

        with col1:
            st.write(f"Porta {p.get('codigo', i)}")

        with col2:
            if st.button("-", key=f"menos_{i}"):
                st.session_state.quantidades[i] = max(0, st.session_state.quantidades[i] - 1)

        with col3:
            if st.button("+", key=f"mais_{i}"):
                st.session_state.quantidades[i] += 1

        st.write(f"Qtd: {st.session_state.quantidades[i]}")

    # =====================
    # IMPORTAR CHAPAS
    # =====================
    st.subheader("Cadastrar chapas")

    arquivo_chapas = st.file_uploader("Importar chapas", type=["xlsx"], key="chapas")

    if arquivo_chapas:
        df_chapas = pd.read_excel(arquivo_chapas)
        st.session_state.chapas = df_chapas.to_dict("records")

    # =====================
    # GERAR CORTE
    # =====================
    if st.button("Gerar Corte"):

        pecas_por_tipo = {}

        # organiza peças
        for i, p in enumerate(st.session_state.portas):
            qtd = st.session_state.quantidades.get(i, 0)

            for _ in range(qtd):

                tipo = p.get("tipo", "incolor")
                largura = int(p.get("largura"))
                altura = int(p.get("altura"))

                if tipo not in pecas_por_tipo:
                    pecas_por_tipo[tipo] = []

                pecas_por_tipo[tipo].append((largura, altura))

        # gera para cada tipo
        for tipo, pecas in pecas_por_tipo.items():

            st.subheader(f"{tipo}")

            chapa = None

            for c in st.session_state.chapas:
                if c.get("tipo") == tipo:
                    chapa = c

            if not chapa:
                st.warning("Chapa não cadastrada")
                continue

            W = int(chapa["largura"])
            H = int(chapa["altura"])

            layout = otimizar_chapa(pecas, W, H)

            desenhar_layout(layout, W, H, f"{tipo}")
