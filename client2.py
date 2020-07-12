# README: You must read the README file (its not that long!) so that you can
# fully understand how to correctly enter saved games, and begin games. If you
# don't, you will inevitably run into bugs!

# The rules of the game have been modified to suit a more fast-paced cut-throat
# style of gameplay that will hopefully shorten the length of games

#############################
# Started code from 15-112 sockets manual, I have barely modified it
# Run code and barebones input functions (redrawAll, mousePressed, etc.)
# were taken from the 15-112 Pygame manual
# Sockets Client Demo
# by Rohan Varma
# adapted by Kyle Chin
#############################

import sys
import socket
import threading
from queue import Queue

if (len(sys.argv)) == 1:
  HOST = "localhost" # Server can now only be accessed on this machine
else:
  HOST = str(sys.argv[1]) # IP address that the user must supply when running the python file

HOST = "localhost" # put your IP address here if playing on multiple computers
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

########### Global Variables ###################################################

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


######## Classes ###############################################################

class Player(object):

    allPlayers = []

    def __init__(self, name):
        Player.allPlayers.append(self)
        self.name = name
        self.priority = len(Player.allPlayers)
        self.position = 0
        self.coords = [740, 740] # Coordinates of the "Go" position
        piece = pygame.image.load("images/player_%s.png" %self.name)
        scaledPiece = pygame.transform.scale(piece, playerSize)
        self.piece = scaledPiece
        self.ready = False
        self.cash = 1500
        self.properties = []

    def __repr__(self):
        return self.name + str(self.priority)

    # Updates coordinates of the players piece whenever their position changes
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
        self.PID = None # The client's name
        self.startScreen = True
        self.helpScreen = False
        self.lobbyScreen = False
        self.gameScreen = False
        self.gameOver = False
        self.loser = None

        # These values are used to help make buttons interactive
        self.mouseOnRoll = False
        self.rollButton = (800, 200)
        self.mouseOnReady = False
        self.readyButton = (1050, 1290, 430, 650)

        # Game data
        self.dice_1 = 1
        self.dice_2 = 1
        self.currNum = 1
        self.currPlayer = None
        self.players = {}
        self.roundEvents = []
        self.counter = 0

        # Player turn popups
        self.options = False
        self.playerStats = False
        self.mortgaging = False
        self.building = False
        self.propertyStats = False

################################################################################
############ Draw Functions ####################################################
################################################################################

    # Many magic numbers are used in these functions that way I can make the
    # GUI look precise and pleasing. The drawback of this is that the game can
    # now only be run on a 1300 by 800 canvas, with no exceptions. This was also
    # done to save time when coding

    # Helper function called whenever I need to draw text
    def drawText(self, screen, size, text, color, x, y):
        font = pygame.font.SysFont("malgungothic", size)
        textSurface = font.render(text, False, color)
        screen.blit(textSurface,(x,y))

    def drawStartScreen(self, screen):
        screen.fill((255,0,0))
        image = pygame.image.load("images/logo.png")
        screen.blit(image, (10,10))
        self.drawText(screen, 100, "S를 눌러 시작합시다!", WHITE, 200, 500)
        self.drawText(screen, 60, "H를 누르면 도움창이 나옵니다!", WHITE, 400, 670)

    def drawHelpScreen(self, screen):
        screen.fill(RED)
        image = pygame.image.load("images/logo.png")
        screen.blit(image, (10,10))
        self.drawText(screen, 20, "This version of monopoly has modified rules to suit a faster-paced style of gampeplay. Modifications include:", WHITE, 100, 400)
        self.drawText(screen, 20, "- Community chest now either gives cash or a card", WHITE, 100, 425)
        self.drawText(screen, 20, "- Chance teleports you a random distance", WHITE, 100, 450)
        self.drawText(screen, 20, "- Going to jail is now only a fine", WHITE, 100, 475)
        self.drawText(screen, 20, "To load the previous saved game with friends:", WHITE, 100, 525)
        self.drawText(screen, 20, "- You must have same number of players as in the save", WHITE, 100, 550)
        self.drawText(screen, 20, "- You must have all entered the server in the same order as in the save file", WHITE, 100, 575)
        self.drawText(screen, 20, "- All your friends must have the same save file", WHITE, 100, 600)
        self.drawText(screen, 20, "- Load the save at the same time by pressing 's' while on this screen", WHITE, 100, 625)
        self.drawText(screen, 60, "Press 'h' for return", WHITE, 400, 670)

    def drawLobbyScreen(self, screen):
        image = pygame.image.load("images/logo.png")
        screen.blit(image, (10,10))
        pygame.draw.rect(screen, RED, (1050, 430, 240, 220))
        pygame.draw.rect(screen, WHITE, (1060, 440, 220, 200))
        self.drawText(screen, 50, "READY", BLACK, 1085, 510)
        counter = 0
        for i in self.players:
            scaledPiece = pygame.transform.scale(self.players[i].piece, (220,220))
            screen.blit(scaledPiece, (50+(250*counter), 450))
            if i == self.PID:
                self.drawText(screen, 30, "You", BLACK, 120+(250*counter), 400)
            else:
                self.drawText(screen, 30, "%s" %self.players[i].name, BLACK, 120+(250*counter), 400)
            if self.players[i].ready == False:
                self.drawText(screen, 20, "Not ready", BLACK,\
                100+(250*counter), 700)
            else: self.drawText(screen, 20, "Ready", BLACK,\
            100+(250*counter), 700)
            counter += 1

