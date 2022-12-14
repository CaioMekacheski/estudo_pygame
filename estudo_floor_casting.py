# Atualizado 14/12/2022

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

    frame = np.random.uniform(0, 1, (hres, halfvres * 2, 3))    # Frame

    # Carrega e armazena a imagem em um array 3d
    sky = pg.surfarray.array3d(pg.transform.scale(pg.image.load('skybox.jpg'), (360, halfvres * 2)))/255

    # Carrega e armazena a imagem em um array 3d
    floor = pg.surfarray.array3d(pg.image.load('floor04.png'))/255

    while running:  # Enquanto running for true
        for event in pg.event.get():    # Checa eventos
            if event.type == pg.QUIT:   # Se o evento for QUIT
                running = False     # Encerra o programa

        # Floor casting
        frame = new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod)


        surf = pg.surfarray.make_surface(frame * 255)
        surf = pg.transform.scale(surf, RES)

        fps = int(clock.get_fps())
        pg.display.set_caption("Pycasting maze - FPS: " + str(fps))
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
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod):

    for i in range(hres):  # Percorre todas as colunas da tela

        rot_i = rot + np.deg2rad(i / mod - 30)  # Calcula o angulo de cada coluna no frame
        sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i / mod - 30))  # Calcula o seno e o
        # cosseno do angulo
        frame[i][:] = sky[int(np.rad2deg(rot_i) % 359)][:]  # Preenche o frame com a imagem correspondente

        for j in range(halfvres):  # Percore todas as linhas da metade pra baixo da tela

            n = (halfvres / (halfvres - j)) / cos2  # Calcula a distância entre a origem e um determinado ponto
            x, y = posx + cos * n, posy + sin * n  # Calcula a posição x e y de cada píxel usando o seno eo cosseno
            xx, yy = int(x * 2 % 1 * 225), int(y * 2 % 1 * 225)
            shade = 0.2 + 0.8 * (1 - j / halfvres)  # Define o sombreamento do chão
            frame[i][halfvres * 2 - j - 1] = shade * floor[xx][yy]  # Preenche o frame considerando o sombreamento

    return frame

if __name__ == '__main__':
    main()
    pg.quit()
