import sys
import socket
import threading
from queue import Queue

if (len(sys.argv)) == 1:
  HOST = "localhost"
else:
  HOST = str(sys.argv[1])

HOST = "localhost"
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST,PORT))
print("connected to server")

def handleServerMsg(server, serverMsg):
  server.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += server.recv(10).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)
      command = msg.split("\n")

import pygame
from Cards import *
import random
import string
import sys
import json
pygame.font.init()

########### 글로벌 변수 #########################################################

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
playerSize = (70, 70)
filename = "other/saves.json"
pygame.mixer.init()
clickFX = pygame.mixer.Sound("sounds/click.wav")
diceFX = pygame.mixer.Sound("sounds/dice.wav")
moneyFX = pygame.mixer.Sound("sounds/money.wav")
whistleFX = pygame.mixer.Sound("sounds/whistle.wav")
themeFX = pygame.mixer.music.load("sounds/theme.mp3")
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.2)


######## 클래스 ################################################################

class Player(object):

    allPlayers = []

    def __init__(self, name):
        Player.allPlayers.append(self)
        self.name = name
        self.priority = len(Player.allPlayers)
        self.position = 0
        self.coords = [720, 720] # GO 포지션
        piece = pygame.image.load("images/player_%s.png" %self.name)
        scaledPiece = pygame.transform.scale(piece, playerSize)
        self.piece = scaledPiece
        self.ready = False
        self.cash = 1500
        self.properties = []

    def __repr__(self):
        return self.name + str(self.priority)

    # 1바퀴 돌았을 때
    def getCoords(self):
        if self.position >= len(gameBoard):
            self.position = self.position - len(gameBoard)
            self.cash += 200
            moneyFX.play()
        spot = gameBoard[self.position]
        self.coords[0] = spot[0][0]
        self.coords[1] = spot[0][1]

class Monopoly(object):

    def init(self):
        self.server = server
        self.PID = None
        self.startScreen = True
        self.helpScreen = False
        self.lobbyScreen = False
        self.gameScreen = False
        self.gameOver = False
        self.loser = None


        self.mouseOnRoll = False
        self.rollButton = (305, 505, 210, 290)
        self.mouseOnReady = False
        self.readyButton = (1050, 1290, 430, 650)


        self.dice_1 = 1
        self.dice_2 = 1
        self.currNum = 1
        self.currPlayer = None
        self.players = {}
        self.roundEvents = []
        self.roundEvents2 = []
        self.counter = 0


        self.options = False
        self.playerStats = False
        self.mortgaging = False
        self.building = False
        self.propertyStats = False


############ 그리기 ############################################################

    def drawText(self, screen, size, text, color, x, y):
        font = pygame.font.SysFont("malgungothic", size)
        textSurface = font.render(text, False, color)
        screen.blit(textSurface,(x,y))

    def drawStartScreen(self, screen):
        image = pygame.image.load("images/Map3.png")
        scaledBoard = pygame.transform.scale(image, (1000, 250))
        screen.blit(scaledBoard, (400,200))
        self.drawText(screen, 100, "S를 눌러 시작합시다!", BLACK, 400, 600)

    def drawLobbyScreen(self, screen):
        image = pygame.image.load("images/logo.png")
        screen.blit(image, (600,100))
        pygame.draw.rect(screen, RED, (1050, 430, 240, 220))
        pygame.draw.rect(screen, WHITE, (1060, 440, 220, 200))
        self.drawText(screen, 50, "READY", BLACK, 1085, 510)
        counter = 0
        for i in self.players:
            scaledPiece = pygame.transform.scale(self.players[i].piece, (220,220))
            screen.blit(scaledPiece, (350+(350*counter), 450))
            if i == self.PID:
                self.drawText(screen, 30, "You", BLACK, 420+(350*counter), 400)
            else:
                self.drawText(screen, 30, "%s" %self.players[i].name, BLACK, 420+(350*counter), 400)
            if self.players[i].ready == False:
                self.drawText(screen, 20, "Not ready", BLACK,\
                400+(350*counter), 700)
            else: self.drawText(screen, 20, "Ready", BLACK,\
            400+(350*counter), 700)
            counter += 1

