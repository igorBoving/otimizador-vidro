import pandas as pd

def carregar_estrutura():

    df = pd.read_csv("estrutura_produto.csv")

    return df


def explodir_portas(pedido):

    estrutura = carregar_estrutura()

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

    return pd.DataFrame(vidros)
