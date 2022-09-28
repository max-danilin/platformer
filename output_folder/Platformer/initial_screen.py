import pygame
import sys
from settings import *
from neat_game import Neat
from game import Platformer


class Button:
    """
    Class for drawing animated button
    """
    def __init__(self, surface, pos, size, font, text):
        """
        sound_timeout - used to determine how often button sound will be played in case of consecutive clicks
        upper - upper rect of a button
        initial_upper - initial rect positions of upper(to correctly process area available for clicks)
        lower - lower rect of a button
        :param surface: surface to draw button on
        :param pos: position of a button
        :param size: size of a button
        :param font: font for rendering text
        :param text: text to render
        """
        self.surface = surface
        self.sound = pygame.mixer.Sound(COIN_SOUND_DIR)
        self.sound.set_volume(0.1)
        self.sound_timeout = 0

        # Rect
        self.upper = pygame.Rect(pos, size)
        self.initial_upper = pygame.Rect(pos, size)
        self.initial_y = self.upper.y
        self.lower = pygame.Rect((self.upper.x, self.upper.y+BUTTON_ELEVATION), size)

        # Flags
        self.pressed = False
        self.was_pressed = False

        # Processing multiple lines of text on a single button
        self.multiple_text = False
        self.render_list = []
        self.rect_list = []
        self.initial_text_y = []
        # Render text
        self.render_text(font, text)

    def render_text(self, font, text):
        """
        Rendering text on a button and managing multiple lines of text
        """
        if '\n' in text:
            self.multiple_text = True
            new_text = text.split('\n')
            i = 0
            for idx, item in enumerate(new_text):
                self.render_list.append(font.render(item, True, BUTTON_TEXT_COLOR))
                cy = int(self.upper.y + self.upper.height / len(new_text) * (0.5 + i))
                self.rect_list.append(self.render_list[idx].get_rect(center=(self.upper.centerx, cy)))
                self.initial_text_y.append(self.rect_list[idx].y)
                i += 1
        else:
            self.surf_text = font.render(text, True, BUTTON_TEXT_COLOR)
            self.text_rect = self.surf_text.get_rect(center=self.upper.center)
            self.text_initial_y = self.text_rect.y

    def draw(self):
        """
        Draws button and blits text on top of it
        Keep track of previous button state to prevent situations when mouse was pressed before colliding with button.
        Changes button color if mouse hovers over it, animate button when it was pressed and ensure that text moves
        with button.
        """
        allow_pressing = True
        mouse_pressed = pygame.mouse.get_pressed(3)[0]
        pygame.draw.rect(self.surface, BUTTON_LOWER_COLOR, self.lower, border_radius=5)

        if pygame.Rect.collidepoint(self.initial_upper, pygame.mouse.get_pos()):
            pygame.draw.rect(self.surface, BUTTON_PRESSED_COLOR, self.upper, border_radius=5)
            # Checking mouse state when it wasn't colliding with button
            if self.was_pressed:
                allow_pressing = False
                if not mouse_pressed:
                    allow_pressing = True
                    self.was_pressed = False
            # Press button when allowed
            if mouse_pressed and allow_pressing:
                self.pressed = True
                self.upper.y = self.initial_y + BUTTON_ELEVATION
                # Text rendering
                if self.multiple_text:
                    for idx, item in enumerate(self.initial_text_y):
                        self.rect_list[idx].y = item + BUTTON_ELEVATION
                else:
                    self.text_rect.y = self.text_initial_y + BUTTON_ELEVATION
            else:
                self.pressed = False
        else:
            self.pressed = False
            self.was_pressed = mouse_pressed
            pygame.draw.rect(self.surface, BUTTON_COLOR, self.upper, border_radius=5)

        # Revert button to its previous position if not pressed
        if not self.pressed:
            self.upper.y = self.initial_y
            if self.multiple_text:
                for idx, item in enumerate(self.initial_text_y):
                    self.rect_list[idx].y = item
            else:
                self.text_rect.y = self.text_initial_y

        # Blit text
        if self.multiple_text:
            for idx in range(len(self.render_list)):
                self.surface.blit(self.render_list[idx], self.rect_list[idx])
        else:
            self.surface.blit(self.surf_text, self.text_rect)

        self.sound_timeout += 1


