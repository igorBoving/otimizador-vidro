import matplotlib.pyplot as plt

def desenhar_chapa(packer, largura_chapa, altura_chapa, indice):

    fig, ax = plt.subplots()

    abin = packer[indice]

    for rect in abin:

        x = rect.x
        y = rect.y
        w = rect.width
        h = rect.height

        codigo = rect.rid

        r = plt.Rectangle((x,y), w, h, fill=False)

        ax.add_patch(r)

        ax.text(
            x + w/2,
            y + h/2,
            f"{codigo}",
            ha="center",
            va="center",
            fontsize=9
        )

    ax.set_xlim(0, largura_chapa)
    ax.set_ylim(0, altura_chapa)

    ax.set_aspect('equal')

    return fig
