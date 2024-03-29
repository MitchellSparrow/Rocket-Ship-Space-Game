import pygame
import os
import platform
from globals import *
from rocket import Rocket
from Asteroids import Asteroid
import pickle
from BgMovement import BgMovement


class run_scratch:
    '''The main class for the scratch game'''

    ### DEFAULT GAME SETTINGS ###
    click = False
    play_music = True
    highscore = 0
    score = 0
    height = HEIGHT
    width = WIDTH
    fullscreen = False
    play_again = False
    quit = False

    def __init__(self):
        '''Function which initializes the game'''

        # Initialize pygame
        pygame.init()

        # Try to load the settings file and update the global variables
        try:
            file = open("settings.txt", "rb")
            settings = pickle.load(file)
            self.play_music = settings['play_music']
            self.highscore = settings['highscore']
            self.height = settings['height']
            self.width = settings['width']
            file.close()
        except FileNotFoundError:
            pass

        # Initialise the screen, background, display and clock
        self.max_width, self.max_height = pygame.display.Info(
        ).current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE)
        self.background = pygame.image.load(
            "./Images/Backgrounds/Space_Background_1080.jpg")
        self.finish_line = pygame.image.load(
            "./Images/Finish_line/Finish_line.png")
        pygame.display.set_caption("Team Scratch")
        self.rocket_image = pygame.image.load("./Images/Rockets/Rocket1.png")
        self.clock = pygame.time.Clock()
        self.flash_count = 0

        # Initialize Moving Background
        self.BgMovement = BgMovement()

        # Initialize Asteroids for the Play screen
        self.asteroids = []
        for i in range(NUM_ASTEROIDS):
            self.asteroids.append(Asteroid(
                self.width, self.height, self.width * (1 + i/NUM_ASTEROIDS)))

        # Initialise Rocket - For the Play screen
        self.rocket = Rocket(self.width, self.height, self.fullscreen)

        # Initialise Rockets and Asteroids - For the Tutorial screen
        self.Trocket = Rocket(self.width, self.height, self.fullscreen)
        self.T_asteroid = Asteroid(self.width, self.height, self.width)

        # Initialize Music
        self.background_music = pygame.mixer.music.load(
            "./Music/background.mp3")
        if self.play_music:
            pygame.mixer.music.play(
                -1)

        # Run the Game
        self.run()

    def show_home_screen(self):
        '''Function which displays the home screen of the game'''

        # Show static background image on home screen
        self.screen.blit(self.background, (0, 0))
        rotated_rocket = pygame.transform.rotate(self.rocket_image, 25)
        self.screen.blit(rotated_rocket, (self.width/10, self.height/2))
        mx, my = pygame.mouse.get_pos()

        # Home screen button options
        button_1 = pygame.Rect(
            self.width/2-75, self.height*4/5 - 12.5, 150, 50)
        button_2 = pygame.Rect(
            self.width/3-75, self.height*4/5 - 12.5, 150, 50)
        button_3 = pygame.Rect(
            2*self.width/3-75, self.height*4/5 - 12.5, 150, 50)

        if button_1.collidepoint((mx, my)):
            if self.click:
                self.settings()

        if button_2.collidepoint((mx, my)):
            if self.click:
                self.tutorial()

        if button_3.collidepoint((mx, my)):
            if self.click:
                self.quit = True
                self.exit()

        pygame.draw.rect(self.screen, LIGHTBLUE, button_1, border_radius=20)
        pygame.draw.rect(self.screen, LIGHTBLUE, button_2, border_radius=20)
        pygame.draw.rect(self.screen, LIGHTBLUE, button_3, border_radius=20)

        self.draw_text("Settings", 20, WHITE,
                       self.width/2, self.height*4/5)
        self.draw_text("Tutorial", 20, WHITE,
                       self.width/3, self.height*4/5)
        self.draw_text("Quit", 20, WHITE,
                       2*self.width/3, self.height*4/5)

        self.click = False

        # Fullscreen / Resizeable text on homescreen
        if self.fullscreen:
            self.draw_text_title(TITLE, 80, WHITE,
                                 self.width / 2, self.height / 6)
            self.draw_text(f"High Score: {self.highscore}",
                           30, WHITE, self.width / 2, self.height / 2.8)
            self.flash_text("Press space to start playing!",
                            30, WHITE, self.width / 2, self.height / 1.8)
        else:
            self.draw_text_title(TITLE, 70, WHITE,
                                 self.width / 2, self.height / 6)
            self.draw_text(f"High Score: {self.highscore}",
                           22, WHITE, self.width / 2, self.height / 2.8)

            self.flash_text("Press space to start playing!",
                            22, WHITE, self.width / 2, self.height / 1.8)

        # Update display
        pygame.display.flip()

    def flash_text(self, text, size, colour, x, y):
        '''Function to display flashing text'''
        self.flash_count += 1
        if self.flash_count <= int(FPS / (2 * FLASH_RATE)):
            self.draw_text(text,
                           size, colour, x, y)
        elif self.flash_count == int(FPS / FLASH_RATE):
            self.flash_count = 0

    def play(self):
        '''Function which starts the game'''

        # Local function variables
        running = True
        play_collision = False

        # Reset rocket to original position
        self.rocket.reset(self.width / 2, self.height / 2)
        for asteroid in self.asteroids:
            asteroid.reset(
                self.width, self.height, self.width * (1 + self.asteroids.index(asteroid)
                                                       / NUM_ASTEROIDS))
        # Reset background and start line
        self.BgMovement.reset()

        while running:
            # Move and draw the background, with start line
            self.BgMovement.run(self.screen, self.background)

            # Move and draw the rocket each game tick
            self.rocket.run(self.screen, self.width, self.height)

            # Set score to 0 before adding the accumulative asteroids score
            self.score = 0

            # Move and draw all asteroids each game tick
            for asteroid in self.asteroids:
                asteroid.run(self.screen, self.rocket,
                             self.width, self.height)
                self.score += asteroid.points
                if asteroid.collision:
                    play_collision = True

            # Show the score in the top left corner of the screen
            self.draw_text(f"Score: {self.score - NUM_ASTEROIDS}",
                           30, WHITE, 100, 10)

            # Update the screen and wait before looping again
            pygame.display.update()
            self.clock.tick(FPS)

            # Check if any keys were pressed or if the window was resized
            running = self.get_key()

            # Check if there was a collision between the rocket and an asteroid
            if play_collision:
                # Update the high score if necessary
                if self.score - NUM_ASTEROIDS > self.highscore:
                    self.highscore = self.score - NUM_ASTEROIDS
                # Explode rocket and show game over screen
                self.rocket.Explosion(self.screen, self.clock)
                self.game_over()
                # Reset background and start line
                self.BgMovement.reset()
                # Reset the rocket to the middle position
                self.rocket.reset(self.width / 2, self.height / 2)
                # Reset all of the asteroids
                for asteroid in self.asteroids:
                    asteroid.reset(
                        self.width, self.height, self.width * (1 + self.asteroids.index(asteroid)
                                                               / NUM_ASTEROIDS))
                # Check if the user wants to play again - if not, break out of play loop
                if not self.play_again:
                    running = False
                play_collision = False
                self.play_again = False

    def get_key(self):
        '''Function which checks what keys were pressed, if the window
        was resized or if the game was exited by the user'''

        e = pygame.event.poll()
        if e.type == pygame.QUIT:
            self.exit()
            self.quit = True
            return False
        # If the user presses ESC then go back
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                return False
        # Check if the user clicked
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                self.click = True
        # Check if the user resized the window
        if e.type == pygame.VIDEORESIZE:
            if self.fullscreen is not True:
                self.width = e.w
                self.height = e.h
                self.screen = pygame.display.set_mode(
                    (e.w, e.h), pygame.RESIZABLE)
        return True

    def game_over(self):
        '''Function which shows the game over screen'''
        # Local function variables
        running = True

        while running:
            # Show the static background with a static rocket image
            self.screen.blit(self.background, (0, 0))
            rotated_rocket = pygame.transform.rotate(self.rocket_image, 25)
            self.screen.blit(rotated_rocket, (self.width/10, self.height/2))

            # Text on game over screen - Fullscreen / Resizeable
            self.click = False

            # Fullscreen / Resizeable text on game over screen
            if self.fullscreen:
                self.draw_text_title("GAME OVER", 72, WHITE,
                                     self.width / 2, self.height / 5)
                self.draw_text(f"Score: {self.score - NUM_ASTEROIDS}",
                               40, WHITE, self.width / 2, self.height / 3)
                self.draw_text("Press ESC to return to home",
                               30, WHITE, self.width / 2, self.height / 2.2)
                self.flash_text("Press space to try again!",
                                48, WHITE, self.width / 2, self.height / 1.5)

            else:
                self.draw_text_title("GAME OVER", 70, WHITE,
                                     self.width / 2, self.height / 6)
                self.draw_text(f"Score: {self.score - NUM_ASTEROIDS}",
                               30, WHITE, self.width / 2, self.height / 3)
                self.draw_text("Press ESC to return to home",
                               22, WHITE, self.width / 2, self.height / 2.2)
                self.flash_text("Press space to try again!",
                                22, WHITE, self.width / 2, self.height / 1.5)

            # Update display and wait
            pygame.display.update()
            self.clock.tick(FPS)

            # Event handling - 'X' button click, ESC press, SPACE press, resize window
            e = pygame.event.poll()
            if e.type == pygame.QUIT:
                self.exit()
                running = False
                self.quit = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    running = False
                    self.play_again = True
            if e.type == pygame.VIDEORESIZE:
                if self.fullscreen is not True:
                    self.width = e.w
                    self.height = e.h
                    self.screen = pygame.display.set_mode(
                        (e.w, e.h), pygame.RESIZABLE)

    def tutorial(self):
        '''Function which shows the tutorial screen'''
        # Local function variables
        running = True
        # Reset rocket and asteroids to their original positions
        self.Trocket.reset(self.width / 2.1, self.height / 1.5)
        self.T_asteroid.reset(self.width, self.height, self.width)

        while running:
            # Show the static background
            self.screen.blit(self.background, (0, 0))

            # Tutorial rocket and asteroid - move and draw them
            key = pygame.key.get_pressed()
            self.Trocket.Movement(self.width, self.height)
            self.Trocket.Draw(self.screen)
            self.T_asteroid.Movement(self.width, self.height)
            self.T_asteroid.Draw(self.screen)

            # Fullscreen / Resizeable text on tutorial screen
            if self.fullscreen:
                self.draw_text_title("Tutorial",
                                     72, WHITE, self.width / 2, self.height / 7)
                self.draw_text("The Up, Down, Left, Right arrowkeys move your rocket. You can test this now!",
                               20, WHITE, self.width / 2, 2*self.height / 6)
                self.draw_text("Avoid the asteroids for as long as possible",
                               20, WHITE, self.width / 2, 3*self.height / 6)
                self.draw_text("Your score increases with asteroids passed, try to beat the high score!",
                               20, WHITE, self.width / 2, 4*self.height / 6)
            else:
                self.draw_text_title("Tutorial",
                                     70, WHITE, self.width / 2, self.height / 7.5)
                self.draw_text("The Up, Down, Left, Right arrowkeys move your rocket. You can test this now!",
                               20, WHITE, self.width / 2, 2*self.height / 6)
                self.draw_text("Avoid the asteroids for as long as possible",
                               20, WHITE, self.width / 2, 3*self.height / 6)
                self.draw_text("Your score increases with asteroids passed, try to beat the high score!",
                               20, WHITE, self.width / 2, 4*self.height / 6)

            # Update display and wait
            pygame.display.update()
            self.clock.tick(FPS)

            # Event handling - 'X' button click, ESC press, resize window
            running = self.get_key()

    def draw_text(self, text, size, color, x, y):
        '''Function which draws NORMAL text on the screen with a specific font, size and colour'''
        font = pygame.font.Font("./Fonts/GamePlayed.ttf", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_text_title(self, text, size, color, x, y):
        '''Function which draws a TITLE text on the screen with a specific font, size and colour'''
        font = pygame.font.Font("./Fonts/Retronoid1.ttf", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def settings(self):
        '''Function which shows the settings screen'''
        # Local function variables
        running = True
        self.click = False

        while running:

            # Get the mouse position
            mx, my = pygame.mouse.get_pos()

            # Draw Background and text to the settings screen
            self.screen.blit(self.background, (0, 0))
            self.draw_text_title("SETTINGS", 70, WHITE,
                                 self.width / 2, self.height / 7)
            self.draw_text("Press ESC to go back",
                           22, WHITE, self.width / 2, self.height / 3)
            self.draw_text("MUSIC",
                           40, WHITE, self.width / 3, self.height / 2)
            self.draw_text("FULLSCREEN",
                           40, WHITE, self.width / 3, int(self.height / 1.5))

            # Create ON/OFF buttons
            on_off_button = pygame.Rect(
                self.width*2/3 - 30, self.height/2, 60, 40)

            on_off_button2 = pygame.Rect(
                self.width*2/3 - 30, self.height/1.5, 60, 40)

            # Change the music button text and layout depending on state
            if self.play_music:
                pygame.draw.rect(self.screen, LIGHTBLUE,
                                 on_off_button, border_radius=20)
                self.draw_text("ON", 20, WHITE,
                               self.width*2/3, self.height/2 + 7.5)
            else:
                pygame.draw.rect(self.screen, WHITE,
                                 on_off_button, border_radius=20)
                self.draw_text("OFF", 20, LIGHTBLUE,
                               self.width*2/3, self.height/2 + 7.5)

            # Play or pause the music
            if on_off_button.collidepoint((mx, my)):
                if self.click:
                    if self.play_music:
                        pygame.mixer.music.pause()
                        self.play_music = False
                    else:
                        pygame.mixer.music.play(-1)
                        self.play_music = True

           # Change the fullscreen button text and layout depending on state
            if self.fullscreen:
                pygame.draw.rect(self.screen, LIGHTBLUE,
                                 on_off_button2, border_radius=20)
                self.draw_text("ON", 20, WHITE,
                               self.width*2/3, self.height/1.5 + 7.5)
            else:
                pygame.draw.rect(self.screen, WHITE,
                                 on_off_button2, border_radius=20)
                self.draw_text("OFF", 20, LIGHTBLUE,
                               self.width*2/3, self.height/1.5 + 7.5)

            # Change the screen to a windowed or fullscreen option
            if on_off_button2.collidepoint((mx, my)):
                if self.click:
                    self.fullscreen = not self.fullscreen
                    # The rocket size changes depending on the display size otherwise the game would
                    # be too easy, therefore the rocket needs to be re-initialized on this change
                    self.rocket = Rocket(
                        self.width, self.height, self.fullscreen)
                    self.Trocket = Rocket(
                        self.width, self.height, self.fullscreen)
                    if self.fullscreen is True:
                        try:
                            # Load correct resolution background, update local variables and set to fullscreen mode
                            bg_path = "./Images/Backgrounds/Space_Background_" + \
                                str(self.max_height) + ".jpg"
                            self.background = pygame.image.load(bg_path)
                        except:
                            # If can't find a background with same resolution, use 1080 px height
                            bg_path = "./Images/Backgrounds/Space_Background_1080.jpg"
                            self.background = pygame.image.load(bg_path)

                        # Set the display to fullscreen
                        self.width = self.max_width
                        self.height = self.max_height
                        self.screen = pygame.display.set_mode(
                            (self.width, self.height), pygame.FULLSCREEN)

                    else:
                        # Load smaller background, set window to default size
                        bg_path = "./Images/Backgrounds/Space_Background_1080.jpg"
                        self.background = pygame.image.load(bg_path)
                        self.screen = pygame.display.set_mode(
                            (1000, 600), pygame.RESIZABLE)

            # Update display
            self.click = False
            pygame.display.update()
            self.clock.tick(FPS)

            # Event handling - 'X' button click, ESC press, MOUSEBUTTON click, resize window
            running = self.get_key()

    def run(self):
        '''Function which is the main game loop'''

        while not self.quit:

            # Show home screen by default
            self.show_home_screen()

            # Clock for home screen
            self.clock.tick(FPS)

            # Event handling - MOUSEBUTTON click, 'X' button click, SPACE press, resize window
            e = pygame.event.poll()
            if e.type == pygame.QUIT:
                self.exit()
                break
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.click = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    # Loop the play screen until the user exits or returns home after game end
                    self.play()
            if e.type == pygame.VIDEORESIZE:
                if self.fullscreen is not True:
                    self.width = e.w
                    self.height = e.h
                    self.screen = pygame.display.set_mode(
                        (e.w, e.h), pygame.RESIZABLE)

    def exit(self):
        # Program termination
        # For Windows or Linux users
        if platform.system() in ['Windows', 'Linux']:
            pygame.quit()
        # For Mac users.
        else:
            os._exit(0)

        # Open the settings file
        file = open("settings.txt", "wb")

        # Save the users screen width and height, their music preference, and highscore
        if not self.fullscreen:
            pickle.dump({'play_music': self.play_music,
                         'highscore': self.highscore,
                         'width': self.width,
                         'height': self.height}, file)
        else:
            pickle.dump({'play_music': self.play_music,
                         'highscore': self.highscore,
                         'width': WIDTH,
                         'height': HEIGHT}, file)
        # Close the settings file
        file.close()


# Lets run the game
run_scratch()
