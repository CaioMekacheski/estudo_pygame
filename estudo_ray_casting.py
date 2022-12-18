import pygame as pg
from numba import njit
from settings import *


def main():
    pg.init()
    screen = pg.display.set_mode(RESOLUTION)
    running = True
    clock = pg.time.Clock()

    hres = HOR_RES  # Resolução horizontal
    halfvres = HALF_VER_RES  # Resolução vertical / 2

    mod = MOD  # Fator de escala (60º fov)

    # Mapa
    size = SIZE
    posx, posy, rot, maph, mapc, exitx, exity = gen_map(size)

    frame = np.random.uniform(0, 1, (hres, halfvres * 2, 3))    # Frame

    # Carrega e armazena a imagem do céu em um array 3d
    image_width = 360
    sky = pg.surfarray.array3d(pg.transform.scale
                               (pg.image.load('skybox2.jpg'), (image_width, halfvres * 2)))/255

    # Carrega e armazena a imagem do chão em um array 3d
    floor = pg.surfarray.array3d(pg.image.load('floor04.png'))/255

    # Carrega e armazena a imagem da parede em um array 3d
    wall = pg.surfarray.array3d(pg.image.load('wall01.jpg'))/255

    while running:  # Enquanto running for true

        for event in pg.event.get():    # Checa eventos

            if event.type == pg.QUIT:   # Se o evento for QUIT
                running = False     # encerra o jogo

            if int(posx) == exitx and int(posy) == exity:   # Se o player encontrar a saída
                print("Você encontrou a saída! Parabéns!!") # encerras o jogo
                running = False


        # Cria o frame
        frame = new_frame(posx, posy, rot,
                          frame, sky, floor,
                          hres, halfvres, mod,
                          maph, mapc, size, wall,
                          exitx, exity)

        # Cria uma superfície para receber o frame e o adapta conforme a altura e largura da tela
        surf = pg.surfarray.make_surface(frame * 255)
        surf = pg.transform.scale(surf, RESOLUTION)

        # Imprime o fps e a posição x e y na borda superior da janela
        fps = int(clock.get_fps())
        pg.display.set_caption(" FPS: " + str(fps) +
                               " X: " + str(int(posx)) +
                               " Y: " + str(int(posy)) +
                               " Rotação: " + str(int(rot)))

        # Define as cordenadas x e y e a rotação do player
        posx, posy, rot = movement(posx, posy, rot, pg.key.get_pressed(), maph, clock.tick())
        screen.blit(surf, (0, 0))
        pg.display.update()
        #posx, posy, rot = movement(posx, posy, rot, pg.key.get_pressed(), maph, clock.tick())

# Movimento do player
def movement(posx, posy, rot, keys, maph, et):  # Movimentação do player

    x, y, diag = posx, posy, rot

    if keys[pg.K_LEFT] or keys[ord('a')]:  # Rotaciona a camera para a direita
        rot -= PLAYER_ROT_SPEED * et

    if keys[pg.K_RIGHT] or keys[ord('d')]:  # Rotaciona a camera para a esquerda
        rot += PLAYER_ROT_SPEED * et

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

        if testx > 0 and testx < size - 1 and testy > 0 and testy < size - 1:

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
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, maph, mapc, size, wall, exitx, exity):

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

        ash = 0

        if maph[int(x - 0.33) % (size - 1)][int(y - 0.33) % (size - 1)]:
            ash = 1


        if maph[int(x - 0.01) % (size - 1)][int(y - 0.01) % (size - 1)]:
            shade, ash = shade * 0.5, 0

        c = shade * mapc[int(x) % (size - 1)][int(y) % (size - 1)]

        for k in range(h * 2):

            if halfvres - h + k >= 0 and halfvres - h + k < 2 * halfvres:

                if ash and 1 - k / (2 * h) < 1 - xx / 225:
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

            elif maph[int(x - 0.33) % (size - 1)][int(y) % (size - 1)] \
                    or maph[int(x) % (size - 1)][int(y - 0.33) % (size - 1)]:

                shade = shade * 0.5


            frame[i][halfvres * 2 - j - 1] = \
                 shade * (floor[xx][yy] + frame[i][halfvres * 2 - j - 1]) / 2  # Preenche o frame considerando o sombreamento

            if int(x) == exitx and int(y) == exity and (x % 1 - 0.5) ** 2 + (y % 1 - 0.5) ** 2 < 0.2:
                ee = j / (10 * halfvres)
                frame[i][j:2 * halfvres - j] = (ee * np.ones(3) + frame[i][j:2 * halfvres - j]) / (1 + ee)

    return frame

if __name__ == '__main__':
    main()
    pg.quit()
