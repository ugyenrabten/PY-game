"""Flappy Bird, implemented using Pygame."""

import math
import os
from random import randint
from collections import deque

import pygame
from pygame.locals import *


FPS = 60
ANIMATION_SPEED = 0.18  # pixels per millisecond
WIN_WIDTH = 284 * 2     
WIN_HEIGHT = 512


class Bird(pygame.sprite.Sprite):

    WIDTH = HEIGHT = 32
    SINK_SPEED = 0.15
    CLIMB_SPEED = 0.3
    CLIMB_DURATION = 333.3

    def __init__(self, x, y, msec_to_climb, images):
        
        super(Bird, self).__init__()
        self.x, self.y = x, y
        self.msec_to_climb = msec_to_climb
        self._img_wingup, self._img_wingdown = images
        self._mask_wingup = pygame.mask.from_surface(self._img_wingup)
        self._mask_wingdown = pygame.mask.from_surface(self._img_wingdown)

    def update(self, delta_frames=1):

        if self.msec_to_climb > 0:
            frac_climb_done = 1 - self.msec_to_climb/Bird.CLIMB_DURATION
            self.y -= (Bird.CLIMB_SPEED * frames_to_msec(delta_frames) *
                       (1 - math.cos(frac_climb_done * math.pi)))
            self.msec_to_climb -= frames_to_msec(delta_frames)
        else:
            self.y += Bird.SINK_SPEED * frames_to_msec(delta_frames)

    @property
    def image(self):

        if pygame.time.get_ticks() % 500 >= 250:
            return self._img_wingup
        else:
            return self._img_wingdown

    @property
    def mask(self):

        if pygame.time.get_ticks() % 500 >= 250:
            return self._mask_wingup
        else:
            return self._mask_wingdown

    @property
    def rect(self):
        return Rect(self.x, self.y, Bird.WIDTH, Bird.HEIGHT)


class PipePair(pygame.sprite.Sprite):

    WIDTH = 80
    PIECE_HEIGHT = 32
    ADD_INTERVAL = 3000

    def __init__(self, pipe_end_img, pipe_body_img):

        self.x = float(WIN_WIDTH - 1)
        self.score_counted = False

        self.image = pygame.Surface((PipePair.WIDTH, WIN_HEIGHT), SRCALPHA)
        self.image.convert()   
        self.image.fill((0, 0, 0, 0))
        total_pipe_body_pieces = int(
            (WIN_HEIGHT -                  
             3 * Bird.HEIGHT -             
             3 * PipePair.PIECE_HEIGHT) /  
            PipePair.PIECE_HEIGHT          
        )
        self.bottom_pieces = randint(1, total_pipe_body_pieces)
        self.top_pieces = total_pipe_body_pieces - self.bottom_pieces

        # bottom pipe
        for i in range(1, self.bottom_pieces + 1):
            piece_pos = (0, WIN_HEIGHT - i*PipePair.PIECE_HEIGHT)
            self.image.blit(pipe_body_img, piece_pos)
        bottom_pipe_end_y = WIN_HEIGHT - self.bottom_height_px
        bottom_end_piece_pos = (0, bottom_pipe_end_y - PipePair.PIECE_HEIGHT)
        self.image.blit(pipe_end_img, bottom_end_piece_pos)

        # top pipe
        for i in range(self.top_pieces):
            self.image.blit(pipe_body_img, (0, i * PipePair.PIECE_HEIGHT))
        top_pipe_end_y = self.top_height_px
        self.image.blit(pipe_end_img, (0, top_pipe_end_y))

        # compensate for added end pieces
        self.top_pieces += 1
        self.bottom_pieces += 1

        # for collision detection
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def top_height_px(self):

        return self.top_pieces * PipePair.PIECE_HEIGHT

    @property
    def bottom_height_px(self):

        return self.bottom_pieces * PipePair.PIECE_HEIGHT

    @property
    def visible(self):

        return -PipePair.WIDTH < self.x < WIN_WIDTH

    @property
    def rect(self):

        return Rect(self.x, 0, PipePair.WIDTH, PipePair.PIECE_HEIGHT)

    def update(self, delta_frames=1):
        self.x -= ANIMATION_SPEED * frames_to_msec(delta_frames)

    def collides_with(self, bird):
        return pygame.sprite.collide_mask(self, bird)