class InitialScreen:
    """
    Class for rendering initial screen and drawing it on a surface
    """
    def __init__(self):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()

        # Background image
        self.image = pygame.image.load(INITIAL_BACK_DIR).convert()
        self.image = pygame.transform.scale(self.image, (self.image.get_width(), screen_height))
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.image_for_loop = self.image.copy()
        self.rect_for_loop = self.image_for_loop.get_rect(topleft=(screen_width, 0))

        # Welcome image
        self.welcome = pygame.image.load(WELCOME_DIR).convert_alpha()
        self.welcome_rect = self.welcome.get_rect(topleft=WELCOME_POS)

        # Music
        pygame.mixer.init()
        self.channel = pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL+3)
        self.sound = pygame.mixer.Sound(MUSIC_DIR)
        self.sound.set_volume(0.03)

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont(FONT_STD, FONT_SIZE)

        # Buttons
        self.neat = Button(self.screen, (screen_width/8+BUTTON_SPACING, BUTTON_Y), BUTTON_SIZE, self.font, 'Run NEAT')
        self.neat_multiple = Button(self.screen, (screen_width/8+BUTTON_SPACING*2, BUTTON_Y), BUTTON_SIZE, self.font,
                                    'Run NEAT\nMultiple')
        self.normal = Button(self.screen, (screen_width/8, BUTTON_Y), BUTTON_SIZE, self.font, 'Play game')
        self.buttons = [self.neat, self.neat_multiple, self.normal]
        # Defining button modes
        self.neat.mode = 'neat'
        self.neat_multiple.mode = 'neat multiple'
        self.normal.mode = 'game'

        self.initial_run = True

    def animate(self):
        """
        Make background image seamlessly looping while moving it. We have to create additional copy of image
        to make it blit when initial image reaches edge of the screen.
        """
        self.rect.x -= BACK_ANIMATION_SPEED
        if self.rect.right - screen_width <= 0:
            self.screen.blit(self.image_for_loop, self.rect_for_loop)
            looping = True
            if self.rect.right <= 0:
                self.rect.x = 0
                looping = False
        else:
            looping = False
        if looping:
            self.rect_for_loop.x -= BACK_ANIMATION_SPEED
        else:
            self.rect_for_loop.x = screen_width

    def no_draw_message(self):
        font = pygame.font.SysFont('Georgia', 60)
        surf_text = font.render('Running Neat without drawing', True, 'red')
        text_rect = surf_text.get_rect(center=(screen_width/2, screen_height/2-50))
        self.screen.blit(surf_text, text_rect)

    def set_mode(self, mode):
        """
        Setting game mode based on pressed button
        :param mode: game mode of neat, neat multiple or usual game
        """
        self.sound.stop()
        self.initial_run = False
        if mode in ('neat', 'neat multiple'):
            if mode == 'neat':
                neat = Neat()
            else:
                neat = Neat(multiple=True)
            if not Neat.draw:
                self.screen.blit(self.image, self.image.get_rect(topleft=(0, 0)))
                self.no_draw_message()
                pygame.display.flip()
            neat.run_neat()
            Neat.generation = 0
            self.initial_run = Neat.return_to_initial
            Neat.return_to_initial = False
        else:
            game = Platformer()
            game.run()
            self.initial_run = game.return_to_initial
            game.return_to_initial = False

    def run(self):
        """
        Run initial screen in the beginning and in case of return from any game mode. Process button clicks and
        starting corresponding game mode.
        """
        started = True
        while True:
            if self.initial_run:
                if started:
                    self.sound.play(loops=-1)
                    started = False
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()

                self.screen.blit(self.image, self.rect)
                self.animate()
                self.screen.blit(self.welcome, self.welcome_rect)

                for button in self.buttons:
                    button.draw()
                    if button.pressed and button.sound_timeout > BUTTON_SOUND_TIMEOUT:
                        button.sound.play()
                        button.sound_timeout = 0
                    if button.pressed:
                        self.set_mode(button.mode)
                        started = True

                pygame.display.update()
                self.clock.tick(CLOCK_RATE)


if __name__ == '__main__':
    initial = InitialScreen()
    initial.run()