###### Game Screen Drawings ####################################################

    def drawGameScreen(self, screen):
        self.drawBoard(screen)
        self.drawPlayers(screen)
        self.drawRoll(screen)
        self.drawDie(screen)
        self.drawPortraits(screen)
        self.drawActivityLog(screen)
        self.drawInstructions(screen)
        self.drawBuildings(screen)

    def drawBoard(self, screen):
        board = pygame.image.load("images/monopoly.png")
        scaledBoard = pygame.transform.scale(board, (800, 800))
        screen.blit(scaledBoard, (0,0))

    def drawPlayers(self, screen):
        for player in Player.allPlayers:
            screen.blit(player.piece, player.coords)

    def drawRoll(self, screen):
        pygame.draw.rect(screen, RED, (800, 0, 500, 200))
        pygame.draw.rect(screen, WHITE, (810, 10, 480, 180))
        self.drawText(screen, 120, "ROLL!", BLACK, 875, 20)

    def drawDie(self, screen):
        # These dice are giving me an odd error saying:
        # libpng warning: iCCP: known incorrect sRGB profile
        dice1 = pygame.image.load("images/dice_%s.png" %self.dice_1)
        dice2 = pygame.image.load("images/dice_%s.png" %self.dice_2)
        screen.blit(dice1, (810, 220))
        screen.blit(dice2, (960, 220))

    def drawInstructions(self, screen):
        self.drawText(screen, 20, "H를 누르면 볼 수 있습니다.", BLACK, 1090, 230)
        self.drawText(screen, 20, "플레이어 상태", BLACK, 1090, 250)
        self.drawText(screen, 20, "현재 게임 상태", BLACK, 1090, 290)

    def drawPortraits(self, screen):
        counter = 0
        for i in self.players:
            scaledPiece = pygame.transform.scale\
            (self.players[i].piece, (100,100))
            screen.blit(scaledPiece, (810+(125*counter), 700))
            if i == self.PID:
                self.drawText(screen, 20, "You", BLACK, 840+(125*counter),670)
            else:
                self.drawText(screen, 20, "%s"%self.players[i].name, BLACK, 840+(125*counter),670)
            counter += 1

    def drawActivityLog(self, screen):
        self.drawText(screen, 20, "현황판:", BLACK, 810, 360)
        pygame.draw.rect(screen, BLACK, (805, 400, 490, 260))
        pygame.draw.rect(screen, WHITE, (810, 405, 480, 250))
        if len(self.roundEvents) > 9:
            self.roundEvents.pop(0)
        counter = 0
        for event in self.roundEvents:
            self.drawText(screen, 20, event, BLACK, 820, 410+(counter*25))
            counter += 1

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
        #Finding the name of the spot I landed on
        spot = self.players[self.PID].position
        card = gameBoard[spot]
        name = card[1]
        pygame.draw.rect(screen, RED, (100, 100, 600, 600))
        self.drawText(screen, 25, "%s을(를) 밟았습니다" %name, WHITE, 150, 150)

        event = self.drawPlayerOptionsHelper()
        if event == "owned":
            self.drawText(screen, 25, "이미 이 땅을 소유하고 있습니다", WHITE, 150, 225)
            self.drawText(screen, 25, "4 -> 부동산 정보", WHITE, 150, 450)
        elif event == "pay":
            owner = self.isOwned(card)
            rent = self.calculateRent(card, owner)
            self.drawText(screen, 25, "$%d으로 %s을(를) 샀습니다" %(rent,owner), WHITE, 150, 225)
        elif event == "buyable":
            price = card[3]
            self.drawText(screen, 25, "1 -> $%d로 땅 구매" %price, WHITE, 150, 225)
            self.drawText(screen, 25, "4 -> 부동산 정보", WHITE, 150, 450)
        elif event == "unbuyable":
            self.drawText(screen, 25, "이 땅을 살 수 없습니다", WHITE, 150, 225)

        self.drawText(screen, 25, "2 -> 땅 팔기", WHITE, 150, 300)
        self.drawText(screen, 25, "3 -> 부동산 짓기", WHITE, 150, 375)
        self.drawText(screen, 25, "d -> 턴 끝내기", WHITE, 150, 525)

    # This function determines what text will pop up after a roll
    def drawPlayerOptionsHelper(self):
        spot = self.players[self.PID].position
        card = gameBoard[spot]
        event = ""
        if (card[2] == "property" or card[2] == "utility" or card[2] == "railroad"):
            if card in self.players[self.PID].properties:
                event = "owned"
            elif self.isOwned(card) != None:
                event = "pay"
            else:
                event = "buyable"
        else:
            event = "unbuyable"
        return event
    #대출
    def drawMortgageOptions(self, screen):
        pygame.draw.rect(screen, RED, (100, 100, 600, 600))
        self.drawText(screen, 25, "b -> 땅 팔기", WHITE, 150, 150)
        counter = 0
        for property in self.players[self.PID].properties:
            if (property[2] == "property" or property[2] == "utility" or property[2] == "railroad"):
                name = property[1]
                mortgage = property[5]
                if counter == abs(self.counter%len(self.players[self.PID].properties)):
                    color = BLACK
                else: color = WHITE
                self.drawText(screen, 25, "%s을(를) $%d에 팝니다" %(name, mortgage), color, 150, 250+(counter*50))
                counter += 1
        self.drawText(screen, 25, "d -> 메뉴로 돌아가기", WHITE, 150, 525)

    def drawBuildingOptions(self, screen):
        pygame.draw.rect(screen, RED, (100, 100, 600, 600))
        self.drawText(screen, 25, "b -> 건물 짓기", WHITE, 150, 150)
        availableCodes, buildableCards = self.buildingAvailability()[0], self.buildingAvailability()[1]
        counter = 0
        for card in buildableCards:
            name = card[1]
            cost = card[6]
            if counter == abs(self.counter%len(buildableCards)):
                color = BLACK
            else: color = WHITE
            self.drawText(screen, 25, "%s을(를) $%d로 지었습니다" %(name, cost), color, 150, 250+(counter*50))
            counter += 1
        self.drawText(screen, 25, "d -> 메뉴로 돌아가기", WHITE, 150, 525)

    def drawPlayerStats(self, screen):
        pygame.draw.rect(screen, RED, (100, 100, 600, 600))
        i = self.counter % len(self.players)
        scaledPiece = pygame.transform.scale(Player.allPlayers[i].piece, (100,100))
        screen.blit(scaledPiece, (350, 120))
        self.drawText(screen, 20, "재산: $%d" %Player.allPlayers[i].cash, WHITE, 150, 250)
        counter = 0
        for property in Player.allPlayers[i].properties:
            if property[2] == "property":
                if property[7] == 5:
                    self.drawText(screen, 20, "%s with a hotel" %property[1], WHITE, 150, 300+(counter*50))
                else:
                    if property[7] == 1:
                        buildings = "house"
                    elif property[7] < 5:
                        buildings = "houses"
                    self.drawText(screen, 20, "%s with %d %s" %(property[1], property[7], buildings), WHITE, 150, 300+(counter*50))
            else: self.drawText(screen, 20, property[1], WHITE, 150, 300+(counter*50))
            counter += 1
        self.drawText(screen, 25, "Press right to view next player", WHITE, 150, 475)
        self.drawText(screen, 25, "d -> 나가기", WHITE, 150, 525)

    def drawPropertyStats(self, screen):
        pygame.draw.rect(screen, RED, (100, 100, 600, 600))
        card = gameBoard[self.players[self.PID].position]
        self.drawText(screen, 25, card[1], WHITE, 150, 150)
        self.drawText(screen, 20, "가격: $%d" %card[3], WHITE, 150, 200)
        self.drawText(screen, 20, "되팔기 값: $%d" %card[5], WHITE, 150, 250)
        if card[2] == "property":
            self.drawText(screen, 20, "짓는 비용: $%d" %card[6], WHITE, 150, 300)
            self.drawText(screen, 20, "1번째 건물 짓기: $%d" %card[4][0], WHITE, 150, 350)
            self.drawText(screen, 20, "2번째 건물 짓기: $%d" %card[4][1], WHITE, 150, 400)
            self.drawText(screen, 20, "3번째 건물 짓기: $%d" %card[4][2], WHITE, 150, 450)
            self.drawText(screen, 20, "4번째 건물 짓기: $%d" %card[4][3], WHITE, 150, 500)
            self.drawText(screen, 20, "5번째 건물 짓기: $%d" %card[4][4], WHITE, 150, 550)
            self.drawText(screen, 20, "6번째 건물 짓기: $%d" %card[4][5], WHITE, 150, 600)
        elif card[2] == "railroad":
            self.drawText(screen, 20, "Rent increases by $50 for every", WHITE, 150, 300)
            self.drawText(screen, 20, "railroad that you own.", WHITE, 150, 330)
        elif card[2] == "utility":
            self.drawText(screen, 20, "If you own one utility, rent is", WHITE, 150, 300)
            self.drawText(screen, 20, "4 times the number the player rolls.", WHITE, 150, 330)
            self.drawText(screen, 20, "With two utilities, the rent is 10", WHITE, 150, 360)
            self.drawText(screen, 20, "times the number the player rolls", WHITE, 150, 390)
        self.drawText(screen, 25, "Press 'd' to return to menu", WHITE, 150, 650)

    def drawGameOver(self, screen):
        pygame.draw.rect(screen, RED, (100, 100, 600, 600))
        self.drawText(screen, 75, "GAME OVER", WHITE, 160, 280)
        self.drawText(screen, 40, "%s loses!" %self.players[self.loser].name, WHITE, 300, 390)

