# Atualizado 22/12/2022

import pygame as pg
import numpy as np
from numba import njit

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    running = True
    clock = pg.time.Clock()

    hres = 120  # horizontal resolution
    halfvres = 100  # vertical resolution/2

    mod = hres / 60  # scaling factor (60° fov)
    posx, posy, rot = 0, 0, 0
    frame = np.random.uniform(0, 1, (hres, halfvres * 2, 3))
    sky = pg.image.load('skybox2.jpg')
    sky = pg.surfarray.array3d(pg.transform.scale(sky, (360, halfvres * 2))) / 255
    floor = pg.surfarray.array3d(pg.image.load('floor04.png')) / 255
    sprite = pg.image.load('spr_test01.png')
    sprsize = np.asarray(sprite.get_size())
    enemies = np.random.uniform(0, 50, (100, 4))


    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        frame = new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod)

        surf = pg.surfarray.make_surface(frame * 255)
        surf = pg.transform.scale(surf, (800, 600))

        #p_mouse = pg.mouse.get_pos()  # Posição do mouse

        #scaling = sprsize * abs((p_mouse[1] - 300) / 300) * 10  #Define o tamanho
                                                                 # conforme a distância
        #sprsurf = pg.transform.scale(sprite, scaling)  # Prepara para imprimir na tela

        #surf.blit(sprsurf, p_mouse - scaling / 2)  # Imprime na tela

        for en in range(100):

            enx, eny = enemies[en][0], enemies[en][1]
            angle = np.arctan((eny - posy) / (enx - posx))  # Calcula o ângulo entre a posição do
                                                            # player e da sprite
            if abs(posx + np.cos(angle) - enx) > abs(posx - enx):  # Checa se a sprite está no
                                                                  # campo de visão do player
                angle = (angle - np.pi) % (2 * np.pi)

            anglediff = (rot - angle) % (2 * np.pi)

            if anglediff > 11 * np.pi / 6 or anglediff < np.pi / 6:  # Se a sprite estiver no campo
                dist = np.sqrt((posx - enx) ** 2 + (posy - eny) ** 2)  # Define a distância
                enemies[en][2], enemies[en][3] = anglediff, 1 / dist

            else:
                enemies[en][3] = 999

        enemies = enemies[enemies[:, 3].argsort()]

        for en in range(100):

            if enemies[en][3] > 10:
                break

            cos2 = np.cos(enemies[en][2])  # Corrige o efeito 'olho de peixe'
            scaling = min(enemies[en][3], 2) / cos2  # Define a escala da sprite
            vert = 300 + 300 * scaling - scaling * sprsize[1] / 2
            hor = 400 - 800 * np.sin(enemies[en][2]) - sprsize[0] / 2
            sprsurf = pg.transform.scale(sprite, scaling * sprsize * 30)  # Prepara para imprimir
                                                                              # na tela
            surf.blit(sprsurf, (hor, vert))  # Imprime na tela



        fps = int(clock.get_fps())
        pg.display.set_caption("Pycasting maze - FPS: " + str(fps))

        screen.blit(surf, (0, 0))
        pg.display.update()

        posx, posy, rot = movement(posx, posy, rot, pg.key.get_pressed(), clock.tick())


def movement(posx, posy, rot, keys, et):
    if keys[pg.K_LEFT] or keys[ord('a')]:
        rot = rot - 0.001 * et

    if keys[pg.K_RIGHT] or keys[ord('d')]:
        rot = rot + 0.001 * et

    if keys[pg.K_UP] or keys[ord('w')]:
        posx, posy = posx + np.cos(rot) * 0.002 * et, posy + np.sin(rot) * 0.002 * et

    if keys[pg.K_DOWN] or keys[ord('s')]:
        posx, posy = posx - np.cos(rot) * 0.002 * et, posy - np.sin(rot) * 0.002 * et

    return posx, posy, rot


@njit()
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod):
    for i in range(hres):
        rot_i = rot + np.deg2rad(i / mod - 30)
        sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i / mod - 30))
        frame[i][:] = sky[int(np.rad2deg(rot_i) % 359)][:]
        for j in range(halfvres):
            n = (halfvres / (halfvres - j)) / cos2
            x, y = posx + cos * n, posy + sin * n
            xx, yy = int(x * 2 % 1 * 99), int(y * 2 % 1 * 99)

            shade = 0.2 + 0.8 * (1 - j / halfvres)

            frame[i][halfvres * 2 - j - 1] = shade * floor[xx][yy]

    return frame


if __name__ == '__main__':
    main()
    pg.quit()
