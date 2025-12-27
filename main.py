from window import Window
import pygame
import win32api  # type: ignore
import win32con  # type: ignore
import win32gui  # type: ignore

FUSCHIA = (255, 0, 128)


class TransparentWindow(Window):
    def __init__(self, width: int, height: int, fps: int = 60):
        self.width, self.height = self.size = width + 2, height + 29
        self.fps = 60

        self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
        self.clock = pygame.time.Clock()
        self.dt = 0

        # https://stackoverflow.com/questions/550001/fully-transparent-windows-in-pygame

        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED,
        )

        win32gui.SetLayeredWindowAttributes(
            hwnd, win32api.RGB(*FUSCHIA), 0, win32con.LWA_COLORKEY
        )

        self.fake_width, self.fake_height = self.fake_size = width, height
        self.fake_fps = fps
        self.fake_screen = pygame.Surface(self.fake_size)
        self.fake_clock = pygame.time.Clock()
        self.fake_dt = 0

        self.fake_image = pygame.image.load("./brongledingle.png")

    def draw_loop(self):
        self.screen.fill(FUSCHIA)
        pygame.draw.rect(self.screen, (200, 200, 200), (0, 0, self.width, 28))
        pygame.draw.rect(
            self.screen, (200, 200, 200), (0, 0, self.width, self.height), 1
        )

        self.fake_screen.blit(self.fake_image, (0, 0))
        self.screen.blit(self.fake_screen, (1, 28))


def main():
    app = TransparentWindow(400, 400, 60)
    app.run()


if __name__ == "__main__":
    main()
