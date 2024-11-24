import pygame
import sys
import os

class TilemapEditor:
    def __init__(self, width, height, tile_size, filename='map'):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.filename = filename
        self.map = []
        self.tile_types = {'1': (255, 255, 255), '0': (0, 0, 0), 'P': (0, 255, 0), 'C': (255, 255, 0), 'E': (255, 0, 0)}
        if os.path.exists(f'{self.filename}.ber'):
            self.load_from_file()
        else:
            self.create_empty_map()
        self.player_position = None
        self.exit_position = None
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.tile_size, self.height * self.tile_size + 50))  # Adjust height for legend
        pygame.display.set_caption('Tilemap Editor')
        self.font = pygame.font.SysFont(None, 24)
        self.current_tile = '1'  # Track current selected tile

    def draw_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                rect = (x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, self.tile_types[self.map[y][x]], rect)
                text = self.font.render(self.map[y][x], True, (0, 0, 0))
                self.screen.blit(text, (x * self.tile_size + 5, y * self.tile_size + 5))

    def draw_legend(self):
        legend_y = self.height * self.tile_size  # Start drawing legend below the map
        self.screen.fill((200, 200, 200), (0, legend_y, self.width * self.tile_size, 50))
        tile_labels = ['1', '0', 'P', 'C', 'E']
        for i, label in enumerate(tile_labels):
            color_rect = pygame.Surface((20, 20))
            color_rect.fill(self.tile_types[label])
            text = self.font.render(label, True, (0, 0, 0))
            color_rect.blit(text, (2, 2))  # Draw text inside the color rectangle
            self.screen.blit(color_rect, (i * 100 + 50, legend_y + 5))
        selected_color_rect = pygame.Surface((20, 20))
        selected_color_rect.fill(self.tile_types[self.current_tile])
        self.screen.blit(selected_color_rect, (10, legend_y + 30))
        selected_text = self.font.render('Selected:', True, (0, 0, 0))
        self.screen.blit(selected_text, (40, legend_y + 30))

    def place_tile(self, x, y, tile):
        if 0 <= x < self.width and 0 <= y < self.height:
            # if self.map[y][x] == '1' and (x == 0 or x == self.width-1 or y == 0 or y == self.height-1):
            #     return  # Do not modify border walls
            if tile == 'E':
                if self.exit_position is not None:
                    ex, ey = self.exit_position
                    self.map[ey][ex] = '0'
                self.exit_position = (x, y)
            elif tile == 'P':
                if self.player_position is not None:
                    px, py = self.player_position
                    self.map[py][px] = '0'
                self.player_position = (x, y)
            self.map[y][x] = tile

    def save_to_file(self):
        with open(f'{self.filename}.ber', 'w') as f:
            for row in self.map:
                f.write(''.join(row) + '\n')

    def load_from_file(self):
        with open(f'{self.filename}.ber', 'r') as f:
            self.map = [list(line.strip()) for line in f.readlines()]   
        self.height = len(self.map)
        self.width = len(self.map[0]) if self.height > 0 else 0
        # Update player and exit positions
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x] == 'P':
                    self.player_position = (x, y)
                elif self.map[y][x] == 'E':
                    self.exit_position = (x, y)

    def create_empty_map(self):
        self.map = [['1' if x == 0 or x == self.width-1 or y == 0 or y == self.height-1 else '0' for x in range(self.width)] for y in range(self.height)]

    def run(self):
        running = True
        mouse_pressed = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pressed = True
                    x, y = pygame.mouse.get_pos()
                    if event.button == 1:  # Left click
                        self.place_tile(x // self.tile_size, y // self.tile_size, self.current_tile)
                    elif event.button == 3:  # Right click
                        self.place_tile(x // self.tile_size, y // self.tile_size, '0')
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_pressed = False
                elif event.type == pygame.MOUSEMOTION and mouse_pressed:
                    x, y = pygame.mouse.get_pos()
                    if pygame.mouse.get_pressed()[0]:  # Left button held down
                        self.place_tile(x // self.tile_size, y // self.tile_size, self.current_tile)
                    elif pygame.mouse.get_pressed()[2]:  # Right button held down
                        self.place_tile(x // self.tile_size, y // self.tile_size, '0')
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.current_tile = '1'
                    elif event.key == pygame.K_0:
                        self.current_tile = '0'
                    elif event.key == pygame.K_p:
                        self.current_tile = 'P'
                    elif event.key == pygame.K_c:
                        self.current_tile = 'C'
                    elif event.key == pygame.K_e:
                        self.current_tile = 'E'
                    elif event.key == pygame.K_s:
                        self.save_to_file()
            self.screen.fill((0, 0, 0))
            self.draw_grid()
            self.draw_legend()  # Draw the legend
            pygame.display.flip()
        pygame.quit()

def main():
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if os.path.exists(f'{filename}.ber'):
            editor = TilemapEditor(0, 0, 32, filename)
            editor.run()
        else:
            print(f"Error: File {filename}.ber not found.")
            sys.exit(1)
    elif len(sys.argv) == 3:
        try:
            width, height = int(sys.argv[1]), int(sys.argv[2])
            if width < 3 or height < 3:
                raise ValueError
            filename = 'map'
            editor = TilemapEditor(width, height, 32, filename)
            editor.create_empty_map()  # Crear un mapa vacío con el perímetro rellenado
            editor.save_to_file()  # Guardar el archivo de inmediato
            editor.run()
        except ValueError:
            print("Error: Width and height must be integers greater than or equal to 3.")
            sys.exit(1)
    elif len(sys.argv) == 4:
        try:
            width, height = int(sys.argv[1]), int(sys.argv[2])
            if width < 3 or height < 3:
                raise ValueError
            filename = sys.argv[3]
            editor = TilemapEditor(width, height, 32, filename)
            editor.create_empty_map()  # Crear un mapa vacío con el perímetro rellenado
            editor.save_to_file()  # Guardar el archivo de inmediato
            editor.run()
        except ValueError:
            print("Error: Width, height, and filename must be valid, and sizes must be greater than or equal to 3.")
            sys.exit(1)
    else:
        print("Usage: python script.py [width] [height] <filename>")

if __name__ == '__main__':
    main()