###### 게임 화면 그리기##########################################################

    def drawGameScreen(self, screen):
        self.drawBoard(screen)
        self.drawPlayers(screen)
        self.drawRoll(screen)
        self.drawDie(screen)
        self.drawPortraits(screen)
        self.drawActivityLog(screen)
        self.drawInstructions(screen)
        self.drawBuildings(screen)
        self.drawProperty(screen)
        self.drawOwnerProperty(screen)

    def drawBoard(self, screen):
        board = pygame.image.load("images/monopolyR.png")
        scaledBoard = pygame.transform.scale(board, (800, 800))
        screen.blit(scaledBoard, (0,0))

    def drawPlayers(self, screen):
        for player in Player.allPlayers:
            screen.blit(player.piece, player.coords)

    def drawRoll(self, screen):
        pygame.draw.rect(screen, RED, (305, 210, 200, 80))
        pygame.draw.rect(screen, WHITE, (315, 220, 180, 60))
        self.drawText(screen, 40, "ROLL!", BLACK, 350, 220)

    def drawDie(self, screen):
        dice1 = pygame.image.load("images/dice_%s.png" %self.dice_1)
        dice2 = pygame.image.load("images/dice_%s.png" %self.dice_2)
        screen.blit(dice1, (275, 350))
        screen.blit(dice2, (425, 350))

    def drawPortraits(self, screen):
        cnt = 0
        for i in self.players:
            scaledPiece = pygame.transform.scale\
            (self.players[i].piece, (50,50))
            if cnt == 0:
                screen.blit(scaledPiece, (820,30))
                if i == self.PID:
                    self.drawText(screen, 20, "You", BLACK, 830,0)
                    self.drawText(screen, 20, "재산 : $%d"%self.players[i].cash, BLACK, 830,90)
                else:
                    self.drawText(screen, 20, "%s"%self.players[i].name, BLACK, 830,0)
                    self.drawText(screen, 20, "재산 : $%d"%self.players[i].cash, BLACK, 830,90)

            if cnt == 1:
                screen.blit(scaledPiece, (820,555))
                if i == self.PID:
                    self.drawText(screen, 20, "You", BLACK, 830,525)
                    self.drawText(screen, 20, "재산 : $%d"%self.players[i].cash, BLACK, 830,615)
                else:
                    self.drawText(screen, 20, "%s"%self.players[i].name, BLACK, 830,525)
                    self.drawText(screen, 20, "재산 : $%d"%self.players[i].cash, BLACK, 830,615)
            cnt += 1

    def drawInstructions(self, screen):
            pygame.draw.line(screen, BLACK, [802, 0], [1182, 0], 3)
            pygame.draw.line(screen, BLACK, [802, 0], [802, 275], 3)
            pygame.draw.line(screen, BLACK, [1182, 0], [1182, 275], 3)
            pygame.draw.line(screen, BLACK, [802, 275], [1182, 275], 3)

            pygame.draw.line(screen, BLACK, [802, 523], [1182, 523], 3)
            pygame.draw.line(screen, BLACK, [802, 523], [802, 798], 3)
            pygame.draw.line(screen, BLACK, [1182, 523], [1182, 798], 3)
            pygame.draw.line(screen, BLACK, [802, 798], [1182, 798], 3)

    def drawActivityLog(self, screen):
        pygame.draw.rect(screen, BLACK, (802, 275, 390, 250))
        pygame.draw.rect(screen, WHITE, (807, 280, 380, 240))
        if len(self.roundEvents) > 9:
            self.roundEvents.pop(0)
        counter = 0
        for event in self.roundEvents:
            self.drawText(screen, 15, event, BLACK, 805, 288+(counter*25))
            counter += 1

    def drawProperty(self, screen):
        if len(self.roundEvents2) > 1:
            self.roundEvents2.pop(0)
        for event in self.roundEvents2:
            self.drawText(screen, 20, event, BLACK, 900, 90)

    def drawOwnerProperty(self, screen):
        for player in self.players:
            for card in self.players[player].properties:
                if card[1] == "Taiwan" and self.isOwned(card) == "Hulk" :
                    self.drawText(screen, 25, "HULK", BLACK, 600, 750)

                elif card[1] == "Taiwan" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (575,710))

                if card[1] == "Philippines" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (460,710))

                elif card[1] == "Philippines" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (460,710))

                if card[1] == "China" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (345,710))

                elif card[1] == "China" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (345,710))

                if card[1] == "Singapore" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (230,710))

                elif card[1] == "Singapore" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (230,710))

                if card[1] == "Turkey" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (115,710))

                elif card[1] == "Turkey" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (115,710))

                if card[1] == "Egypt" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,710))

                elif card[1] == "Egypt" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,710))

                if card[1] == "Greece" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,574))

                elif card[1] == "Greece" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,574))

                if card[1] == "Denmark" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,456))

                elif card[1] == "Denmark" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,456))

                if card[1] == "Sweden" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,340))

                elif card[1] == "Sweden" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,340))

                if card[1] == "Suisse" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,224))

                elif card[1] == "Suisse" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,224))

                if card[1] == "Germany" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,107))

                elif card[1] == "Germany" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,107))

                if card[1] == "Italia" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,0))

                elif card[1] == "Italia" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (0,0))

                if card[1] == "France" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (108,2))

                elif card[1] == "France" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (108,2))

                if card[1] == "Spain" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (226,2))

                elif card[1] == "Spain" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (226,2))

                if card[1] == "UK" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (344,2))

                elif card[1] == "UK" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (344,2))

                if card[1] == "Brazil" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (462,2))

                elif card[1] == "Brazil" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (462,2))

                if card[1] == "Argentina" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (580,2))

                elif card[1] == "Argentina" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (580,2))

                if card[1] == "Australia" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (698,2))

                elif card[1] == "Australia" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (698,2))

                if card[1] == "Mexico" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,107))

                elif card[1] == "Mexico" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,107))

                if card[1] == "USA" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,224))

                elif card[1] == "USA" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,224))

                if card[1] == "Canada" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,340))

                elif card[1] == "Canada" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,340))

                if card[1] == "Japan" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,456))

                elif card[1] == "Japan" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,456))

                if card[1] == "Korea" and self.isOwned(card) == "Hulk" :
                    ownerImage = pygame.image.load("images/HulkFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,574))

                elif card[1] == "Korea" and self.isOwned(card) == "Captain":
                    ownerImage = pygame.image.load("images/CaptainFace.png")
                    scaledBoard = pygame.transform.scale(ownerImage, (90, 90))
                    screen.blit(scaledBoard, (716,574))

    def drawBuildings(self, screen):
        for player in self.players:
            if self.players[player].name == self.PID:
                color = WHITE
            else: color = BLACK
            for card in self.players[player].properties:
                if card[2] == "property" and card[7] != 0:
                    if card[0][1] == botY:
                        self.drawText(screen, 20, str(card[7]), color, card[0][0] + 15, botY - 50)
                    elif card[0][0] == leftX:
                        self.drawText(screen, 20, str(card[7]), color, leftX + 70, card[0][1] + 15)
                    elif card[0][1] == topY:
                        self.drawText(screen, 20, str(card[7]), color, card[0][0] + 15, topY + 65)
                    elif card[0][0] == rightX:
                        self.drawText(screen, 20, str(card[7]), color, rightX - 70, card[0][1] + 15)

    def drawPlayerOptions(self, screen):
        spot = self.players[self.PID].position
        card = gameBoard[spot]
        name = card[1]
        pygame.draw.rect(screen, RED, (1190, 100, 600, 600))
        self.drawText(screen, 25, "%s을(를) 밟았습니다" %name, WHITE, 1200, 150)

        event = self.drawPlayerOptionsHelper()
        if event == "owned":
            self.drawText(screen, 25, "이미 이 땅을 가지고있습니다", WHITE, 1200, 225)
            self.drawText(screen, 25, "4 -> 부동산 정보", WHITE, 1200, 450)
        elif event == "pay":
            owner = self.isOwned(card)
            rent = self.calculateRent(card, owner)
            self.drawText(screen, 25, "%s에게 $%d을 지불했습니다" %(owner,rent), WHITE, 1200, 225)
        elif event == "buyable":
            price = card[3]
            self.drawText(screen, 25, "1 -> $%d로 땅 구매" %price, WHITE, 1200, 225)
            self.drawText(screen, 25, "4 -> 부동산 정보", WHITE, 1200, 450)
        elif event == "unbuyable":
            self.drawText(screen, 25, "살 수 없는 땅입니다", WHITE, 1200, 225)

        self.drawText(screen, 25, "2 -> 땅 팔기", WHITE, 1200, 300)
        self.drawText(screen, 25, "3 -> 부동산 짓기", WHITE, 1200, 375)
        self.drawText(screen, 25, "d -> 턴 끝내기", WHITE, 1200, 525)

    def drawPlayerOptionsHelper(self):
        spot = self.players[self.PID].position
        card = gameBoard[spot]
        event = ""
        if (card[2] == "property"):
            if card in self.players[self.PID].properties:
                event = "owned"
            elif self.isOwned(card) != None:
                event = "pay"
            else:
                event = "buyable"
        else:
            event = "unbuyable"
        return event

    def drawMortgageOptions(self, screen):
        pygame.draw.rect(screen, RED, (1190, 100, 600, 600))
        self.drawText(screen, 25, "b -> 땅 팔기", WHITE, 1200, 150)
        counter = 0
        for property in self.players[self.PID].properties:
            if (property[2] == "property"):
                name = property[1]
                mortgage = property[5]
                if counter == 0:
                    color = BLACK
                else: color = WHITE
                self.drawText(screen, 25, "%s을(를) $%d에 팝니다" %(name, mortgage), color, 1200, 250+(counter*50))
                counter += 1
        self.drawText(screen, 25, "d -> 메뉴로 돌아가기", WHITE, 1200, 525)

    def drawBuildingOptions(self, screen):
        pygame.draw.rect(screen, RED, (1190, 100, 600, 600))
        self.drawText(screen, 25, "b -> 건물 짓기", WHITE, 1200, 150)
        availableCodes, buildableCards = self.buildingAvailability()[0], self.buildingAvailability()[1]
        counter = 0
        for card in buildableCards:
            name = card[1]
            cost = card[6]
            if counter == abs(self.counter%len(buildableCards)):
                color = BLACK
            else: color = WHITE
            self.drawText(screen, 25, "%s을(를) $%d로 짓습니다." %(name, cost), color, 1200, 250+(counter*50))
            counter += 1
        self.drawText(screen, 25, "d -> 메뉴로 돌아가기", WHITE, 1200, 525)

    def drawPropertyStats(self, screen):
        pygame.draw.rect(screen, RED, (1190, 100, 600, 600))
        card = gameBoard[self.players[self.PID].position]
        self.drawText(screen, 25, card[1], WHITE, 1200, 150)
        self.drawText(screen, 20, "가격: $%d" %card[3], WHITE, 1200, 200)
        self.drawText(screen, 20, "되팔기 값: $%d" %card[5], WHITE, 1200, 250)
        if card[2] == "property":
            self.drawText(screen, 20, "짓는 비용: $%d" %card[6], WHITE, 1200, 300)
            self.drawText(screen, 20, "1번째 건물 짓기: $%d" %card[4][0], WHITE, 1200, 350)
            self.drawText(screen, 20, "2번째 건물 짓기: $%d" %card[4][1], WHITE, 1200, 400)
            self.drawText(screen, 20, "3번째 건물 짓기: $%d" %card[4][2], WHITE, 1200, 450)
            self.drawText(screen, 20, "4번째 건물 짓기: $%d" %card[4][3], WHITE, 1200, 500)
            self.drawText(screen, 20, "5번째 건물 짓기: $%d" %card[4][4], WHITE, 1200, 550)
            self.drawText(screen, 20, "6번째 건물 짓기: $%d" %card[4][5], WHITE, 1200, 600)
    def drawGameOver(self, screen):
        pygame.draw.rect(screen, RED, (100, 100, 600, 600))
        self.drawText(screen, 75, "GAME OVER", WHITE, 160, 280)
        self.drawText(screen, 40, "%s loses!" %self.players[self.loser].name, WHITE, 300, 390)

####### 본 게임 함수 ##############################################################

    def eventAfterRoll(self):
        msg = ""
        spot = self.players[self.PID].position
        card = gameBoard[spot]
        if (card[2] == "property"):
            if self.isOwned(card) != None and self.isOwned(card) != self.PID:
                owner = self.isOwned(card)
                rent = self.calculateRent(card, owner)
                self.players[owner].cash += rent
                self.players[self.PID].cash -= rent
                msg = "paidRent %s %d\n" %(owner, rent)

        if (msg != ""):
            print ("sending: ", msg,)
            self.server.send(msg.encode())

    # 한가지 색의 영역을 다 가지고 있으면 조건 성립
    def buildingAvailability(self):
        availableCodes = set()
        allCodes = {}
        buildableCards = []
        for card in self.players[self.PID].properties:
            if card[2] == "property":
                buildingCode = card[8]
                if buildingCode not in allCodes:
                    allCodes[buildingCode] = 1
                else: allCodes[buildingCode] += 1
        for key in allCodes:
            if key == "red" or key == "purple":
                target = 2
            elif key == "yellow":
                target = 4
            else:
                target = 3
            if allCodes[key] == target:
                availableCodes.add(key)
        for card in self.players[self.PID].properties:
            if card[2] == "property":
                if card[8] in availableCodes and card[7] < 5:
                    buildableCards.append(card)
        return (availableCodes, buildableCards)

    def buy(self):
        msg = ""
        spot = self.players[self.PID].position
        card = gameBoard[spot]
        if self.isOwned(card) == None and (card[2] == "property"):
            self.players[self.PID].properties.append(card)
            self.players[self.PID].cash -= card[3]
            self.roundEvents.append("%s을(를) $%d로 샀습니다"%(card[1], card[3]))
            msg = "playerBought %d %d\n" %(spot, card[3])
            if (msg != ""):
                print ("sending: ", msg,)
                self.server.send(msg.encode())

    def mortgage(self):
        card = self.players[self.PID].properties[abs(self.counter%len(self.players[self.PID].properties))]
        if card[2] == "property":
            buildingCode = card[8]
        for property in self.players[self.PID].properties:
            if property[2] == "property" and property[8] == buildingCode:
                property[7] = 0
        spot = gameBoard.index(card)
        value = card[5]
        spot2 = self.players[self.PID].properties.index(card)
        if card[2] == "property":
            self.players[self.PID].properties[spot2][7] = 0
        self.players[self.PID].properties.pop(abs(self.counter%len(self.players[self.PID].properties)))
        self.players[self.PID].cash += value
        self.roundEvents.append("%s을(를) $%d에 팔았습니다" % (card[1], value))
        msg = "playerMortgaged %d %d\n" % (spot, value)
        print ("sending: ", msg,)
        self.server.send(msg.encode())

    def build(self):
        buildableCards = self.buildingAvailability()[1]
        if len(buildableCards) == 0:
            return None
        card = buildableCards[abs(self.counter%len(buildableCards))]
        spot1 = gameBoard.index(card)
        spot2 = self.players[self.PID].properties.index(card)
        cost = card[6]
        self.players[self.PID].cash -= cost
        self.players[self.PID].properties[spot2][7] += 1
        moneyFX.play()
        self.roundEvents.append("%s을(를) $%d로 지었습니다" %(card[1], cost))
        msg = "playerBuilt %d %d\n" %(spot1, cost)
        print ("sending: ", msg,)
        self.server.send(msg.encode())

    def isOwned(self, card):
        for player in self.players:
            if card in self.players[player].properties:
                return player

    def calculateRent(self, card, owner):
        if card[2] == "property":
            numHouses = card[7]
            rent = card[4][numHouses]
        return rent

    def playerTurn(self):
        x = self.currPlayer
        for player in self.players:
            if self.currNum == self.players[player].priority:
                self.currPlayer = player
        y = self.currPlayer
        if x == y and len(self.players) > 1:
            self.currNum += 1
            self.playerTurn()

    def roll(self):
        msg = ""
        self.dice_1 = random.randint(1,6)
        self.dice_2 = random.randint(1,6)
        roll = sum([self.dice_1, self.dice_2])
        self.players[self.currPlayer].position += roll
        self.players[self.currPlayer].getCoords()
        self.roundEvents.append("주사위 %d이 나왔습니다" %roll)
        self.options = True
        if self.currNum + 1 <= len(self.players):
            self.currNum += 1
        else: self.currNum = 1
        self.playerTurn()
        msg = "playerRolled %d\n" %roll
        if (msg != ""):
            print ("sending: ", msg,)
            self.server.send(msg.encode())
        self.eventAfterRoll()

########### 마우스 키보드  ######################################################

    def mousePressed(self, x, y):
        msg = ""

        if self.gameOver == True:
            return None

        if self.mouseOnReady == True and self.lobbyScreen == True:
            self.players[self.PID].ready = True
            clickFX.play()
            msg = "playerReady %s\n" %self.PID
        if self.mouseOnRoll == True and self.currPlayer == self.PID and self.options == False:
            diceFX.play()
            self.roll()
        if (msg != ""):
            print ("sending: ", msg,)
            self.server.send(msg.encode())

    def mouseMotion(self, x, y):
        if self.lobbyScreen == True:
            if x > self.readyButton[0] and x < self.readyButton[1]\
            and y > self.readyButton[2] and y < self.readyButton[3]:
                self.mouseOnReady = True
            else: self.mouseOnReady = False
        if self.gameScreen == True and self.options == False:
            if x > self.rollButton[0] and x < \
            self.rollButton[1] and y > 200 and y < 290:
                self.mouseOnRoll = True
            else: self.mouseOnRoll = False

    def keyPressed(self, keyCode, modifier):
        msg = ""

        if self.gameOver == True:
            return None

        if self.startScreen == True:
            if keyCode == pygame.K_s:
                self.startScreen = False
                self.lobbyScreen = True
                clickFX.play()
            elif keyCode == pygame.K_h:
                self.startScreen = False
                self.helpScreen = True
                clickFX.play()

        elif self.helpScreen == True:
            if keyCode == pygame.K_h:
                self.helpScreen = False
                self.startScreen = True
                clickFX.play()

        elif self.gameScreen == True:

            if keyCode == pygame.K_h:
                self.playerStats = True

            elif self.options == True and self.mortgaging == False and \
            self.building == False and self.propertyStats == False:
                if keyCode == pygame.K_d:
                    self.options = False
                    card = gameBoard[self.players[self.PID].position]
                    self.roundEvents.append("턴을 끝냈습니다")
                    clickFX.play()
                    msg = "endedTurn %d\n" %self.currNum
                elif keyCode == pygame.K_1:
                    moneyFX.play()
                    self.buy()
                elif keyCode == pygame.K_2:
                    clickFX.play()
                    self.mortgaging = True
                elif keyCode == pygame.K_3:
                    clickFX.play()
                    self.building = True
                elif keyCode == pygame.K_4:
                    clickFX.play()
                    spot = self.players[self.PID].position
                    card = gameBoard[spot]
                    if card[2] == "property":
                        self.propertyStats = True

            elif self.mortgaging == True and self.playerStats == False:
                if keyCode == pygame.K_d:
                    self.mortgaging = False
                    self.counter = 0
                elif keyCode == pygame.K_DOWN:
                    self.counter += 1
                elif keyCode == pygame.K_UP:
                    self.counter -= 1
                elif keyCode == pygame.K_b:
                    if len(self.players[self.PID].properties) > 0:
                        moneyFX.play()
                        self.mortgage()

            elif self.building == True and self.playerStats == False:
                if keyCode == pygame.K_d:
                    self.building = False
                    self.counter = 0
                elif keyCode == pygame.K_DOWN:
                    self.counter += 1
                elif keyCode == pygame.K_UP:
                    self.counter -= 1
                elif keyCode == pygame.K_b:
                    self.build()

            elif self.propertyStats == True and self.playerStats == False:
                if keyCode == pygame.K_d:
                    self.propertyStats = False

            elif self.playerStats == True:
                if keyCode == pygame.K_d:
                    self.playerStats = False
                    self.counter == 0
                elif keyCode == pygame.K_LEFT:
                    self.counter += 1
                elif keyCode == pygame.K_RIGHT:
                    self.counter -= 1

        if (msg != ""):
            print ("sending: ", msg,)
            self.server.send(msg.encode())

########## 서버 관련 ############################################################

    def timerFired(self, dt):

        if self.gameScreen == True and self.currPlayer == None:
            for player in self.players:
                if self.players[player].priority == 1:
                    self.currPlayer = player

        if self.gameScreen == True:
            for player in self.players:
                if self.players[player].cash <= 0:
                    whistleFX.play()
                    self.gameOver = True
                    self.loser = player

        if self.lobbyScreen == True:
            counter = 0
            for player in self.players:
                if self.players[player].ready == True:
                    counter += 1
            if counter == len(self.players):
                self.lobbyScreen, self.gameScreen = False, True

        while self.serverMsg.qsize() > 0:
            msg = self.serverMsg.get(False)
            try:
                print("received: ", msg, "\n")
                msg = msg.split()
                command = msg[0]
                if (command == "myIDis"):
                    myPID = msg[1]
                    self.PID = myPID
                    self.players[myPID] = Player(myPID)

                if (command == "newPlayer"):
                    newPID = msg[1]
                    self.players[newPID] = Player(newPID)

                if (command == "playerReady"):
                    PID = msg[1]
                    self.players[PID].ready = True

                if (command == "playerRolled"):
                    PID = msg[1]
                    roll = int(msg[2])
                    self.roundEvents.append("%s가 주사위 %d이 나왔습니다" %(PID, roll))
                    self.players[PID].position += roll
                    self.players[PID].getCoords()

                if (command == "endedTurn"):
                    PID = msg[1]
                    card = gameBoard[self.players[PID].position]
                    self.roundEvents.append("%s 턴이 끝났습니다" %PID)
                    self.currNum = int(msg[2])
                    self.playerTurn()

                if (command == "playerBought"):
                    PID = msg[1]
                    spot = int(msg[2])
                    cost = int(msg[3])
                    card = gameBoard[spot]
                    self.players[PID].properties.append(card)
                    self.players[PID].cash -= card[3]
                    self.roundEvents.append("%s가 %s을(를) $%d로 샀습니다" %(PID, card[1], cost))

                if (command == "paidRent"):
                    PID = msg[1]
                    owner = msg[2]
                    rent = int(msg[3])
                    self.players[PID].cash -= rent
                    self.players[owner].cash += rent
                    if self.players[owner].name == self.PID:
                        moneyFX.play()

                if (command == "playerMortgaged"):
                    PID = msg[1]
                    spot = int(msg[2])
                    card = gameBoard[spot]
                    if card[2] == "property":
                        buildingCode = card[8]
                        for property in self.players[PID].properties:
                            if property[8] == buildingCode:
                                property[7] = 0
                    value = int(msg[3])
                    self.roundEvents.append("%s가 %s을(를) $%d에 팔았습니다" % (PID, card[1], value))
                    spot2 = self.players[PID].properties.index(card)
                    self.players[PID].properties[spot2][7] = 0
                    self.players[PID].properties.remove(card)
                    self.players[PID].cash += card[5]

                if (command == "playerBuilt"):
                    PID = msg[1]
                    spot = int(msg[2])
                    card = gameBoard[spot]
                    cost = int(msg[3])
                    self.roundEvents.append("%s가 %s을(를) %d로 지었습니다" % (PID, card[1], cost))
                    self.players[PID].cash -= cost
                    spot2 = self.players[PID].properties.index(card)
                    self.players[PID].properties[spot2][7] += 1

                if (command == "raisedBid"):
                    PID = msg[1]
                    self.bid += 50
                    self.timer = 50
                    self.highestBidder = PID

            except:
                print ("failed!")
            self.serverMsg.task_done()

    def redrawAll(self, screen):
        if self.startScreen == True:
            self.drawStartScreen(screen)
        elif self.helpScreen == True:
            self.drawHelpScreen(screen)
        elif self.lobbyScreen == True:
            self.drawLobbyScreen(screen)
            if self.mouseOnReady == True:
                pygame.draw.rect(screen, GREEN, (1060, 440, 220, 200))
                self.drawText(screen, 50, "READY", BLACK, 1085, 510)
        elif self.gameScreen == True:
            self.drawGameScreen(screen)
            if self.mouseOnRoll == True:
                pygame.draw.rect(screen, GREEN, (315, 220, 180, 60))
                font = pygame.font.SysFont("Times New Roman MS", 70)
                textSurface = font.render("ROLL!", False, BLACK)
                screen.blit(textSurface, (335, 230))
            if self.options == True:
                self.drawPlayerOptions(screen)
            if self.mortgaging == True:
                self.drawMortgageOptions(screen)
            if self.building == True:
                self.drawBuildingOptions(screen)
            if self.propertyStats == True:
                self.drawPropertyStats(screen)
            # if self.auction == True:
            #     self.drawAuction(screen)
            if self.playerStats == True:
                self.drawPlayerStats(screen)
            if self.gameOver == True:
                self.drawGameOver(screen)

############ 사용하지 않은 유저  #################################################

    def mouseReleased(self, x, y):
        pass

    def mouseDrag(self, x, y):
        pass

    def keyReleased(self, keyCode, modifier):
        pass

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

######## 코드 스타트 ############################################################

    def __init__(self, width=1800, height=800, fps=50, title="부루마블"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.bgColor = (255, 255, 255)
        pygame.init()

    def run(self, serverMsg = None, server = None):

        self.server = server
        self.serverMsg = serverMsg
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self._keys = dict()
        self.init()
        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDrag(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    playing = False
            screen.fill(self.bgColor)
            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()
        self.server.close()

def main():
    game = Monopoly()
    serverMsg = Queue(1000)
    threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
    game.run(serverMsg, server)

if __name__ == '__main__':
    main()
