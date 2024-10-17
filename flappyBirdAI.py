import pygame
import neat # neuro evolution augmented topology
import time
import os
import random

pygame.font.init()
#UPPERCASE = 절대 바꾸지 않기
WIN_WIDTH = 570
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png")))], [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png")))], [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

############################# Game Classes #############################

class Bird:
    """
    Bird Class
    Class for the Bird object (AKA player)
    """
    # Constants
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5
    
    def __init__(self, x, y):
        """
        Bird Class Initializer
        x: x coordinate of the Bird
        y: y coordinate of the Bird
        The initializer initializes the variables for calculation and the bird image.
        """
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0][0]
        
    def jump(self):
        """
        jump function
        The equivalent of "space bar" move of the game
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        move function
        When the bird moves (both x and y direction), this function calculates the change in velocity.
        """
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        if d >= 16:
            d = 16
        if d < 0:
            d -= 2
        
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, win):
        """
        draw function
        win: the background window
        This function draws the bird and changes the picture according to the tick count.
        """
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0][0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1][0]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2][0]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1][0]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0][0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1][0]
            self.img_count = self.ANIMATION_TIME * 2
        
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        """
        get_mask function
        gets the mask from the provided image after several calculation.
        """
        return pygame.mask.from_surface(self.img)
    
class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100
        self.top = 0 #where are the top and bottom of pipe img?
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #flip the pipe (위에 있는거)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False #is bird passed from pipe?
        self.set_height() #define where top and bottom and how tall the pipe is

    def set_height(self):
        #give random number to the pipe height
        self.height = random.randrange(40,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -= self.VEL 
    
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        else:
            return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)

    score_label = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

def main(genomes, config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    score = 0
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind += 1
        else:
            run = False
            break
        
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(700))
        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() > 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        # bird.move()
        base.move()

        draw_window(win, birds, pipes, base, score)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)
    #stat info
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_feedforward.txt")
    run(config_path)
