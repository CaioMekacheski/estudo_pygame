# Atualizado 5/01/2023 - 03:07

import pygame as pg
from numba import njit
from settings import *


def main():
    pg.init()
    screen = pg.display.set_mode(RES)
    running = True
    clock = pg.time.Clock()

    pg.mouse.set_visible(False)  # Poteiro do mouse invisível
    pg.event.set_grab(1)  # O mouse não sai da janela

    hres = HOR_RES  # Resolução horizontal
    halfvres = HALF_VER_RES  # Resolução vertical / 2

    mod = MOD  # Fator de escala (60º fov)

    # Mapa
    size = SIZE
    posx, posy, rot, maph, mapc, exitx, exity = gen_map(size)

    frame = np.random.uniform(0, 1, (hres, halfvres * 2, 3))    # Frame

    # Carrega e armazena a imagem do céu em um array 3d
    image_width = 360
    escala_cor = 255
    sky = pg.surfarray.array3d(pg.transform.smoothscale
                               (pg.image.load('skybox2.jpg'),
                                (image_width * 2, halfvres * 2))) / escala_cor

    # Carrega e armazena a imagem do chão, da parede em um array 3d
    floor = pg.surfarray.array3d(pg.image.load('floor04.png')) / escala_cor

    wall = pg.surfarray.array3d(pg.image.load('wall01.jpg')) / escala_cor

    # Carrega e a sprite do inimigo e define o tamanho da sprite
    sprites, sprsize, sword, sword_spr, pistol, pistol_spr = get_sprites(hres)

    # Gera os inimigos no mapa
    enemy_num = 10
    enemies = spawn_enemies(enemy_num, maph, size)

    while running:  # Enquanto running for true

        ticks = pg.time.get_ticks() / 200
        er = clock.tick() / 25

        # Se o player encontrar a saída encerra o jogo
        if int(posx) == exitx and int(posy) == exity and enemy_num <= 1:

            print("Você encontrou a saída! Parabéns!!")
            running = False

        elif int(posx) == exitx and int(posy) == exity and enemy_num > 0:

            pg.display.set_caption(' Ainda há inimigos! ')

        else:
            # Imprime o fps, a posição x e y, a rotação na borda superior da janela e quantidade
            # de inimigos restante
            fps = int(clock.get_fps())
            pg.display.set_caption(" FPS: " + str(fps) +
                                   " X: " + str(int(posx)) +
                                   " Y: " + str(int(posy)) +
                                   " Rotação: " + str(int(rot)) +
                                   "   Inimigos: " + str(int(enemy_num)))
        # Checa eventos
        for event in pg.event.get():
            # Encerra o jogo se Esc for presionado
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:

                running = False

            # Movimenta a espada
            if sword_spr < 1 and event.type == pg.MOUSEBUTTONDOWN:

                sword_spr = 1

            # Movimenta a pistola
            if pistol_spr < 1 and event.type == pg.MOUSEBUTTONDOWN:

                for spr in range(0, 3, 1):

                    pistol_spr = spr




        # Cria o frame
        frame = new_frame(posx, posy, rot,
                          frame, sky, floor,
                          hres, halfvres, mod,
                          maph, mapc, size,
                          wall, exitx, exity)

        # Cria uma superfície para receber o frame e o adapta conforme a altura e largura da tela
        surf = pg.surfarray.make_surface(frame * escala_cor)

        # Cria e desenha, os inimigos e a espada
        enemies = sort_sprites(posx, posy, rot, enemies, maph, size, er / 5)
        surf, en = draw_sprites(surf, sprites, enemies, sprsize,
                                hres, halfvres, ticks, sword, sword_spr, pistol, pistol_spr)

        surf = pg.transform.scale(surf, RES)

        # Retorna a espada para posição inicial
        if int(sword_spr) > 0:

            if sword_spr == 1 and 1 < enemies[en][3] < 10:

                enemies[en][0] = 0
                enemy_num -= 1

            sword_spr = (sword_spr + er * 5) % 4

        if int(pistol_spr) > 0:
            pistol_spr = 0

        # Define as cordenadas x e y e a rotação do player
        posx, posy, rot = movement(posx, posy, rot, pg.key.get_pressed(), maph, clock.tick())
        screen.blit(surf, (0, 0))
        pg.display.update()

