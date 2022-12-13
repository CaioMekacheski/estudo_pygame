import pygame as pg
import numpy as np


def main():
    pg.init()
    screen = pg.display.set_mode([800, 600])
    running = True
    clock = pg.time.Clock()

    hres = 120  # Resolução horizontal
    halfvres = 100  # Resolução vertical / 2

    mod = hres/60   # Fator de escala (60º fov)
    posx, posy, rot = 0, 0, 0   # Posição x, y e rotação

    frame = np.random.uniform(0, 1, (hres, halfvres * 2, 3))    # Frame

    sky = pg.image.load('sky01.png')    # Carrega a imagem do céu
    sky = pg.surfarray.array3d(pg.transform.scale(sky, (360, halfvres * 2)))  # Armazena a imagem em um array 3d

    floor = pg.image.load('floor01.png')  # Carre a imagem do chão
    floor = pg.surfarray.array3d(floor)  # Armazena a imagem em um array 3d

    while running:  # Enquanto running for true
        for event in pg.event.get():    # Checa eventos
            if event.type == pg.QUIT:   # Se o evento for QUIT
                running = False     # Encerra o programa

        # Floor casting
        for i in range(hres):   #  Percorre todas as colunas da tela
            rot_i = rot + np.deg2rad(i / mod - 30)  # Calcula o angulo de cada coluna no frame
            sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i / mod - 30))     # Calcula o seno e o
                                                                                                # cosseno do angulo
            frame[i][:] = sky[int(np.rad2deg(rot_i) % 359)][:] / 255  # Preenche o frame com a imagem correspondente

            for j in range(halfvres):   # Percore todas as linhas da metade pra baixo da tela
                n = (halfvres / (halfvres - j)) / cos2 # Calcula a distância entre a origem e um determinado ponto
                x, y = posx + cos * n, posy + sin * n  # Calcula a posição x e y de cada píxel usando o seno eo cosseno
                xx, yy = int(x * 2 % 1 * 100), int(y * 2 % 1 * 100)

                shade = 0.2 + 0.8 * (1 - j / halfvres) # Define o sombreamento do chão
                frame[i][halfvres * 2 - j - 1] = shade * floor[xx][yy] / 255  # Preenche o frame considerando o sombreamento

                """if int(x) % 2 == int(y) % 2:  # Se a parte inteira do dobro de x for igual a parte inteira do dobro de y
                    frame[i][halfvres * 2 - j - 1] = [0, 0, 0]  # Pinta o pixel de preto
                else:
                    frame[i][halfvres * 2 - j - 1] = [1, 1, 1]  # Senão pinta o píxel de branco
"""

        surf = pg.surfarray.make_surface(frame * 255)
        surf = pg.transform.scale(surf, [800, 600])
        screen.blit(surf, (0, 0))
        pg.display.update()
        posx, posy, rot = movement(posx, posy, rot, pg.key.get_pressed(), clock.tick(60))

def movement(posx, posy, rot, keys, et):  # Movimentação do player

    if keys[pg.K_LEFT] or keys[ord('a')]:  # Rotaciona a camera para a direita
        rot -= 0.001 * et

    if keys[pg.K_RIGHT] or keys[ord('d')]:  # Rotaciona a camera para a esquerda
        rot += 0.001 * et

    if keys[pg.K_UP] or keys[ord('w')]:     # Move para frente
        posx, posy = posx + np.cos(rot) * 0.001 * et, posy + np.sin(rot) * 0.001 * et

    if keys[pg.K_DOWN] or keys[ord('s')]:   # Move para trás
        posx, posy = posx - np.cos(rot) * 0.001 * et, posy - np.sin(rot) * 0.001 * et


    return posx, posy, rot


if __name__ == '__main__':
    main()
    pg.quit()
