import pygame
from pygame.event import Event


class Window:
    def __init__(self, width: int, height: int, fps: int = 60):
        self.width, self.height = self.size = width, height
        self.fps = fps

        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.dt = 0

    def process_event(self, event: Event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    def draw_loop(self):
        self.screen.fill((50, 50, 50))

    def run(self):
        while True:
            for event in pygame.event.get():
                self.process_event(event)

            self.draw_loop()

            pygame.display.flip()
            self.dt = self.clock.tick(self.fps) / 1000
