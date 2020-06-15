import pygame
import neat
import time
import os
import random

#UPPERCASE = 절대 바꾸지 않기
WIN_WIDTH = 600
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png")))], [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png")))], [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))]
BASE_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))]
BG_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))]
