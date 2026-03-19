import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ==============================
# ESTADO
# ==============================
if "portas" not in st.session_state:
    st.session_state.portas = []

if "chapas" not in st.session_state:
    st.session_state.chapas = []

if "lote" not in st.session_state:
    st.session_state.lote = {}

# ==============================
# MENU (NÃO ALTERADO)
# ==============================
menu = st.sidebar.selectbox("Menu", ["Cadastro de Chapas", "Cadastro de Portas", "Lote de Produção"])

# ==============================
# CADASTRO DE CHAPAS
# ==============================
if menu == "Cadastro de Chapas":
    st.title("Cadastro de Chapas")

    nome = st.text_input("Nome da chapa")
    largura = st.number_input("Largura", value=6000)
    altura = st.number_input("Altura", value=3210)
    tipo = st.selectbox("Tipo", ["incolor", "tek"])

    if st.button("Adicionar chapa"):
        st.session_state.chapas.append({
            "nome": nome,
            "largura": largura,
            "altura": altura,
            "tipo": tipo
        })

    for i, c in enumerate(st.session_state.chapas):
        col1, col2 = st.columns([4,1])
        col1.write(f"{c['nome']} - {c['largura']}x{c['altura']} ({c['tipo']})")
        if col2.button("Remover", key=f"remover_chapa_{i}"):
            st.session_state.chapas.pop(i)
            st.rerun()

# ==============================
# CADASTRO DE PORTAS
# ==============================
if menu == "Cadastro de Portas":
    st.title("Cadastro de Portas")

    codigo = st.text_input("Código da porta")
    larg = st.number_input("Largura", value=600)
    alt = st.number_input("Altura", value=1700)
    tipo = st.selectbox("Tipo de vidro", ["incolor", "tek"])

    if st.button("Salvar porta"):
        st.session_state.portas.append({
            "codigo": codigo,
            "larg": larg,
            "alt": alt,
            "tipo": tipo
        })

    st.subheader("Portas cadastradas")

    for i, p in enumerate(st.session_state.portas):
        st.write(f"{p['codigo']} - {p['larg']}x{p['alt']} ({p['tipo']})")

# ==============================
# FUNÇÃO OTIMIZAÇÃO (MELHORADA)
# ==============================
def otimizar_chapa(pecas, W, H):
    pecas.sort(key=lambda x: x[0]*x[1], reverse=True)

    ocupados = []
    livres = [(0, 0, W, H)]

    for pw, ph in pecas:
        colocado = False

        for i, (x, y, lw, lh) in enumerate(livres):

            # normal
            if pw <= lw and ph <= lh:
                ocupados.append((x, y, pw, ph))

                livres.pop(i)
                livres.append((x + pw, y, lw - pw, ph))
                livres.append((x, y + ph, lw, lh - ph))

                colocado = True
                break

            # girado
            if ph <= lw and pw <= lh:
                ocupados.append((x, y, ph, pw))

                livres.pop(i)
                livres.append((x + ph, y, lw - ph, pw))
                livres.append((x, y + pw, lw, lh - pw))

                colocado = True
                break

        if not colocado:
            pass

    return ocupados

# ==============================
# LOTE DE PRODUÇÃO
# ==============================
if menu == "Lote de Produção":
    st.title("Lote de produção")

    # CONTROLE + -
    for p in st.session_state.portas:
        col1, col2, col3 = st.columns([4,1,1])

        if p["codigo"] not in st.session_state.lote:
            st.session_state.lote[p["codigo"]] = 0

        col1.write(f"{p['codigo']}")

        if col2.button("-", key=f"menos_{p['codigo']}"):
            if st.session_state.lote[p["codigo"]] > 0:
                st.session_state.lote[p["codigo"]] -= 1

        col3.write(st.session_state.lote[p["codigo"]])

        if col3.button("+", key=f"mais_{p['codigo']}"):
            st.session_state.lote[p["codigo"]] += 1

    if st.button("Gerar Corte"):
        for tipo in ["incolor", "tek"]:
            st.subheader(f"{tipo}")

            chapas = [c for c in st.session_state.chapas if c["tipo"] == tipo]

            if not chapas:
                st.warning("Chapa não cadastrada")
                continue

            chapa = chapas[0]

            pecas = []

            for p in st.session_state.portas:
                qtd = st.session_state.lote.get(p["codigo"], 0)

                if p["tipo"] == tipo:
                    for _ in range(qtd):
                        pecas.append((p["larg"], p["alt"]))

            if not pecas:
                continue

            ocupados = otimizar_chapa(pecas, chapa["largura"], chapa["altura"])

            fig, ax = plt.subplots(figsize=(10,5))

            ax.set_xlim(0, chapa["largura"])
            ax.set_ylim(0, chapa["altura"])

            area_usada = 0

            for x, y, w, h in ocupados:
                ax.add_patch(plt.Rectangle((x,y), w, h, fill=False))
                ax.text(x+w/2, y+h/2, f"{w}x{h}", ha="center", va="center")
                area_usada += w*h

            area_total = chapa["largura"] * chapa["altura"]

            aproveitamento = (area_usada / area_total) * 100
            sucata = 100 - aproveitamento

            st.pyplot(fig)

            st.success(f"Aproveitamento: {aproveitamento:.2f}%")
            st.error(f"Sucata: {sucata:.2f}%")
