import csv
import math
import os
import pathlib
import random
import sys
import time
from pygame.locals import *
import pygame
import numpy as np
pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()


HEIGHT = 700
WIDTH = 600
MOVE_SPEED = 3

scoreObj = {"score":0}

#todo music

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('FLAGS CATCHER')

def loadExplosionanimation():
    explosionAnim = {}
    explosionAnim['lg'] = []
    explosionAnim['sm'] = []
    for i in range(9):
        filename = 'expl{}.png'.format(i)
        img = pygame.image.load("explosions/" +filename).convert()
        img.set_colorkey([0,0,0])
        lg = pygame.transform.scale(img, (80, 80))
        explosionAnim['lg'].append(lg)
        sm = pygame.transform.scale(img, (30, 30))
        explosionAnim['sm'].append(sm)
    return explosionAnim

explosionAnim = loadExplosionanimation()

def populateFlagsMap():
   
    flagsMap = {}

    with open('flags/all.csv', 'r',encoding='utf8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            alpha2 = row[1].upper()
            flagObj = {"name":row[0],"continent":row[5]}
            flagsMap[alpha2] = flagObj
    currPath = pathlib.Path().resolve()        
    imgspath = str(currPath) + "\\flags\\84x63"
    imgs = os.listdir(imgspath)
    for img in imgs:
        img_split = img.split(".")
        alpha2 = img_split[0].upper()
        imgObj = pygame.image.load(imgspath + "/" + img)
        imgObj = pygame.transform.scale(imgObj, [60,40])
        if alpha2 in flagsMap:
            flagObj = flagsMap[alpha2]
            flagObj["imgObj"] = imgObj
    return flagsMap    

flagsMap = populateFlagsMap() 

def sampleContinent(flagsMap):
    continentList = []
    for flagId in flagsMap:
        flagObj = flagsMap[flagId]
        if (flagObj['continent'] !=False):
            continentList.append(flagObj['continent'])
    return np.random.choice(continentList)  

CONTINENT_CHOSEN=sampleContinent(flagsMap)

flagsMapTaken = {}  

class Flag(pygame.sprite.Sprite):
      def __init__(self, flagsMap, minx, maxx, moveSpeed, flagId):
        super().__init__()
        self.moveSpeed = moveSpeed  
        self.flagsMap = flagsMap
        self.flagId = str(flagId)
        self.getFlag()
        self.rect = self.image.get_rect()

        self.minx = minx
        self.maxx = maxx
        self.rect.center = self.generateCenter()
        

      def update(self):
        self.rect.move_ip(0,self.moveSpeed)
        if (self.rect.bottom > HEIGHT):
            self.resetPosition()

      def resetPosition(self):
        self.rect.top = 0
        self.rect.center = self.generateCenter()
        self.moveSpeed += 0.1
        self.getFlag()          

      def generateCenter(self):
         c = (random.randint(self.minx, self.maxx), 0)
         return c
          
      def getFlag(self):
        maxAttempts = 10000
        k = None
        for i in range(maxAttempts): 
            k = np.random.choice(list(self.flagsMap))
            ftvs = set(flagsMapTaken.values())
            if not(k in ftvs):
                break
        flagObj = self.flagsMap[k] 
        flagsMapTaken[self.flagId] = k
        self.image = flagObj['imgObj']
        self.name = flagObj['name']
        self.continent = flagObj['continent']

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosionAnim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.lastUpdate = pygame.time.get_ticks()
        self.frameRate = FPS

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.lastUpdate > self.frameRate:
            self.lastUpdate = now
            self.frame += 1
            if self.frame == len(explosionAnim[self.size]):
                self.kill()
            else:
                self.image = explosionAnim[self.size][self.frame]      

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__() 
        self.originImage = self.loadImage()
        self.rect = self.originImage.get_rect()
        self.rect.center = (160, HEIGHT - 60)

    def loadImage(self):
        image = pygame.image.load("Player-removebg-preview.png")
        image = pygame.transform.scale(image, [60,60])
        return image
    
    def update(self):
        pressed_keys = pygame.key.get_pressed()
        self.image = pygame.transform.rotate(self.originImage, 0)
        if self.rect.left > 0:
              if pressed_keys[K_LEFT]:
                  self.rect.move_ip(-5, 0)
                  self.image = pygame.transform.rotate(self.originImage, 90)
                  if pressed_keys[K_SPACE]:
                    self.rect.move_ip(-10, 0)
        if self.rect.right < WIDTH:        
              if pressed_keys[K_RIGHT]:
                  self.image = pygame.transform.rotate(self.originImage, -90)
                  self.rect.move_ip(5, 0)
                  if pressed_keys[K_SPACE]:
                    self.rect.move_ip(10, 0)         
                               


running = True
SCROLL = 0
SCROLL_SPEED = 3
bg = pygame.image.load("I5ram_small.png").convert()
tiles = math.ceil(HEIGHT/bg.get_height()) + 1   


def initFlagList(numfOfFlags):
    flags = pygame.sprite.Group()
    gridunit = WIDTH/numfOfFlags
    minx = 40
    maxx = minx + gridunit - 50
    for i in range(numfOfFlags):
        if i == (numfOfFlags - 1):
            maxx = maxx - 40  
        f1 = Flag(flagsMap,minx,maxx, MOVE_SPEED,i)
        flags.add(f1)
        minx = minx + gridunit
        maxx = maxx + gridunit
    return flags    

flags = initFlagList(3)
allEntities = pygame.sprite.Group()
for f in flags:
    allEntities.add(f)
player = Player()
allEntities.add(player)

def drawAllEntities():
    for entity in allEntities:
        entity.update()
        window.blit(entity.image, entity.rect)
        if hasattr(entity, 'flagId'):

            newRect = entity.rect.copy() 
            newRect.move_ip(15, -50)
            newImage = entity.image.copy()
            newImage = pygame.transform.scale(newImage, [30,20])
            window.blit(newImage, newRect)

            newRect = entity.rect.copy() 
            newRect.move_ip(20, -100)
            newImage = entity.image.copy()
            newImage = pygame.transform.scale(newImage, [20,10])
            window.blit(newImage, newRect)

window.fill([30,255,40])
font = pygame.font.SysFont("Verdana", 20)
fontcolor =  [0,0,10]
window.blit(font.render("Catch the flags of " + CONTINENT_CHOSEN +  "!", True,fontcolor), (20,250))
pygame.display.update()
time.sleep(3)
            

while running:
        
    i=0
    while(i<tiles): #one image right after the other
        bgx = 0
        bgy = -1*(bg.get_height()*i - SCROLL)
        window.blit(bg, (bgx,bgy))
        i+=1
    SCROLL += SCROLL_SPEED
    if abs(SCROLL) > bg.get_height():
        SCROLL = 0
    
    drawAllEntities()

    collisions = pygame.sprite.spritecollideany(player, flags)
    if collisions:
        
        
        if collisions.continent != CONTINENT_CHOSEN:
            expl = Explosion(player.rect.center, 'lg')
            allEntities.add(expl)
            pygame.mixer.Sound('hit.mp3').play()
            drawAllEntities()
            pygame.display.update()
            time.sleep(1)
                    
            window.fill([255,10,40])
            font = pygame.font.SysFont("Verdana", 20)
            fontcolor =  [0,0,10]
            window.blit(font.render("Game Over!  You hit " + collisions.name + " in " + collisions.continent + "!", True,fontcolor), (20,250))
            window.blit(font.render("SCORE:" + str(scoreObj['score']), True, fontcolor), (20,280))
            pygame.display.update()
            for entity in allEntities:
                entity.kill() 
            time.sleep(4)
            pygame.quit()
            sys.exit()
        else:
            expl = Explosion(collisions.rect.center, 'sm')
            allEntities.add(expl)
            pygame.mixer.Sound('Good_hit.mp3').play()
            scoreObj['score'] = scoreObj['score'] + 1
            for f in flags:
                f.resetPosition()
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()
    FramePerSec.tick(FPS)