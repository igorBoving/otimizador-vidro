import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# =========================
# SESSION STATE
# =========================
if "portas" not in st.session_state:
    st.session_state.portas = []

if "chapas" not in st.session_state:
    st.session_state.chapas = []

if "quantidades" not in st.session_state:
    st.session_state.quantidades = {}

# =========================
# MENU (MANTIDO SIMPLES)
# =========================
menu = st.sidebar.selectbox("Menu", ["Lote de Produção"])

# =========================
# OTIMIZAÇÃO TETRIS MELHORADA
# =========================
def otimizar_chapa(pecas, W, H):

    pecas = sorted(pecas, key=lambda x: x[0]*x[1], reverse=True)

    livres = [(0, 0, W, H)]
    ocupados = []

    for w, h in pecas:
        melhor = None

        for i, (x, y, lw, lh) in enumerate(livres):

            # normal
            if w <= lw and h <= lh:
                sobra = (lw*lh) - (w*h)
                if melhor is None or sobra < melhor[0]:
                    melhor = (sobra, i, x, y, w, h)

            # rotacionado
            if h <= lw and w <= lh:
                sobra = (lw*lh) - (h*w)
                if melhor is None or sobra < melhor[0]:
                    melhor = (sobra, i, x, y, h, w)

        if melhor is None:
            continue

        _, idx, x, y, w, h = melhor

        lw, lh = livres[idx][2], livres[idx][3]
        livres.pop(idx)

        ocupados.append((x, y, w, h))

        # dividir espaço
        direita = (x + w, y, lw - w, h)
        baixo = (x, y + h, lw, lh - h)

        if direita[2] > 0 and direita[3] > 0:
            livres.append(direita)

        if baixo[2] > 0 and baixo[3] > 0:
            livres.append(baixo)

    return ocupados

# =========================
# DESENHO
# =========================
def desenhar(pecas, W, H, titulo):

    fig, ax = plt.subplots()

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)

    area_usada = 0

    for x, y, w, h in pecas:
        rect = plt.Rectangle((x, y), w, h, fill=False)
        ax.add_patch(rect)

        ax.text(x + w/2, y + h/2, f"{int(w)}x{int(h)}",
                ha="center", va="center", fontsize=8)

        area_usada += w * h

    area_total = W * H

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
    arquivo = st.file_uploader("Importar portas", type=["xlsx"], key="upload_portas")

    if arquivo:
        df = pd.read_excel(arquivo)
        st.session_state.portas = df.to_dict("records")

        for i in range(len(st.session_state.portas)):
            st.session_state.quantidades[i] = 1

    # =====================
    # LISTA
    # =====================
    for i, p in enumerate(st.session_state.portas):

        col1, col2, col3 = st.columns([4,1,1])

        with col1:
            st.write(f"Porta {p.get('codigo', i)}")

        with col2:
            if st.button("-", key=f"menos_{i}"):
                st.session_state.quantidades[i] = max(
                    0, st.session_state.quantidades.get(i, 0) - 1
                )

        with col3:
            if st.button("+", key=f"mais_{i}"):
                st.session_state.quantidades[i] = st.session_state.quantidades.get(i, 0) + 1

        st.write(f"Qtd: {st.session_state.quantidades.get(i,0)}")

    # =====================
    # IMPORTAR CHAPAS
    # =====================
    st.subheader("Importar chapas")

    arquivo_chapas = st.file_uploader("Importar chapas", type=["xlsx"], key="upload_chapas")

    if arquivo_chapas:
        df_chapas = pd.read_excel(arquivo_chapas)
        st.session_state.chapas = df_chapas.to_dict("records")

    # =====================
    # GERAR CORTE
    # =====================
    if st.button("Gerar Corte"):

        pecas_por_tipo = {}

        for i, p in enumerate(st.session_state.portas):

            qtd = st.session_state.quantidades.get(i, 0)

            for _ in range(qtd):

                tipo = str(p.get("tipo", "incolor")).lower()
                larg = int(p.get("largura"))
                alt = int(p.get("altura"))

                if tipo not in pecas_por_tipo:
                    pecas_por_tipo[tipo] = []

                pecas_por_tipo[tipo].append((larg, alt))

        for tipo, pecas in pecas_por_tipo.items():

            st.subheader(f"Vidro: {tipo}")

            chapa = None

            for c in st.session_state.chapas:
                if str(c.get("tipo")).lower() == tipo:
                    chapa = c

            if not chapa:
                st.warning(f"Sem chapa para {tipo}")
                continue

            W = int(chapa["largura"])
            H = int(chapa["altura"])

            layout = otimizar_chapa(pecas, W, H)

            desenhar(layout, W, H, f"{tipo}")
