from turtle import position
from pip import main
import pygame, sys, random
from pygame.math import Vector2

class SNAKE:
    def __init__(self):
        self.body = [Vector2(5,10), Vector2(4,10), Vector2(3,10)]
        self.direction = Vector2(0,0)
        self.new_block = False

        self.head_up = pygame.image.load('graphics/fire_face_u.png').convert_alpha()
        self.head_up = pygame.transform.scale(self.head_up, (40,40))

        self.head_down = pygame.image.load('graphics/fire_face_d.png').convert_alpha()
        self.head_down = pygame.transform.scale(self.head_down, (40,40))

        self.head_right = pygame.image.load('graphics/fire_face_r.png').convert_alpha()
        self.head_right = pygame.transform.scale(self.head_right, (40,40))

        self.head_left = pygame.image.load('graphics/fire_face_l.png').convert_alpha()
        self.head_left = pygame.transform.scale(self.head_left, (40,40))

        self.tail = pygame.image.load('graphics/fire_tail.png').convert_alpha()
        self.tail = pygame.transform.scale(self.tail, (40,40))

        self.body_im = pygame.image.load('graphics/fire.png').convert_alpha()
        self.body_im = pygame.transform.scale(self.body_im, (40,40))

        # add sound
        self.score_sound = pygame.mixer.Sound('sounds\mixkit-retro-game-notification-212.wav')
        self.lose_sound = pygame.mixer.Sound('sounds\mixkit-arcade-retro-game-over-213.wav')

    def draw_snake(self):
        # for block in self.body:
        #     x_pos = int(block.x * cell_size)
        #     y_pos = int(block.y * cell_size)
        #     block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)
        #     #draw snake rectangles
        #     pygame.draw.rect(screen, (30,50,200), block_rect)

        self.update_head_graphics()

        for index, block in enumerate(self.body):
            # we need a rect for posistioning
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)
            
            # what direction is the face
            if index == 0:
                screen.blit(self.head, block_rect)
            elif index == len(self.body) - 1:
                screen.blit(self.tail, block_rect)
            else:
                screen.blit(self.body_im, block_rect)
        
    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1,0): self.head = self.head_left
        elif head_relation == Vector2(-1,0): self.head = self.head_right
        elif head_relation == Vector2(0,1): self.head = self.head_up
        elif head_relation == Vector2(0,-1): self.head = self.head_down



    def move_snake(self):
        if self.new_block == True:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self):
        self.new_block = True
    
    def play_score_sound(self):
        self.score_sound.play()

    def play_game_over(self):
        self.lose_sound.play()

    def reset(self):
        # self.play_game_over()
        self.body = [Vector2(5,10), Vector2(4,10), Vector2(3,10)]
        self.direction = Vector2(0,0)

class FRUIT:
    def __init__(self):
        self.randomize()
        
    def draw_fruit(self):
        # draw a square
        fruit_rect = pygame.Rect(int(self.pos.x * cell_size), int(self.pos.y * cell_size), cell_size, cell_size)
        screen.blit(apple, fruit_rect)
        #pygame.draw.rect(screen,(200,20,20),fruit_rect)

    def randomize(self):
                # Create a random x and y position
        self.x = random.randint(0,(cell_number -1))
        self.y = random.randint(0,(cell_number -1))
        self.pos = Vector2(self.x,self.y)

class MAIN:
    def __init__(self):
        self.snake = SNAKE()
        self.fruit = FRUIT()

    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()
    
    def draw_elements(self):
        self.draw_grass()
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            # reposition fruit
            self.fruit.randomize()
            # grow snake body
            self.snake.add_block()

            # play sound
            self.snake.play_score_sound()
        
        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()

    def check_fail(self):
        #check snake hits border
        if not 0 <= self.snake.body[0].x < cell_number:
            self.game_over()
        elif not 0 <= self.snake.body[0].y < cell_number:
            self.game_over()
        #check if snake hits body
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()
    
    def game_over(self):
        self.snake.reset()
    
    def draw_grass(self):
        grass_color = (255,212,128)
        for row in range(cell_number):
            if row % 2 == 0:
                for column in range(cell_number):
                    if column % 2 == 0:
                        grass_rect = pygame.Rect((column*cell_size), (row * cell_size), cell_size, cell_size)
                        pygame.draw.rect(screen,grass_color, grass_rect)
            else:
                for column in range(cell_number):
                    if column % 2 != 0:
                        grass_rect = pygame.Rect((column*cell_size), (row * cell_size), cell_size, cell_size)
                        pygame.draw.rect(screen,grass_color, grass_rect)

    def draw_score(self):
        score_text = str(len(self.snake.body) - 3)
        score_surface = game_font.render(score_text, True,(10,20,30))
        score_x = int((cell_size * cell_number) - 60)
        score_y = int((cell_size * cell_number) - 40)
        score_rect = score_surface.get_rect(center = (score_x, score_y))
        
        # draw small wood next to score
        apple_rect = apple.get_rect(midright = (score_rect.left, score_rect.centery))

        # draw small rectangle around score
        bg_rect = pygame.Rect(apple_rect.left, apple_rect.top, (apple_rect.width + score_rect.width + 5), (apple_rect.height + 2))

        pygame.draw.rect(screen,(255,150,100),bg_rect)
        pygame.draw.rect(screen,(10,20,30),bg_rect,2)
        screen.blit(score_surface, score_rect)
        screen.blit(apple, apple_rect)

pygame.init()
cell_size = 40
cell_number = 20
screen = pygame.display.set_mode((cell_size*cell_number,cell_size*cell_number))
clock = pygame.time.Clock()

# import image of wood
apple = pygame.image.load('graphics\wood.png').convert_alpha()
apple = pygame.transform.scale(apple, (40,40))

# font for score
game_font = pygame.font.Font('font/1up.ttf', 25)

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 150) #every 150ms

main_game = MAIN()

while True:
    # Here we draw every element
    for event in pygame.event.get():
        #exit when clicking cross
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SCREEN_UPDATE:
            main_game.update()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if main_game.snake.direction.y != 1:
                    main_game.snake.direction = Vector2(0,-1)
            if event.key == pygame.K_DOWN:
                if main_game.snake.direction.y != -1:
                    main_game.snake.direction = Vector2(0,1)
            if event.key == pygame.K_LEFT:
                if main_game.snake.direction.x != 1:
                    main_game.snake.direction = Vector2(-1,0)
            if event.key == pygame.K_RIGHT:
                if main_game.snake.direction.x != -1:
                    main_game.snake.direction = Vector2(1,0)

    # background color
    screen.fill((255,195,77))
    main_game.draw_elements()
    pygame.display.update()
    #frames per second
    clock.tick(60)