# Movimento do player
def movement(posx, posy, rot, keys, maph, et):  # Movimentação do player

    # Define as coordenadas x e y
    x, y, diag = posx, posy, rot

    #Configura a rotação da camera conforme a posição do mouse
    p_mouse = pg.mouse.get_rel()
    rot = rot + np.clip((p_mouse[0]) / 200, -0.2, 0.2)

    if keys[pg.K_LEFT] or keys[ord('a')]:  # Move para direita
        x, y = posx + np.sin(rot) * PLAYER_SPEED * et, \
               posy - np.cos(rot) * PLAYER_SPEED * et

    if keys[pg.K_RIGHT] or keys[ord('d')]:  # Move para esquerda
        x, y = posx - np.sin(rot) * PLAYER_SPEED * et, \
               posy + np.cos(rot) * PLAYER_SPEED * et

    if keys[pg.K_UP] or keys[ord('w')]:     # Move para frente
        x, y, diag = posx + np.cos(rot) * PLAYER_SPEED * et, \
                     posy + np.sin(rot) * PLAYER_SPEED * et, 1

    if keys[pg.K_DOWN] or keys[ord('s')]:   # Move para trás
        x, y, diag = posx - np.cos(rot) * PLAYER_SPEED * et, \
                     posy - np.sin(rot) * PLAYER_SPEED * et, 1

    # Verifica se há paredes no caminho
    if not (maph[int(x - 0.1)][int(y)] or maph[int(x + 0.1)][int(y)] or
            maph[int(x)][int(y - 0.1)] or maph[int(x)][int(y + 0.1)]):
        posx, posy = x, y

    elif not (maph[int(posx - 0.1)][int(y)] or maph[int(posx + 0.1)][int(y)] or
              maph[int(posx)][int(y - 0.1)] or maph[int(posx)][int(y + 0.1)]):
        posy = y

    elif not (maph[int(x - 0.1)][int(posy)] or maph[int(x + 0.1)][int(posy)] or
              maph[int(x)][int(posy - 0.1)] or maph[int(x)][int(posy + 0.1)]):
        posx = x

    return posx, posy, rot

# Criação do mapa
def gen_map(size):
    mapc = np.random.uniform(0, 1, (size, size, 3))
    maph = np.random.choice([0, 0, 0, 0, 1, 1], (size, size))
    maph[0, :], maph[size - 1, :], maph[:, 0], maph[:, size - 1] = (1, 1, 1, 1)

    # Define as coordendas
    posx, posy, rot = PLAYER_POSX, PLAYER_POSY + .5, PLAYER_ANGLE
    x, y = int(posx), int(posy)
    maph[x][y] = 0
    count = 0

    # Define a posição da saída no mapa
    while True:
        testx, testy = (x, y)
        if np.random.uniform() > 0.5:
            testx = testx + np.random.choice([-1, 1])
        else:
            testy = testy + np.random.choice([-1, 1])

        if 0 < testx < size - 1 and 0 < testy < size - 1:

            if maph[testx][testy] == 0 or count > 5:
                count = 0
                x, y = (testx, testy)
                maph[x][y] = 0

                if x == size - 2:
                    exitx, exity = (x, y)
                    break
            else:
                count = count + 1
    return posx, posy, rot, maph, mapc, exitx, exity