def load_images():

    def load_image(img_file_name):
        file_name = os.path.join(os.path.dirname(__file__),
                                 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert()
        return img

    return {'background': load_image('background.png'),
            'pipe-end': load_image('pipe_end.png'),
            'pipe-body': load_image('pipe_body.png'),
            'bird-wingup': load_image('bird_wing_down.png'),
            'bird-wingdown': load_image('bird_wing_down.png')}


def frames_to_msec(frames, fps=FPS):
    return 1000.0 * frames / fps


def msec_to_frames(milliseconds, fps=FPS):
    return fps * milliseconds / 1000.0

def home_screen(display_surface):

    title_font = pygame.font.SysFont(None, 48, bold=True)
    option_font = pygame.font.SysFont(None, 32, bold=True)

    title_text = title_font.render("Flappy Bird", True, (255, 255, 255))
    start_text = option_font.render("Start", True, (255, 255, 255))
    quit_text = option_font.render("Quit", True, (255, 255, 255))

    title_x = WIN_WIDTH / 2 - title_text.get_width() / 2
    start_x = WIN_WIDTH / 2 - start_text.get_width() / 2
    quit_x = WIN_WIDTH / 2 - quit_text.get_width() / 2

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_s:
                    return  # Start the game
                if event.key == K_q:
                    pygame.quit()
                    sys.exit()

        display_surface.fill((0, 0, 0))
        display_surface.blit(title_text, (title_x, WIN_HEIGHT / 2 - 50))
        display_surface.blit(start_text, (start_x, WIN_HEIGHT / 2))
        display_surface.blit(quit_text, (quit_x, WIN_HEIGHT / 2 + 50))

        pygame.display.flip()

def main():

    pygame.init()

    display_surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('Pygame Flappy Bird')

    clock = pygame.time.Clock()
    score_font = pygame.font.SysFont(None, 32, bold=True)  # default font
    images = load_images()
    home_screen(display_surface)
    bird = Bird(50, int(WIN_HEIGHT / 2 - Bird.HEIGHT / 2), 2,
                (images['bird-wingup'], images['bird-wingdown']))
    # the bird stays in the same x position, so bird.x is a constant
    # center bird on screen
    bird = Bird(50, int(WIN_HEIGHT/2 - Bird.HEIGHT/2), 2,
                (images['bird-wingup'], images['bird-wingdown']))

    pipes = deque()

    frame_clock = 0  
    score = 0
    done = paused = False
    while not done:
        clock.tick(FPS)

        if not (paused or frame_clock % msec_to_frames(PipePair.ADD_INTERVAL)):
            pp = PipePair(images['pipe-end'], images['pipe-body'])
            pipes.append(pp)

        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                break
            elif e.type == KEYUP and e.key in (K_PAUSE, K_p):
                paused = not paused
            elif e.type == MOUSEBUTTONUP or (e.type == KEYUP and
                    e.key in (K_UP, K_RETURN, K_SPACE)):
                bird.msec_to_climb = Bird.CLIMB_DURATION

        if paused:
            continue  

        pipe_collision = any(p.collides_with(bird) for p in pipes)
        if pipe_collision or 0 >= bird.y or bird.y >= WIN_HEIGHT - Bird.HEIGHT:
            done = True

        for x in (0, WIN_WIDTH / 2):
            display_surface.blit(images['background'], (x, 0))

        while pipes and not pipes[0].visible:
            pipes.popleft()

        for p in pipes:
            p.update()
            display_surface.blit(p.image, p.rect)

        bird.update()
        display_surface.blit(bird.image, bird.rect)

        # update and display score
        for p in pipes:
            if p.x + PipePair.WIDTH < bird.x and not p.score_counted:
                score += 1
                p.score_counted = True

        score_surface = score_font.render(str(score), True, (255, 255, 255))
        score_x = WIN_WIDTH/2 - score_surface.get_width()/2
        display_surface.blit(score_surface, (score_x, PipePair.PIECE_HEIGHT))

        pygame.display.flip()
        frame_clock += 1

        display_surface.fill((0, 0, 0))  # Clear the screen
    game_over_font = pygame.font.SysFont(None, 48, bold=True)
    game_over_text = game_over_font.render("Game Over", True, (255, 255, 255))
    score_text = score_font.render(f'Your Score: {score}', True, (255, 255, 255))
    restart_text = score_font.render("Press 'R' to Restart", True, (255, 255, 255))
    quit_text = score_font.render("Press 'Q' to Quit", True, (255, 255, 255))
    game_over_x = WIN_WIDTH / 2 - game_over_text.get_width() / 2
    score_x = WIN_WIDTH / 2 - score_text.get_width() / 2
    restart_x = WIN_WIDTH / 2 - restart_text.get_width() / 2
    quit_x = WIN_WIDTH / 2 - quit_text.get_width() / 2
    display_surface.blit(game_over_text, (game_over_x, WIN_HEIGHT / 2 - 50))
    display_surface.blit(score_text, (score_x, WIN_HEIGHT / 2))
    display_surface.blit(restart_text, (restart_x, WIN_HEIGHT / 2 + 50))
    display_surface.blit(quit_text, (quit_x, WIN_HEIGHT / 2 + 100))
    pygame.display.flip()

    # Game-over loop
    game_over = True
    while game_over:
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if e.type == KEYUP:
                if e.key == K_r:
                    game_over = False  # Restart the game
                if e.key == K_q:
                    pygame.quit()
                    sys.exit()
    print('Game over! Score: %i' % score)
    pygame.quit()


if __name__ == '__main__':
    # If this module had been imported, __name__ would be 'flappybird'.
    # It was executed (e.g. by double-clicking the file), so call main.
    main()
