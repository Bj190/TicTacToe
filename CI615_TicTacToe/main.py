import pygame
import sys


#initlise
pygame.init()
#Constants
WIN_SIZE = 900
ROWS, COLS = 3,3
CELL_SIZE = WIN_SIZE // 3
#Display
screen = pygame.display.set_mode([WIN_SIZE] * 2)
pygame.display.set_caption('Tic Tac Toe')
font = pygame.font.SysFont('Verdana', CELL_SIZE // 4, True)
#Images
field_image = pygame.transform.scale(pygame.image.load('resources/field.png'), (WIN_SIZE, WIN_SIZE))
O_image = pygame.transform.scale(pygame.image.load('resources/o.png'), (CELL_SIZE, CELL_SIZE))
X_image = pygame.transform.scale(pygame.image.load('resources/x.png'), (CELL_SIZE, CELL_SIZE))
vec2 = pygame.math.Vector2
CELL_CENTER = vec2(CELL_SIZE / 2)
# Colors
LINE_COLOR = (255, 0, 0)

class Button:
    def __init__(self, text, pos, size, callback):
        self.rect = pygame.Rect(pos, size)
        self.text = font.render(text, True, 'white')
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 3)
        text_rect = self.text.get_rect(center=self.rect.center)
        surface.blit(self.text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

class Tile:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.value = ""

    def draw(self, surface):
        if self.value == "X":
            surface.blit(X_image, self.rect.topleft)
        elif self.value == "O":
            surface.blit(O_image, self.rect.topleft)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw_x(self):
        self.value = "X"

    def draw_o(self):
        self.value = "O"

    def get_center(self):
        return self.rect.center

class TicTacToeGame:
    def __init__(self):
        self.tiles = [[Tile(row, col) for col in range(COLS)] for row in range(ROWS)]
        self.playable = True
        self.turn_x = True
        self.winning_combo = None
        self.winner = None
        self.font_Game = font
        self.status_message = None
        self.status_time = 0
        self.game_paused = False

        button_width = 300
        button_height = 60
        gap = 20
        center_x = WIN_SIZE // 2 - button_width // 2
        start_y = WIN_SIZE // 3 + 100
        self.buttons = [
            Button("Audio", (center_x, start_y), (button_width, button_height), self.audio_button),
            Button("Option", (center_x, start_y + (button_height + gap)), (button_width, button_height), self.option_button),
            Button("Quit", (center_x, start_y + 2 * (button_height + gap)), (button_width, button_height), self.quit_button)
        ]

    def draw(self, surface):
        if self.game_paused:
            self.inGameMenu(surface)
        else:
            surface.blit(field_image, (0, 0))
            for row in self.tiles:
                for tile in row:
                    tile.draw(surface)

            if self.winning_combo:
                pygame.draw.line(surface, LINE_COLOR,
                                 self.winning_combo[0],
                                 self.winning_combo[1],
                                 CELL_SIZE // 8)

            self.draw_status(surface)

    def handle_click(self, pos):
        if not self.playable:
            return

        for row in self.tiles:
            for tile in row:
                if tile.is_clicked(pos) and tile.value == "":
                    if self.turn_x:
                        tile.draw_x()
                    else:
                        tile.draw_o()
                    self.turn_x = not self.turn_x
                    self.update_status_message()
                    self.check_winner()
                    return
                
    def check_winner(self):
        combos = []

        # Rows and columns
        for i in range(ROWS):
            combos.append([self.tiles[i][0], self.tiles[i][1], self.tiles[i][2]])  # Row
            combos.append([self.tiles[0][i], self.tiles[1][i], self.tiles[2][i]])  # Column

        # Diagonals
        combos.append([self.tiles[0][0], self.tiles[1][1], self.tiles[2][2]])
        combos.append([self.tiles[0][2], self.tiles[1][1], self.tiles[2][0]])

        for combo in combos:
            if combo[0].value != "" and combo[0].value == combo[1].value == combo[2].value:
                self.playable = False
                start = combo[0].get_center()
                end = combo[2].get_center()
                self.winning_combo = (start, end)
                self.winner = combo[0].value
                break
        #Tie
        if all(tile.value != "" for row in self.tiles for tile in row):
            self.playable = False
            self.winner = None

    def draw_status(self, surface):
        now = pygame.time.get_ticks()
        label = None
        sub_label = None

        match (self.winner, self.playable):
            case (winner, _) if winner:
                # Winner message
                label = self.font_Game.render(f'Player "{winner}" wins!', True, 'white', 'black')
                sub_label = self.font_Game.render('Press R to Restart', True, 'white', 'black')

            case (None, False):
                # Tie message
                label = self.font_Game.render('Tie!', True, 'white', 'black')
                sub_label = self.font_Game.render('Press R to Restart', True, 'white', 'black')

            case _ if self.status_message and (now - self.status_time < 2000):
                # Current player status (temporary)
                label = self.font_Game.render(self.status_message, True, 'white', 'black')

        if label:
            # Center main label
            label_x = WIN_SIZE // 2 - label.get_width() // 2
            label_y = WIN_SIZE // 20
            surface.blit(label, (label_x, label_y))

            if sub_label:
                # Center sub label just below
                sub_x = WIN_SIZE // 2 - sub_label.get_width() // 2
                sub_y = label_y + label.get_height() + 10
                surface.blit(sub_label, (sub_x, sub_y))

    def inGameMenu(self, surface):
        surface.fill((52, 78, 91))
        label = self.font_Game.render("Paused", True, 'white')
        sub_label = self.font_Game.render("Press ESC to Resume", True, 'white')
        surface.blit(sub_label, (WIN_SIZE // 5.5 - label.get_width() // 2, WIN_SIZE // 3))
        surface.blit(label, (WIN_SIZE // 2 - label.get_width() // 2, WIN_SIZE // 5))

        for button in self.buttons:
            button.draw(surface)
            
    def handle_menu_event(self, event):
        for button in self.buttons:
            button.handle_event(event)
    def audio_button(self):
        print("Audio button clicked!")

    def option_button(self):
        print("Option button clicked!")
    def quit_button(self):
        pygame.quit()
        sys.exit()

    def update_status_message(self):
        current_player = "X" if self.turn_x else "O"
        self.status_message = f'Player "{current_player}" turn'
        self.status_time = pygame.time.get_ticks()

    def reset(self):
        self.__init__()

def main():
    clock = pygame.time.Clock()
    game = TicTacToeGame()
    game.update_status_message() 
    
    while True:
        for event in pygame.event.get():
            match(event.type):
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                case pygame.MOUSEBUTTONDOWN:
                    if game.game_paused:
                        game.handle_menu_event(event)
                    else:
                        game.handle_click(event.pos)
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_r:
                            game.reset()
                        case pygame.K_ESCAPE:
                            game.game_paused = not game.game_paused

        game.draw(screen)
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()