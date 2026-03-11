import matplotlib.pyplot as plt

def desenhar_chapa(packer, largura_chapa, altura_chapa, indice_chapa=0):

    fig, ax = plt.subplots()

    abin = packer[indice_chapa]

    for rect in abin:

        x = rect.x
        y = rect.y
        w = rect.width
        h = rect.height

        r = plt.Rectangle((x, y), w, h, fill=False)

        ax.add_patch(r)

    ax.set_xlim(0, largura_chapa)
    ax.set_ylim(0, altura_chapa)

    ax.set_aspect('equal')

    return fig