################################################################################
####### Monopoly Game Functions ################################################
################################################################################

    # Determines if rent must be paid after roll then modifies client data
    def eventAfterRoll(self):
        msg = ""
        spot = self.players[self.PID].position
        card = gameBoard[spot]
        if (card[2] == "property" or card[2] == "utility" or card[2] == "railroad"):
            if self.isOwned(card) != None and self.isOwned(card) != self.PID:
                owner = self.isOwned(card)
                rent = self.calculateRent(card, owner)
                self.players[owner].cash += rent
                self.players[self.PID].cash -= rent
                msg = "paidRent %s %d\n" %(owner, rent)
        elif card[2] == "communityChest":
            self.communityChest()

        if (msg != ""):
            print ("sending: ", msg,)
            self.server.send(msg.encode())

    # Returns which properties can be built on
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
            if key == "brown" or key == "purple":
                target = 2
            else: target = 3
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
        if self.isOwned(card) == None and (card[2] == "property" or card[2] == "railroad" or card[2] == "utility"):
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
        elif card[2] == "railroad":
            counter = -1
            for ownedCard in self.players[owner].properties:
                if ownedCard[2] == "railroad":
                    counter += 1
            rent = 50 + (50*counter)
        elif card[2] == "utility":
            counter = 0
            for ownedCard in self.players[owner].properties:
                if ownedCard[2] == "utility":
                    counter += 1
            if counter == 1:
                rent = 4 * (self.dice_1 + self.dice_2)
            elif counter == 2:
                rent = 10 * (self.dice_1 + self.dice_2)
        return rent

    def communityChest(self):
        chest = random.choice(["money", "money", "money", "card"])
        if chest == "money":
            money = random.randint(-1, 2) * 100
            if money > 0:
                moneyFX.play()
            self.players[self.PID].cash += money
            self.roundEvents.append("You got $%d from the chest!" %money)
            msg = "communityChest 0 %d\n" %money
        elif chest == "card":
            possibilities = []
            for card in cards:
                type = cards[card][2]
                if self.isOwned(cards[card]) == None and (type == "property" or type == "railroad" or type == "utility"):
                    possibilities.append(cards[card])
            choice = random.randint(0, len(possibilities))
            spot = gameBoard.index(possibilities[choice])
            self.players[self.PID].properties.append(possibilities[choice])
            self.roundEvents.append("You got %s from the chest!" %possibilities[choice][1])
            msg = "communityChest 1 %d\n" %spot
        print ("sending: ", msg,)
        self.server.send(msg.encode())

    # Determines which player's turn is next based on priority
    def playerTurn(self):
        x = self.currPlayer
        for player in self.players:
            if self.currNum == self.players[player].priority:
                self.currPlayer = player
        y = self.currPlayer
        if x == y and len(self.players) > 1:
            self.currNum += 1
            self.playerTurn()

    # Outputs random dice roll and sets in motion player turn events
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

