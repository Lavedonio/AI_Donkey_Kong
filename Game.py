__author__ = 'Batchu Vishal'
import pygame
import sys
from pygame.locals import *
from Board import Board
from pygame import mixer

'''
This class defines the logic of the game and how player input is taken etc
We run one instance of this class at the start of the game, and this instance manages the game for us.
'''


class Game:
    def __init__(self):
        '''
        Set the height and width for the game element
        FPS is set to 30 frames per second
        '''
        self.height = 520
        self.width = 1200
        self.FPS = 30
        self.clock = pygame.time.Clock()
        self.displayScreen = pygame.display.set_mode((self.width, self.height))
        # Font is set to comic sans MS
        self.myFont = pygame.font.SysFont("comicsansms", 30)

        # Create a new instance of the Board class
        self.newGame = Board(self.width, self.height)

        # Initialize the fireball timer
        self.fireballTimer = 0

        # Assign groups from the Board instance that was created
        self.playerGroup = self.newGame.playerGroup
        self.wallGroup = self.newGame.wallGroup
        self.ladderGroup = self.newGame.ladderGroup

    def runGame(self):
        while 1:
            self.clock.tick(self.FPS)
            self.scoreLabel = self.myFont.render(str(self.newGame.score), 1,
                                                 (0, 0, 0))  # Display the score on the screen

            # If the game state is not 1 then we will not have to run the game, we just need to display buttons
            if self.newGame.gameState != 1:

                self.newGame.checkButton()  # Checks the buttons for hover effects
                self.newGame.redrawScreen(self.displayScreen, self.scoreLabel, self.width,
                                          self.height)  # Redraws the buttons onto the screen

                for event in pygame.event.get():
                    # Exit to desktop
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.MOUSEBUTTONUP:
                        self.newGame.processButton()  # Check which button was clicked and change game state accordingly
                        # Assign groups again
                        self.playerGroup = self.newGame.playerGroup
                        self.wallGroup = self.newGame.wallGroup
                        self.ladderGroup = self.newGame.ladderGroup

            # This is where the actual game is run
            if self.newGame.gameState == 1:

                # Get the appropriate groups
                self.fireballGroup = self.newGame.fireballGroup
                self.coinGroup = self.newGame.coinGroup

                # Create fireballs as required, depending on the number of Donkey Kongs in our game at the moment
                if self.fireballTimer == 0:
                    self.newGame.CreateFireball(self.newGame.Enemies[0].getPosition(), 0)
                elif len(self.newGame.Enemies) >= 2 and self.fireballTimer == 23:
                    self.newGame.CreateFireball(self.newGame.Enemies[1].getPosition(), 1)
                elif len(self.newGame.Enemies) >= 3 and self.fireballTimer == 46:
                    self.newGame.CreateFireball(self.newGame.Enemies[2].getPosition(), 2)
                self.fireballTimer = (self.fireballTimer + 1) % 70

                # Animate the coin
                for coin in self.coinGroup:
                    coin.animateCoin()

                # To check collisions below, we move the player downwards then check and move him back to his original location
                self.newGame.Players[0].updateY(2)
                self.laddersCollidedBelow = self.newGame.Players[0].checkCollision(self.ladderGroup)
                self.wallsCollidedBelow = self.newGame.Players[0].checkCollision(self.wallGroup)
                self.newGame.Players[0].updateY(-2)

                # To check for collisions above, we move the player up then check and then move him back down
                self.newGame.Players[0].updateY(-2)
                self.wallsCollidedAbove = self.newGame.Players[0].checkCollision(self.wallGroup)
                self.newGame.Players[0].updateY(2)

                # Sets the onLadder state of the player
                self.newGame.ladderCheck(self.laddersCollidedBelow, self.wallsCollidedBelow, self.wallsCollidedAbove)

                for event in pygame.event.get():
                    # Exit to desktop
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()

                    if event.type == KEYDOWN:
                        # Get the ladders collided with the player
                        self.laddersCollidedExact = self.newGame.Players[0].checkCollision(self.ladderGroup)

                        if event.key == K_q:
                            # We quit the game and go to the restart screen
                            self.newGame.gameState = 2
                            self.newGame.ActiveButtons[0] = 0
                            self.newGame.ActiveButtons[1] = 1
                            self.newGame.ActiveButtons[2] = 1

                        if (event.key == K_SPACE and self.newGame.Players[0].onLadder == 0) or (
                                event.key == K_w and self.laddersCollidedExact):
                            # Set the player to move up
                            self.direction = 2
                            if self.newGame.Players[0].isJumping == 0 and self.wallsCollidedBelow:
                                # We can make the player jump and set his currentJumpSpeed
                                self.newGame.Players[0].isJumping = 1
                                self.newGame.Players[0].currentJumpSpeed = 7
                                if event.key == K_SPACE:
                                    # Play the jump sound
                                    mixer.music.load('Assets/jump.wav')
                                    mixer.music.set_volume(1)
                                    pygame.mixer.music.play()
                                    #print "Started JUMP"

                # Update the player's position and process his jump if he is jumping
                self.newGame.Players[0].continuousUpdate(self.wallGroup, self.ladderGroup)

                '''
                We use cycles to animate the character, when we change direction we also reset the cycles
                We also change the direction according to the key pressed
                '''
                keyState = pygame.key.get_pressed()
                if keyState[pygame.K_d]:
                    if self.newGame.direction != 4:
                        self.newGame.direction = 4
                        self.newGame.cycles = -1  # Reset cycles
                    self.newGame.cycles = (self.newGame.cycles + 1) % 10
                    if self.newGame.cycles < 5:
                        # Display the first image for half the cycles
                        self.newGame.Players[0].updateWH(pygame.image.load('Assets/right.png'), "H",
                                                         self.newGame.Players[0].getSpeed(), 15, 15)
                    else:
                        # Display the second image for half the cycles
                        self.newGame.Players[0].updateWH(pygame.image.load('Assets/right2.png'), "H",
                                                         self.newGame.Players[0].getSpeed(), 15, 15)
                    wallsCollidedExact = self.newGame.Players[0].checkCollision(self.wallGroup)
                    if wallsCollidedExact:
                        # If we have collided a wall, move the player back to where he was in the last state
                        self.newGame.Players[0].updateWH(pygame.image.load('Assets/right.png'), "H",
                                                         -self.newGame.Players[0].getSpeed(), 15, 15)

                if keyState[pygame.K_a]:
                    if self.newGame.direction != 3:
                        self.newGame.direction = 3
                        self.newGame.cycles = -1  # Reset cycles
                    self.newGame.cycles = (self.newGame.cycles + 1) % 10
                    if self.newGame.cycles < 5:
                        # Display the first image for half the cycles
                        self.newGame.Players[0].updateWH(pygame.image.load('Assets/left.png'), "H",
                                                         -self.newGame.Players[0].getSpeed(), 15, 15)
                    else:
                        # Display the second image for half the cycles
                        self.newGame.Players[0].updateWH(pygame.image.load('Assets/left2.png'), "H",
                                                         -self.newGame.Players[0].getSpeed(), 15, 15)
                    wallsCollidedExact = self.newGame.Players[0].checkCollision(self.wallGroup)
                    if wallsCollidedExact:
                        # If we have collided a wall, move the player back to where he was in the last state
                        self.newGame.Players[0].updateWH(pygame.image.load('Assets/left.png'), "H",
                                                         self.newGame.Players[0].getSpeed(), 15, 15)

                # If we are on a ladder, then we can move up
                if keyState[pygame.K_w] and self.newGame.Players[0].onLadder:
                    self.newGame.Players[0].updateWH(pygame.image.load('Assets/still.png'), "V",
                                                     -self.newGame.Players[0].getSpeed() / 2, 15, 15)
                    if len(self.newGame.Players[0].checkCollision(self.ladderGroup)) == 0 or len(
                            self.newGame.Players[0].checkCollision(self.wallGroup)) != 0:
                        self.newGame.Players[0].updateWH(pygame.image.load('Assets/still.png'), "V",
                                                         self.newGame.Players[0].getSpeed() / 2, 15, 15)

                # If we are on a ladder, then we can move down
                if keyState[pygame.K_s] and self.newGame.Players[0].onLadder:
                    self.newGame.Players[0].updateWH(pygame.image.load('Assets/still.png'), "V",
                                                     self.newGame.Players[0].getSpeed() / 2, 15, 15)

                # Redraws all our instances onto the screen
                self.newGame.redrawScreen(self.displayScreen, self.scoreLabel, self.width, self.height)

                # Update the fireball and check for collisions with player (ie Kill the player)
                self.newGame.fireballCheck()

                # Collect a coin
                coinsCollected = pygame.sprite.spritecollide(self.newGame.Players[0], self.coinGroup, True)
                self.newGame.coinCheck(coinsCollected)

                # Check if you have reached the princess
                self.newGame.checkVictory(self.clock)

                # Update all the Donkey Kongs
                for enemy in self.newGame.Enemies:
                    enemy.continuousUpdate(self.wallGroup, self.ladderGroup)

            # Update the display to view our changes
            pygame.display.update()


if __name__ == "__main__":
    pygame.init()
    # Initialize the mixer for music
    mixer.init()
    # Instantiate the Game class and run the game
    createdGame = Game()
    createdGame.runGame()
