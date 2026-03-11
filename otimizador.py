from rectpack import newPacker

def otimizar_corte(df, largura_chapa, altura_chapa):

    packer = newPacker(rotation=True)

    for _, r in df.iterrows():
        packer.add_rect(r["largura"], r["altura"])

    packer.add_bin(largura_chapa, altura_chapa, float("inf"))

    packer.pack()

    return packer
