import pygame as pg
import numpy as np
from numba import njit
from settings import *


def main():
    pg.init()
    screen = pg.display.set_mode(RES)
    running = True
    clock = pg.time.Clock()

    hres = HALF_WIDTH  # Resolução horizontal
    halfvres = HALF_HEIGHT  # Resolução vertical / 2

    mod = hres/60   # Fator de escala (60º fov)
    posx, posy, rot = PLAYER_POSX, PLAYER_POSX, PLAYER_ANGLE   # Posição x, y e rotação

    size = 25
    maph = np.random.choice([0, 0, 0, 1], (size, size))
    mapc = np.random.uniform(0, 1, (size, size, 3))

    frame = np.random.uniform(0, 1, (hres, halfvres * 2, 3))    # Frame

    # Carrega e armazena a imagem do céu em um array 3d
    sky = pg.surfarray.array3d(pg.transform.scale(pg.image.load('skybox2.jpg'), (360, halfvres * 2)))/255

    # Carrega e armazena a imagem do chão em um array 3d
    floor = pg.surfarray.array3d(pg.image.load('floor04.png'))/255

    # Carrega e armazena a imagem da parede em um array 3d
    wall = pg.surfarray.array3d(pg.image.load('wall01.jpg'))/255

    while running:  # Enquanto running for true
        for event in pg.event.get():    # Checa eventos
            if event.type == pg.QUIT:   # Se o evento for QUIT
                running = False     # Encerra o programa

        # Floor casting
        frame = new_frame(posx, posy, rot,
                          frame, sky, floor,
                          hres, halfvres, mod,
                          maph, mapc, size, wall)

        surf = pg.surfarray.make_surface(frame * 255)
        surf = pg.transform.scale(surf, RES)

        fps = int(clock.get_fps())
        pg.display.set_caption(" FPS: " + str(fps) +
                               " X: " + str(posx) +
                               " Y: " + str(posy) +
                               " Rotação: " + str(rot))

        posx, posy, rot = movement(posx, posy, rot, pg.key.get_pressed(), clock.tick())
        screen.blit(surf, (0, 0))
        pg.display.update()
        posx, posy, rot = movement(posx, posy, rot, pg.key.get_pressed(), clock.tick())

def movement(posx, posy, rot, keys, et):  # Movimentação do player

    if keys[pg.K_LEFT] or keys[ord('a')]:  # Rotaciona a camera para a direita
        rot -= PLAYER_ROT_SPEED * et

    if keys[pg.K_RIGHT] or keys[ord('d')]:  # Rotaciona a camera para a esquerda
        rot += PLAYER_ROT_SPEED * et

    if keys[pg.K_UP] or keys[ord('w')]:     # Move para frente
        posx, posy = posx + np.cos(rot) * PLAYER_SPEED * et, posy + np.sin(rot) * PLAYER_SPEED * et

    if keys[pg.K_DOWN] or keys[ord('s')]:   # Move para trás
        posx, posy = posx - np.cos(rot) * PLAYER_SPEED * et, posy - np.sin(rot) * PLAYER_SPEED * et

    return posx, posy, rot


@njit()
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, maph, mapc, size, wall):

    for i in range(hres):  # Percorre todas as colunas da tela

        rot_i = rot + np.deg2rad(i / mod - 30)  # Calcula o angulo de cada coluna no frame

        # Calcula o seno e o cosseno do angulo
        sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i / mod - 30))

        # Preenche o frame com a imagem do céu
        frame[i][:] = sky[int(np.rad2deg(rot_i) % 359)][:]

        x, y = posx, posy

        # Verifica se há paredes e calcula a distância
        while maph[int(x) % (size - 1)][int(y) % (size - 1)] == 0:
            x, y = x + 0.01 * cos, y + 0.01 * sin

        n = abs((x - posx) / cos)
        h = int(halfvres / (n * cos2 + 0.001))

        xx = int(x * 3 % 1 * 254)

        if x % 1 < 0.02 or x % 1 > 2.53:
            xx = int(y * 3 % 1 * 254)

        yy = np.linspace(0, 762, h * 2) % 254
        shade = 0.3 + 0.7 * (h / halfvres)  # Define o sombreamento da parede

        if shade > 1:
            shade = 1

        c = shade * mapc[int(x) % (size - 1)][int(y) % (size - 1)]

        for k in range(h * 2):

            if halfvres - h + k >= 0 and halfvres - h + k < 2 * halfvres:
                frame[i][halfvres - h + k] = c * wall[xx][int(yy[k])]

                if halfvres + 3 * h - k < 2 * halfvres:
                    frame[i][halfvres + 3 * h - k] = c * wall[xx][int(yy[k])]

        for j in range(halfvres - h):  # Percore todas as linhas da metade pra baixo da tela

            n = (halfvres / (halfvres - j)) / cos2  # Calcula a distância entre a origem e um determinado ponto
            x, y = posx + cos * n, posy + sin * n  # Calcula a posição x e y de cada píxel usando o seno eo cosseno
            xx, yy = int(x * 2 % 1 * 225), int(y * 2 % 1 * 225)

            shade = 0.2 + 0.8 * (1 - j / halfvres)  # Define o sombreamento do chão

            frame[i][halfvres * 2 - j - 1] = \
                 shade * (floor[xx][yy] + frame[i][halfvres * 2 - j - 1]) / 2  # Preenche o frame considerando o sombreamento

    return frame

if __name__ == '__main__':
    main()
    pg.quit()