# Criação do frame
@njit()
def new_frame(posx, posy, rot,
              frame, sky, floor,
              hres, halfvres, mod,
              maph, mapc, size,
              wall, exitx, exity):

    for i in range(hres):  # Percorre todas as colunas da tela

        rot_i = rot + np.deg2rad(i / mod - 30)  # Calcula o angulo de cada coluna no frame

        # Calcula o seno e o cosseno do angulo
        sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i / mod - 30))

        # Preenche o frame com a imagem do céu
        frame[i][:] = sky[int(np.rad2deg(rot_i) % 359)][:]

        # Define as coordenadas x e y
        x, y = posx, posy

        # Verifica se há paredes e calcula a distância
        while maph[int(x) % (size - 1)][int(y) % (size - 1)] == 0:
            x, y = x + 0.01 * cos, y + 0.01 * sin

        n = abs((x - posx) / cos)
        h = int(halfvres / (n * cos2 + 0.001))

        xx = int(x * 3 % 1 * WALL_WIDTH - 1)

        if x % 1 < 0.02 or x % 1 > 0.98:
            xx = int(y * 3 % 1 * WALL_WIDTH - 1)

        yy = np.linspace(0, 3, h * 2) * (WALL_WIDTH - 1) % (WALL_WIDTH - 1)
        shade = 0.3 + 0.7 * (h / halfvres)  # Define o sombreamento da parede

        if shade > 1:   # Limita o sombreamento
            shade = 1

        # Verifica se há sombra em paredes perpendiculares
        ash = 0

        if maph[int(x - 0.33) % (size - 1)][int(y - 0.33) % (size - 1)]:
            ash = 1

        if maph[int(x - 0.01) % (size - 1)][int(y - 0.01) % (size - 1)]:
            shade, ash = shade * 0.5, 0

        c = shade * mapc[int(x) % (size - 1)][int(y) % (size - 1)]

        for k in range(h * 2):

            if halfvres - h + k >= 0 and halfvres - h + k < 2 * halfvres:

                if ash and 1 - k / (2 * h) < 1 - xx / WALL_WIDTH:
                    c, ash = 0.5 * c, 0

                frame[i][halfvres - h + k] = c * wall[xx][int(yy[k])]

                if halfvres + 3 * h - k < 2 * halfvres:
                    frame[i][halfvres + 3 * h - k] = c * wall[xx][int(yy[k])]

        for j in range(halfvres - h):  # Percore todas as linhas da metade pra baixo da tela

            n = (halfvres / (halfvres - j)) / cos2  # Calcula a distância entre a origem e um determinado ponto
            x, y = posx + cos * n, posy + sin * n  # Calcula a posição x e y de cada píxel usando o seno eo cosseno
            xx, yy = int(x * 2 % 1 * 225), int(y * 2 % 1 * 225)

            shade = 0.2 + 0.8 * (1 - j / halfvres)  # Define o sombreamento do chão

            if maph[int(x - 0.33) % (size - 1)][int(y - 0.33) % (size - 1)]:
                shade = shade * 0.5

            elif ((maph[int(x - 0.33) % (size - 1)][int(y) % (size - 1)] and y % 1 > x % 1) or
                  (maph[int(x) % (size - 1)][int(y - 0.33) % (size - 1)] and x % 1 > y % 1)):

                shade = shade * 0.5

            # Preenche o frame considerando o sombreamento e o reflexo
            frame[i][halfvres * 2 - j - 1] = \
                shade * (floor[xx][yy] + frame[i][halfvres * 2 - j - 1]) / 2

            # frame[i][halfvres * 2 - j - 1] = shade * floor[xx][yy]

            # Cria a saída do labirinto
            if int(x) == exitx and int(y) == exity \
                    and (x % 1 - 0.5) ** 2 + (y % 1 - 0.5) ** 2 < 0.2:

                ee = j / (10 * halfvres)
                frame[i][j:2 * halfvres - j] = \
                    (ee * np.ones(3) + frame[i][j:2 * halfvres - j]) / (1 + ee)

    return frame

# Define aleatoriamente os tipos e as posições dos inimigos
@njit()
def sort_sprites(posx, posy, rot, enemies, maph, size, er):

    for en in range(len(enemies)):

        # Movimentação dos inimigos
        cos, sin = er * np.cos(enemies[en][6]), er * np.sin(enemies[en][6])
        # Define as coordenadas x e y
        enx, eny = enemies[en][0] + cos, enemies[en][1] + sin
        # Checa se há uma parede no caminho
        if (maph[int(enx - 0.2) % (size - 1)][int(eny - 0.2) % (size - 1)] or
            maph[int(enx - 0.2) % (size - 1)][int(eny + 0.2) % (size - 1)] or
            maph[int(enx + 0.2) % (size - 1)][int(eny - 0.2) % (size - 1)] or
            maph[int(enx + 0.2) % (size - 1)][int(eny + 0.2) % (size - 1)]):
            # Se for o caso, muda a direção de forma aleatória
            enx, eny = enemies[en][0], enemies[en][1]
            enemies[en][6] = enemies[en][6] + np.random.uniform(0.5, 0.5)

        else:
            # Senão continua na mesma direção
            enemies[en][0], enemies[en][1] = enx, eny

        # Calcula o ângulo entre a posição do player e da sprite
        angle = np.arctan((eny - posy) / (enx - posx))
        # Checa se a sprite está no campo de visão do player
        if abs(posx + np.cos(angle) - enx) > abs(posx - enx):

            angle = (angle - np.pi) % (2 * np.pi)

        angle2 = (rot - angle) % (2 * np.pi)

        if angle2 > 10.5 * np.pi / 6 or angle2 < 1.5 * np.pi / 6:  # Se a sprite estiver no campo

            # Define a distância, o ângulo, o seno, o cosseno, e as coordenadas x e y
            dir2p = ((enemies[en][6] - angle - 3 * np.pi / 4) % (2 * np.pi)) / (np.pi / 2)
            enemies[en][2] = angle2
            enemies[en][7] = dir2p
            enemies[en][3] = 1 / np.sqrt((enx - posx) ** 2 + (eny - posy) ** 2 + 1e-16)

            cos, sin = (posx - enx) * enemies[en][3], (posy - eny) * enemies[en][3]
            x, y = enx, eny

            for i in range(int((1 / enemies[en][3]) / 0.05)):

                x, y = x + 0.05 * cos, y + 0.05 * sin

                # Checa se o inimigo esta dentro do mapa
                if (maph[int(x - 0.2 * cos) % (size - 1)][int(y) % (size - 1)] or
                    maph[int(x) % (size - 1)][int(y - 0.2 * sin) % (size - 1)]):

                    enemies[en][3] = 9999
                    break
        else:
            enemies[en][3] = 9999
    #if enemies[en][3] > 1:
    enemies = enemies[enemies[:, 3].argsort()]

    return enemies

