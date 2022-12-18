# Atualizado em 17/12/2022

import math
import numpy as np

RES = WIDTH, HEIGHT = 800, 600
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
HOR_RES = 160
HALF_VER_RES = 120
MOD = HOR_RES / 60

PLAYER_POSX = 1.5
PLAYER_POSY = np.random.randint(1, SIZE - 1)
PLAYER_ANGLE = np.pi / 4
PLAYER_SPEED = 0.002
PLAYER_ROT_SPEED = 0.001