########### User Interaction Functions #########################################

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

    # I only use this function to make buttons interactive
    def mouseMotion(self, x, y):
        if self.lobbyScreen == True:
            if x > self.readyButton[0] and x < self.readyButton[1]\
            and y > self.readyButton[2] and y < self.readyButton[3]:
                self.mouseOnReady = True
            else: self.mouseOnReady = False
        if self.gameScreen == True and self.options == False:
            #Checks to see if mouse is over the "Roll!" button
            if x > self.rollButton[0] and x < \
            self.width and y < self.rollButton[1]:
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
            self.building == False and self.playerStats == False:
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
                        if card[2] == "property" or card[2] == "railroad" or card[2] == "utility":
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

########## timerFired ##########################################################

    # Timerfired checks for all incoming data from the server and processes it
    def timerFired(self, dt):

        # Selects the first current player (which will always be "Hat")
        if self.gameScreen == True and self.currPlayer == None:
            for player in self.players:
                if self.players[player].priority == 1:
                    self.currPlayer = player

        if self.gameScreen == True:
            for player in self.players:
                if self.players[player].cash <= 0 and len(self.players[player].properties) == 0:
                    whistleFX.play()
                    self.gameOver = True
                    self.loser = player

        # Checks to see if all players are ready to begin the game
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

                if (command == "communityChest"):
                    PID = msg[1]
                    type = int(msg[2])
                    if type == 0:
                        money = int(msg[3])
                        self.players[PID].cash += money
                        self.roundEvents.append("%s got $%d from the chest!" %(PID, money))
                    if type == 1:
                        spot = int(msg[3])
                        card = gameBoard[spot]
                        self.players[PID].properties.append(card)
                        self.roundEvents.append("%s got %s from the chest!" %(PID, card[1]))

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
                #Did not use drawText function because I wanted a different font
                pygame.draw.rect(screen, GREEN, (810, 10, 480, 180))
                font = pygame.font.SysFont("Times New Roman MS", 150)
                textSurface = font.render("ROLL!", False, BLACK)
                screen.blit(textSurface, (890, 50))
            if self.options == True:
                self.drawPlayerOptions(screen)
            if self.mortgaging == True:
                self.drawMortgageOptions(screen)
            if self.building == True:
                self.drawBuildingOptions(screen)
            if self.propertyStats == True:
                self.drawPropertyStats(screen)
            if self.playerStats == True:
                self.drawPlayerStats(screen)
            if self.gameOver == True:
                self.drawGameOver(screen)

############ Unused starter functions ##########################################

    def mouseReleased(self, x, y):
        pass

    def mouseDrag(self, x, y):
        pass

    def keyReleased(self, keyCode, modifier):
        pass

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

######## Run functions from starter code #######################################

    def __init__(self, width=1300, height=800, fps=50, title="부루마블"):
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
        # set the title of the window
        pygame.display.set_caption(self.title)
        # stores all the keys currently being held down
        self._keys = dict()
        # call game-specific initialization
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