# Gera os inimigos no mapa
def spawn_enemies(number, maph, msize):

    enemies = []

    for i in range(number):

        x, y = np.random.uniform(1, msize-2), np.random.uniform(1, msize-2)

        # Checa se esta no mapa
        while (maph[int(x - 0.1) % (msize - 1)][int(y - 0.1) % (msize - 1)] or
               maph[int(x - 0.1) % (msize - 1)][int(y + 0.1) % (msize - 1)] or
               maph[int(x + 0.1) % (msize - 1)][int(y - 0.1) % (msize - 1)] or
               maph[int(x + 0.1) % (msize - 1)][int(y + 0.1) % (msize - 1)]):

            # Se estiver define as coordenadas x e y
            x, y = np.random.uniform(1, msize -1), np.random.uniform(1, msize -1)

        # Define o angulo, a distância, a direção, o tipo, e o tamanho
        angle2p, invdist2p, dir2p = 0, 0, 0
        entype = np.random.choice([0, 1])
        direction = np.random.uniform(0, 2 * np.pi)
        size = np.random.uniform(7, 10)
        enemies.append([x, y, angle2p, invdist2p, entype, size, direction, dir2p])

    return np.asarray(enemies)

#Carrega as sprites e a organiza em uma lista
def get_sprites(hres):

    # Carrega a imagem da espada e dos inimigos
    # e cria as listas que irão receber essas imagens
    sheet = pg.image.load('zombie_n_skeleton.png').convert_alpha()
    sprites = [[], []]

    swordsheet = pg.image.load('sword1.png').convert_alpha()
    sword = []

    pistolsheet = pg.image.load('pistol01.png').convert_alpha()
    pistol = []

    # Armazena as imagens em suas respectivas listas

    for k in range(4):

        subpistol = pg.Surface.subsurface(pistolsheet, (k * 99.5, 0, 99.5, 138))
        pistol.append(pg.transform.smoothscale(subpistol, (hres / 2, int(hres * 0.5))))

    for i in range(3):

        subsword = pg.Surface.subsurface(swordsheet, (i * 800, 0, 800, 600))
        sword.append(pg.transform.smoothscale(subsword, (hres, int(hres * 0.75))))

        xx = i * 32
        sprites[0].append([])
        sprites[1].append([])

        for j in range(4):
            yy = j * 100
            sprites[0][i].append(pg.Surface.subsurface(sheet, (xx, yy, 32, 100)))
            sprites[1][i].append(pg.Surface.subsurface(sheet, (xx + 96, yy, 32, 100)))

    sprsize = np.asarray(sprites[0][1][0].get_size()) * hres / 800

    sword.append(sword[1])
    sword_spr = 0

    pistol.append(pistol[1])
    pistol_spr = 0

    return sprites, sprsize, sword, sword_spr, pistol, pistol_spr

# Configura e desenha as sprites
def draw_sprites(surf, sprites, enemies, sprsize,
                 hres, halfvres, ticks, sword, sword_spr, pistol, pistol_spr):

    cycle = int(ticks) % 3

    for en in range(len(enemies)):

        if enemies[en][3] > 20:

            break

        types, dir2p = int(enemies[en][4]), int(enemies[en][7])
        cos2 = np.cos(enemies[en][2])
        scale = min(enemies[en][3], 2) * sprsize * enemies[en][5] / cos2
        vert = halfvres + halfvres * min(enemies[en][3], 2) / cos2
        hor = hres / 2 - hres * np.sin(enemies[en][2])
        spsurf = pg.transform.scale(sprites[types][cycle][dir2p], scale)
        surf.blit(spsurf, (hor, vert) - scale / 2)

    weapon = pistol[int(pistol_spr)]
    weapon_pos = WIDTH / 10, HEIGHT / 10

    surf.blit(weapon, weapon_pos)

    return surf, en - 1


if __name__ == '__main__':
    main()
    pg.quit()
