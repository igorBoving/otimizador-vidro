import pandas as pd
import os

arquivo_modelos = "modelos_portas.csv"

def carregar_modelos():
    if os.path.exists(arquivo_modelos):
        return pd.read_csv(arquivo_modelos)
    else:
        return pd.DataFrame(columns=["codigo","largura","altura"])

def salvar_modelo(codigo, largura, altura):

    df = carregar_modelos()

    novo = pd.DataFrame([{
        "codigo": codigo,
        "largura": largura,
        "altura": altura
    }])

    df = pd.concat([df, novo], ignore_index=True)

    df.to_csv(arquivo_modelos, index=False)
