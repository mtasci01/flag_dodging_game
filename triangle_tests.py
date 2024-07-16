import math
import pygame
import numpy as np
pygame.init()

HEIGHT = 800
WIDTH = 600

window = pygame.display.set_mode((HEIGHT,WIDTH))
pygame.display.set_caption('TRIANGLE TESTS')
RED = (255,0,0)

NUM_TRIANGLES = 6
TRIANGLE_SIDE = 30
SPACING_TRIANGLES = 100
triangles = []

def heightFromSide(s):
    return (0.5)*math.sqrt(3)*s

for i in range(NUM_TRIANGLES):
    p1 = [(TRIANGLE_SIDE*i) + (SPACING_TRIANGLES*i),0]
    p2 = [p1[0] + TRIANGLE_SIDE,0]
    p3 = [(p1[0] + p2[0])/2, heightFromSide(TRIANGLE_SIDE)]
    triangles.append([p1,p2,p3])

running = True

triangles = np.array(triangles)

SPEED = 0.1

while running:
    window.fill([0,0,0])
    for triangle in triangles:
        for i in range(len(triangle)):
            triangle[i] = triangle[i] + np.array([0,SPEED])
            if triangle[i][1] > HEIGHT or triangle[i][1] < 0:
                SPEED = SPEED*-1
        pygame.draw.polygon(window, RED, triangle.tolist(),0)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()