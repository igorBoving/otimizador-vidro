import pandas as pd
import os

arquivo = "historico_producao.csv"

def salvar_producao(dados):

    if os.path.exists(arquivo):

        df = pd.read_csv(arquivo)

        df = pd.concat([df, pd.DataFrame([dados])])

    else:

        df = pd.DataFrame([dados])

    df.to_csv(arquivo, index=False)

def carregar_historico():

    if os.path.exists(arquivo):

        return pd.read_csv(arquivo)

    else:

        return pd.DataFrame()
