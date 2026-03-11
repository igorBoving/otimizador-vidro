import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from rectpack import newPacker

st.title("Otimizador de Corte de Vidro")

# ----------------------------
# carregar estrutura
# ----------------------------

estrutura = pd.read_csv("estrutura_produto.csv")

# ----------------------------
# pedido operador
# ----------------------------

st.header("Pedido de portas")

porta = st.number_input("Código da porta", step=1)

quantidade = st.number_input("Quantidade", step=1)

if st.button("Calcular"):

    pedido = pd.DataFrame([{
        "porta":porta,
        "quantidade":quantidade
    }])

# ----------------------------
# explodir portas em vidros
# ----------------------------

    vidros = []

    for _, p in pedido.iterrows():

        porta = p["porta"]
        qtd_portas = p["quantidade"]

        componentes = estrutura[estrutura["porta"] == porta]

        for _, c in componentes.iterrows():

            qtd_vidro = qtd_portas * c["quantidade"]

            vidros.append({

                "codigo": c["vidro_codigo"],
                "tipo": c["tipo_vidro"],
                "largura": c["largura"],
                "altura": c["altura"],
                "quantidade": qtd_vidro

            })

    df_vidros = pd.DataFrame(vidros)

# ----------------------------
# separar vidros
# ----------------------------

    insulado = df_vidros[df_vidros["tipo"]=="insulado"]
    tek = df_vidros[df_vidros["tipo"]=="tek"]

# ----------------------------
# função otimização
# ----------------------------

    def otimizar(df, largura_chapa, altura_chapa):

        packer = newPacker(rotation=True)

        for _, r in df.iterrows():

            for i in range(int(r["quantidade"])):

                packer.add_rect(
                    r["largura"],
                    r["altura"],
                    rid=r["codigo"]
                )

        packer.add_bin(largura_chapa, altura_chapa, float("inf"))

        packer.pack()

        return packer

# ----------------------------
# otimizar insulado
# ----------------------------

    packer_insulado = otimizar(insulado,6000,3210)

# ----------------------------
# otimizar tek
# ----------------------------

    packer_tek = otimizar(tek,3300,2134)

# ----------------------------
# resultados
# ----------------------------

    st.header("Resultado")

    st.subheader("Vidro INSULADO")

    st.write("Chapas necessárias:",len(packer_insulado))

    st.subheader("Vidro TEK")

    st.write("Chapas necessárias:",len(packer_tek))

# ----------------------------
# layout
# ----------------------------

    indice = st.number_input(
        "Mostrar chapa insulado",
        0,
        len(packer_insulado)-1,
        0
    )

    fig, ax = plt.subplots()

    abin = packer_insulado[indice]

    for rect in abin:

        x=rect.x
        y=rect.y
        w=rect.width
        h=rect.height

        r=plt.Rectangle((x,y),w,h,fill=False)

        ax.add_patch(r)

        ax.text(
            x+w/2,
            y+h/2,
            rect.rid,
            ha="center"
        )

    ax.set_xlim(0,6000)
    ax.set_ylim(0,3210)

    ax.set_aspect('equal')

    st.pyplot(fig)
