__author__ = 'Batchu Vishal'
import pygame
import math
import random
import sys

from pygame import mixer
from Person import Person
from OnBoard import OnBoard
from Coin import Coin
from Player import Player
from Fireball import Fireball
from DonkeyKong import DonkeyKong
from Button import Button

# Initialize the mixer
mixer.init()

'''
This class defines our gameboard.
A gameboard contains everthing related to our game on it like our characters, walls, ladders, coins etc
The generation of the level also happens in this class.
'''


class Board:
    def __init__(self, width, height):
        self.__width = width
        self.__actHeight = height
        self.__height = self.__actHeight + 10
        self.score = 0
        self.gameState = 0
        self.cycles = 0  # For the characters animation
        self.direction = 0

        self.white = (255, 255, 255)

        '''
        The map is essentially an array of 30x80 in which we store what each block on our map is.
        1 represents a wall, 2 for a ladder and 3 for a coin.
        '''
        self.map = []
        # These are the arrays in which we store our instances of different classes
        self.Players = self.Enemies = self.Allies = self.Coins = self.Walls = self.Ladders = self.Fireballs = self.Hearts = self.Boards = self.FireballEndpoints = []

        # Resets the above groups and initializes the game for us
        self.resetGroups()

        # The buttons used in the pregame and postgame screens
        self.Buttons = [Button(pygame.image.load('Assets/start.png'), (500, 400), "start"),
                        Button(pygame.image.load('Assets/exit.png'), (700, 400), "exit"),
                        Button(pygame.image.load('Assets/restart.png'), (500, 400), "restart"), ]
        self.ActiveButtons = [1, 1, 0]  # Initially the pregame screen uses the first 2 buttons
        self.myfont = pygame.font.SysFont("comicsansms", 50)

        self.background = pygame.image.load('Assets/background.png')
        self.background = pygame.transform.scale(self.background, (width, height))
        self.startbackground = pygame.image.load('Assets/buttonbackground.jpg')
        self.startbackground = pygame.transform.scale(self.startbackground, (width, height))

        # Initialize the instance groups which we use to display our instances on the screen
        self.fireballGroup = pygame.sprite.RenderPlain(self.Fireballs)
        self.playerGroup = pygame.sprite.RenderPlain(self.Players)
        self.enemyGroup = pygame.sprite.RenderPlain(self.Enemies)
        self.wallGroup = pygame.sprite.RenderPlain(self.Walls)
        self.ladderGroup = pygame.sprite.RenderPlain(self.Ladders)
        self.coinGroup = pygame.sprite.RenderPlain(self.Coins)
        self.allyGroup = pygame.sprite.RenderPlain(self.Allies)
        self.fireballEndpointsGroup = pygame.sprite.RenderPlain(self.FireballEndpoints)
        self.boardGroup = pygame.sprite.RenderPlain(self.Boards)
        self.heartGroup = pygame.sprite.RenderPlain(self.Hearts)

    def resetGroups(self):
        self.score = 0
        self.map = []  # We will create the map again when we reset the game
        self.Players = [Player(pygame.image.load('Assets/still.png'), (50, 440))]
        self.Enemies = [DonkeyKong(pygame.image.load('Assets/kong0.png'), (100, 117))]
        self.Allies = [Person(pygame.image.load('Assets/princess.png'), (50, 55))]
        self.Allies[0].updateWH(self.Allies[0].image, "H", 0, 25, 25)
        self.Coins = []
        self.Walls = []
        self.Ladders = []
        self.Fireballs = []
        self.Hearts = [OnBoard(pygame.image.load('Assets/heart.png'), (730, 490)),
                       OnBoard(pygame.image.load('Assets/heart.png'), (750, 490)),
                       OnBoard(pygame.image.load('Assets/heart.png'), (770, 490))]
        self.Hearts[0].modifySize(pygame.image.load('Assets/heart.png'), 20, 20)
        self.Hearts[1].modifySize(pygame.image.load('Assets/heart.png'), 20, 20)
        self.Hearts[2].modifySize(pygame.image.load('Assets/heart.png'), 20, 20)
        self.Boards = [OnBoard(pygame.image.load('Assets/board.png'), (200, 480)),
                       OnBoard(pygame.image.load('Assets/board.png'), (685, 480))]
        self.Boards[0].modifySize(self.Boards[0].image, 40, 150)  # Do this on purpose to get a pixelated image
        self.Boards[1].modifySize(self.Boards[1].image, 40, 150)
        self.FireballEndpoints = [OnBoard(pygame.image.load('Assets/still.png'), (50, 440))]
        self.initializeGame()  # This initializes the game and generates our map
        self.createGroups()  # This creates the instance groups

    # Checks to destroy a fireball when it reaches its terminal point
    def checkFireballDestroy(self, fireball):
        if pygame.sprite.spritecollide(fireball, self.fireballEndpointsGroup, False):
            self.DestroyFireball(fireball.index)  # We use indices on fireballs to uniquely identify each fireball

    # Creates a new fireball and adds it to our fireball group
    def CreateFireball(self, location, kongIndex):
        if len(self.Fireballs) < len(self.Enemies) * 6+6:
            self.Fireballs.append(
                Fireball(pygame.image.load('Assets/fireballright.png'), (location[0], location[1] + 15), len(self.Fireballs),
                         2 + len(self.Enemies)/2))
            # Starts DonkeyKong's animation
            self.Enemies[kongIndex].setStopDuration(15)
            self.Enemies[kongIndex].setPosition(
                (self.Enemies[kongIndex].getPosition()[0], self.Enemies[kongIndex].getPosition()[1] - 12))
            self.Enemies[kongIndex].setCenter(self.Enemies[kongIndex].getPosition())
            # if 5 > self.Fireballs[len(self.Fireballs)-1].speed:
            #    self.Fireballs[len(self.Fireballs)-1].speed=self.Fireballs[len(self.Fireballs)-1].speed+1
            self.createGroups()  # We recreate the groups so the fireball is added

    # Destroy a fireball if it has collided with a player or reached its endpoint
    def DestroyFireball(self, index):
        for fireBall in range(len(self.Fireballs)):
            if self.Fireballs[fireBall].index == index:
                self.Fireballs.remove(self.Fireballs[fireBall])
                for fireBallrem in range(
                        len(self.Fireballs)):  # We need to reduce the indices of all fireballs greater than this
                    if self.Fireballs[fireBallrem].index > index:
                        self.Fireballs[fireBallrem].index -= 1
                self.createGroups()  # Recreate the groups so the fireball is removed
                break

    # Randomly Generate coins in the level where there is a wall below the coin so the player can reach it
    def GenerateCoins(self):
        for i in range(6, len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] == 0 and ((i + 1 < len(self.map) and self.map[i + 1][j] == 1) or (
                            i + 2 < len(self.map) and self.map[i + 2][j] == 1)):
                    randNumber = math.floor(random.random() * 1000)
                    if randNumber % 35 == 0 and len(self.Coins) <= 25:  # At max there will be 26 coins in the map
                        self.map[i][j] = 3
                        if j - 1 >= 0 and self.map[i][j - 1] == 3:
                            self.map[i][j] = 0
                        if self.map[i][j] == 3:
                            # Add the coin to our coin list
                            self.Coins.append(Coin(pygame.image.load('Assets/coin1.png'), (j * 15 + 15 / 2, i * 15 + 15 / 2)))
        if len(self.Coins) <= 20:  # If there are less than 21 coins, we call the function again
            self.GenerateCoins()

    # Given a position and checkNo ( 1 for wall, 2 for ladder, 3 for coin) the function tells us if its a valid position to place or not
    def checkMapForMatch(self, placePosition, floor, checkNo, offset):
        if floor < 1:
            return 0
        for i in range(0, 5):  # We will get things placed atleast 5-1 blocks away from each other
            if self.map[floor * 5 - offset][placePosition + i] == checkNo:
                return 1
            if self.map[floor * 5 - offset][placePosition - i] == checkNo:
                return 1
        return 0

    # Create an empty 2D map of 30x80 size
    def makeMap(self):
        for point in range(0, self.__height / 15 + 1):
            row = []
            for point2 in range(0, self.__width / 15):
                row.append(0)
            self.map.append(row)

    # Add walls to our map boundaries and also the floors
    def makeWalls(self):
        for i in range(0, (self.__height / 15) - 4):
            self.map[i][0] = self.map[i][self.__width / 15 - 1] = 1
        for i in range(0, (self.__height / (15 * 5))):
            for j in range(0, self.__width / 15):
                self.map[i * 5][j] = 1

    # Make a small chamber on the top where the princess resides
    def makePrincessChamber(self):
        for j in range(0, 5):
            self.map[j][9] = 1
        for j in range(10, (self.__width / 15) - 1):
            self.map[1 * 5][j] = 0
        for j in range(0, 5):
            self.map[1 * 5 + j][7] = self.map[1 * 5 + j][8] = 2

    # Generate ladders randomly, 1 for each floor such that they are not too close to each other
    def makeLadders(self):
        for i in range(2, (self.__height / (15 * 5) - 1)):
            ladderPos = math.floor(random.random() * (self.__width / 15 - 20))
            ladderPos = int(10 + ladderPos)
            while self.checkMapForMatch(ladderPos, i - 1, 2, 0) == 1:
                ladderPos = math.floor(random.random() * (self.__width / 15 - 20))
                ladderPos = int(10 + ladderPos)
            for k in range(0, 5):
                self.map[i * 5 + k][ladderPos] = self.map[i * 5 + k][ladderPos + 1] = 2

    # Generate a few broken ladders, such that they are not too close to each other
    def makeBrokenLadders(self):
        for i in range(2, (self.__height / (15 * 5) - 1)):
            if i % 2 == 1:
                brokenLadderPos = math.floor(random.random() * (self.__width / 15 - 20))
                brokenLadderPos = int(10 + brokenLadderPos)
                # Make sure aren't too close to other ladders or broken ladders
                while self.checkMapForMatch(brokenLadderPos, i - 1, 2, 0) == 1 or self.checkMapForMatch(brokenLadderPos,i, 2,0) == 1 or self.checkMapForMatch(brokenLadderPos, i + 1, 2, 0) == 1:
                    brokenLadderPos = math.floor(random.random() * (self.__width / 15 - 20))
                    brokenLadderPos = int(10 + brokenLadderPos)
                # Randomly make the broken edges of the ladder
                brokenRand = int(math.floor(random.random() * 100)) % 2
                brokenRand2 = int(math.floor(random.random() * 100)) % 2
                for k in range(0, 1):
                    self.map[i * 5 + k][brokenLadderPos] = self.map[i * 5 + k][brokenLadderPos + 1] = 2
                for k in range(3 + brokenRand, 5):
                    self.map[i * 5 + k][brokenLadderPos] = 2
                for k in range(3 + brokenRand2, 5):
                    self.map[i * 5 + k][brokenLadderPos + 1] = 2

    # Create the holes on each floor (extreme right and extreme left)
    def makeHoles(self):
        for i in range(3, (self.__height / (15 * 5) - 1)):
            for k in range(1, 6):  # Ladders wont interfere since they leave 10 blocks on either side
                if i % 2 == 0:
                    self.map[i * 5][k] = 0
                else:
                    self.map[i * 5][self.__width / 15 - 1 - k] = 0

    '''
    This is called once you have finished making holes, ladders, walls etc
    You use the 2D map to add instances to the groups
    '''

    def populateMap(self):
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y] == 1:
                    # Add a wall at that position
                    self.Walls.append(OnBoard(pygame.image.load('Assets/wood_block.png'), (y * 15 + 15 / 2, x * 15 + 15 / 2)))
                elif self.map[x][y] == 2:
                    # Add a ladder at that position
                    self.Ladders.append(OnBoard(pygame.image.load('Assets/ladder.png'), (y * 15 + 15 / 2, x * 15 + 15 / 2)))

    # Check if the player is on a ladder or not
    def ladderCheck(self, laddersCollidedBelow, wallsCollidedBelow, wallsCollidedAbove):
        if laddersCollidedBelow and len(wallsCollidedBelow) == 0:
            for ladder in laddersCollidedBelow:
                if ladder.getPosition()[1] >= self.Players[0].getPosition()[1]:
                    self.Players[0].onLadder = 1
                    self.Players[0].isJumping = 0
                    # Move the player down if he collides a wall above
                    if wallsCollidedAbove:
                        #print "HIT HEAD"
                        self.Players[0].updateY(3)
                    #print "ON LADDER!"
        else:
            self.Players[0].onLadder = 0

    # Update all the fireball positions and check for collisions with player
    def fireballCheck(self):
        for fireball in self.fireballGroup:
            fireball.continuousUpdate(self.wallGroup, self.ladderGroup)
            if fireball.checkCollision(self.playerGroup, "V"):
                if len(self.Hearts) >= 2:  # Reduce the player's life by 1
                    self.Fireballs.remove(fireball)
                    self.Hearts.pop(len(self.Hearts) - 1)
                    self.Players[0].setPosition((50, 440))
                    mixer.music.load('Assets/death.wav')
                    mixer.music.set_volume(1)
                    pygame.mixer.music.play()
                    print "YOU DIED"
                    self.score -= 25
                    if self.score < 0:
                        self.score = 0
                    self.createGroups()
                else:  # The player has lost all lives, so end the game
                    self.gameState = 2
                    self.ActiveButtons[0] = 0
                    self.ActiveButtons[1] = 1
                    self.ActiveButtons[2] = 1
            self.checkFireballDestroy(fireball)

    # Check for coins collided and add the appropriate score
    def coinCheck(self, coinsCollected):
        for coin in coinsCollected:
            self.score += coin.collectCoin()
            # We also remove the coin entry from our map
            self.map[(coin.getPosition()[1] - 15 / 2) / 15][(coin.getPosition()[0] - 15 / 2) / 15] = 0
            # Remove the coin entry from our list
            self.Coins.remove(coin)
            # Update the coin group since we modified the coin list
            self.createGroups()

    # Check if the player wins
    def checkVictory(self, clock):
        # If you touch the princess or reach the floor with the princess you win!
        if self.Players[0].checkCollision(self.allyGroup) or self.Players[0].getPosition()[1] < 5 * 15:

            print "VICTORY"
            mixer.music.load('Assets/levelcomplete.wav')  # Victory sound
            mixer.music.set_volume(1)
            pygame.mixer.music.play()
            clock.tick(100)  # A delay of 0.1 second before the next level starts
            self.score += 50

            # This is just the next level so we only clear the fireballs and regenerate the coins
            self.Fireballs = []
            self.Players[0].setPosition((50, 440))
            self.Coins = []
            self.GenerateCoins()

            # Add Donkey Kongs
            if len(self.Enemies) == 1:
                self.Enemies.append(DonkeyKong(pygame.image.load('Assets/kong0.png'), (700, 117)))
            elif len(self.Enemies) == 2:
                self.Enemies.append(DonkeyKong(pygame.image.load('Assets/kong0.png'), (400, 117)))
            # Create the groups again so the enemies are effected
            self.createGroups()

    # When a button is clicked perform the needed actions
    def processButton(self):
        # If the start button is pressed
        if self.ActiveButtons[0] == 1 and self.Buttons[0].rect.collidepoint(pygame.mouse.get_pos()):
            self.resetGroups()
            self.gameState = 1
            self.ActiveButtons[0] = 0
            self.ActiveButtons[1] = 0
            self.ActiveButtons[2] = 0
        # If the exit button is pressed
        if self.ActiveButtons[1] == 1 and self.Buttons[1].rect.collidepoint(pygame.mouse.get_pos()):
            pygame.quit()
            sys.exit()
        # If the restart button is pressed
        if self.ActiveButtons[2] == 1 and self.Buttons[2].rect.collidepoint(pygame.mouse.get_pos()):
            self.gameState = 0
            self.ActiveButtons[0] = 1
            self.ActiveButtons[1] = 1
            self.ActiveButtons[2] = 0

    # Checks for mouse hovers over buttons to change their images giving a hover button effect
    def checkButton(self):
        mousePosition = pygame.mouse.get_pos()
        for button in range(len(self.Buttons)):
            # If the button is active
            if self.ActiveButtons[button] == 1 and self.Buttons[button].rect.collidepoint(mousePosition):
                if button == 0:
                    self.Buttons[button].changeImage(pygame.image.load('Assets/start1.png'))
                elif button == 1:
                    self.Buttons[button].changeImage(pygame.image.load('Assets/exit1.png'))
                elif button == 2:
                    self.Buttons[button].changeImage(pygame.image.load('Assets/restart1.png'))
            # Inactive button
            else:
                if button == 0:
                    self.Buttons[button].changeImage(pygame.image.load('Assets/start.png'))
                elif button == 1:
                    self.Buttons[button].changeImage(pygame.image.load('Assets/exit.png'))
                elif button == 2:
                    self.Buttons[button].changeImage(pygame.image.load('Assets/restart.png'))

    # Redraws the entire game screen for us
    def redrawScreen(self, displayScreen, scoreLabel, width, height):
        displayScreen.fill((0, 0, 0))  # Fill it with black
        # If we are in either pregame or postgame states
        if self.gameState != 1:
            displayScreen.blit(self.startbackground, self.startbackground.get_rect())
            if self.gameState == 0:
                # Pregame state
                displayScreen.blit(pygame.image.load('Assets/donkeykongtext.png'), (340, 50))
            if self.gameState == 2:
                # Post game state
                label = self.myfont.render("Your score is " + str(self.score), 1, (255, 255, 255))
                displayScreen.blit(label, (410, 70))
            for button in range(len(self.ActiveButtons)):
                if self.ActiveButtons[button] == 1:
                    displayScreen.blit(self.Buttons[button].image, self.Buttons[button].getTopLeftPosition())
        # We are in the game state
        if self.gameState == 1:
            # Draw the background first
            displayScreen.blit(self.background, self.background.get_rect())
            # Draw all our groups on the background
            self.ladderGroup.draw(displayScreen)
            self.playerGroup.draw(displayScreen)
            self.coinGroup.draw(displayScreen)
            self.wallGroup.draw(displayScreen)
            self.fireballGroup.draw(displayScreen)
            self.enemyGroup.draw(displayScreen)
            self.allyGroup.draw(displayScreen)
            self.boardGroup.draw(displayScreen)
            displayScreen.blit(scoreLabel, (265-scoreLabel.get_width()/2, 470)) #Center the text on the board
            self.heartGroup.draw(displayScreen)

    # Update all the groups from their corresponding lists
    def createGroups(self):
        self.fireballGroup = pygame.sprite.RenderPlain(self.Fireballs)
        self.playerGroup = pygame.sprite.RenderPlain(self.Players)
        self.enemyGroup = pygame.sprite.RenderPlain(self.Enemies)
        self.wallGroup = pygame.sprite.RenderPlain(self.Walls)
        self.ladderGroup = pygame.sprite.RenderPlain(self.Ladders)
        self.coinGroup = pygame.sprite.RenderPlain(self.Coins)
        self.allyGroup = pygame.sprite.RenderPlain(self.Allies)
        self.fireballEndpointsGroup = pygame.sprite.RenderPlain(self.FireballEndpoints)
        self.boardGroup = pygame.sprite.RenderPlain(self.Boards)
        self.heartGroup = pygame.sprite.RenderPlain(self.Hearts)

    '''
    Initialize the game by making the map, generating walls, generating princess chamber, generating ladders randomly,
    generating broken ladders randomly, generating holes, generating coins randomly, adding the ladders and walls to our lists
    and finally updating the groups.
    '''

    def initializeGame(self):
        self.makeMap()
        self.makeWalls()
        self.makePrincessChamber()
        self.makeLadders()
        self.makeBrokenLadders()
        self.makeHoles()
        self.GenerateCoins()
        self.populateMap()
        self.createGroups()
