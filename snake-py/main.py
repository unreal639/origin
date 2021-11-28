import pygame
import sys
import time
from pygame.locals import *
from enum import Enum
from collections import deque
import random
import time

class Direct(Enum):
	LEFT = 0
	UP = 1
	DOWN = 2
	RIGHT = 3

	def opposite(self):
		return Direct(3-self.value)

SNAKE_SQUARE_SIZE = 12
FOOD_SIZE = 12

GREEN = (0, 255, 0)
RED = (255, 0 ,0)
BLACK = (0, 0, 0)

BLANK_COLOR = BLACK
FOOD_COLOR = RED

GAME_HEIGHT = 600
GAME_WIDTH = 1000

BOARD_LINE_WIDTH = 3

INNER_HEIGHT = GAME_HEIGHT - BOARD_LINE_WIDTH
INNER_WIDTH = GAME_WIDTH - BOARD_LINE_WIDTH

def draw_background(screen):
	draw_board(screen, 0, GAME_WIDTH)
	draw_board(screen, GAME_HEIGHT-BOARD_LINE_WIDTH, GAME_WIDTH)

	draw_board(screen, 0, GAME_HEIGHT, False)
	draw_board(screen, GAME_WIDTH-BOARD_LINE_WIDTH, GAME_HEIGHT, False)


def draw_board(screen, pos, length, direction=True, line_with=BOARD_LINE_WIDTH):
	interval = 12
	start = 0
	while start <= length:
		if direction:
			pygame.draw.rect(screen, GREEN, (start, pos, interval, line_with))
		else:
			pygame.draw.rect(screen, GREEN, (pos, start, line_with, interval))

		start += (interval*2)

class Square:
	def __init__(self, screen, pos):
		
		self.size = SNAKE_SQUARE_SIZE
		self.screen = screen
		self.color = GREEN
		self.x,self.y = pos


	def draw(self):
		pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

	def remove(self):
		pygame.draw.rect(screen, BLANK_COLOR, (self.x, self.y, self.size, self.size))

	def boarder(self, direct:Direct):
		if direct == Direct.LEFT:
			return self.x
		elif direct == Direct.UP:
			return self.y
		elif direct == Direct.RIGHT:
			return self.x + self.size
		elif direct == Direct.DOWN:
			return self.y + self.size
	

def around(sq:Square, direct:Direct):
	interval = 3
	if direct == Direct.LEFT:
		new_s = Square(sq.screen, (sq.x-SNAKE_SQUARE_SIZE-interval, sq.y))
	elif direct == Direct.RIGHT:
		new_s = Square(sq.screen, (sq.x+SNAKE_SQUARE_SIZE+interval, sq.y))
	elif direct == Direct.UP:
		new_s = Square(sq.screen, (sq.x, sq.y-SNAKE_SQUARE_SIZE-interval))
	elif direct == Direct.DOWN:
		new_s = Square(sq.screen, (sq.x, sq.y+SNAKE_SQUARE_SIZE+interval))
	return new_s

def collide(s1:Square, s2:Square):
	s1_left_s2 = s1.boarder(Direct.RIGHT) < s2.boarder(Direct.LEFT)
	s1_right_s2 = s1.boarder(Direct.LEFT) > s2.boarder(Direct.RIGHT)
	s1_up_s2 = s1.boarder(Direct.DOWN) < s2.boarder(Direct.UP)
	s1_down_s2 = s1.boarder(Direct.UP) > s2.boarder(Direct.DOWN)
	return not (s1_left_s2 or s1_right_s2 or s1_up_s2 or s1_down_s2)
	
def check(s:Square, height=INNER_HEIGHT, width=INNER_WIDTH):
	return s.x > 0 and s.y > 0 and s.boarder(Direct.RIGHT) < width and s.boarder(Direct.DOWN) < height

def is_direct_key(key_type):
	return key_type in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]

def get_direct(key_type):
	mapper = {
		pygame.K_LEFT:  Direct.LEFT,
		pygame.K_RIGHT: Direct.RIGHT,
		pygame.K_UP:    Direct.UP,
		pygame.K_DOWN:  Direct.DOWN
	}
	return mapper[key_type]

def game_over(screen):
	font = pygame.font.SysFont('arial', 60)
	text = font.render('GAME OVER', True, GREEN)
	rect = text.get_rect()
	rect.center = (GAME_WIDTH/2, GAME_HEIGHT/2)
	screen.blit(text, rect)

class Snake:
	def __init__(self, screen):
		self.direct = Direct.RIGHT
		self.body = deque()


	def draw(self, body_list):
		self.body.extend(body_list)
		for s in self.body:
			s.draw()

	def update(self, direct:Direct = None):
		direct = self.direct if direct is None else direct
		
		new_head = around(self.head, direct)
		new_head.draw()
		self.body.appendleft(new_head)

		tail = self.body.pop()
		tail.remove()

	def after_eat(self):
		new_head = around(self.head, self.direct)
		new_head.draw()
		self.body.appendleft(new_head)

	def bite(self):
		for idx,s in enumerate(self.body):
			if idx == 0:
				continue
			if collide(self.head, s):
				return True
		return False

	@property
	def head(self):
		if len(self.body) != 0:
			return self.body[0]
		return None
	

class Food(Square):
	def __init__(self, screen):
		self.screen = screen
		self.size = FOOD_SIZE
		self.color = FOOD_COLOR
		self.x, self.y = random.randint(FOOD_SIZE, INNER_WIDTH-FOOD_SIZE), random.randint(FOOD_SIZE, INNER_HEIGHT-FOOD_SIZE)


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((GAME_WIDTH,GAME_HEIGHT))
pygame.display.set_caption('snake game')

draw_background(screen)
snake = Snake(screen)

s1 = Square(screen, (60,90))
left = around(s1, Direct.LEFT)
l2 = around(left, Direct.LEFT)
snake.draw([s1,left,l2])

food = Food(screen)
food.draw()

while True:
	clock.tick(15)

	if not check(snake.head) or snake.bite():
		game_over(screen)
		pygame.display.update()
		break

	if collide(snake.head, food):
		food.remove()
		snake.after_eat()
		food = Food(screen)
		food.draw()

	for ev in pygame.event.get():
		if ev.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if ev.type == pygame.KEYDOWN:
			if is_direct_key(ev.key):
				direct = get_direct(ev.key)
				snake.update(direct)
				snake.direct = direct
				continue
	
	snake.update()
	pygame.display.flip()

time.sleep(3)