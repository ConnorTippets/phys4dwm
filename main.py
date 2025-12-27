from window import Window
import pygame
import win32api  # type: ignore
import win32con  # type: ignore
import win32gui  # type: ignore

FUSCHIA = (255, 0, 128)


class TransparentWindow(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def draw_loop(self):
        self.screen.fill(FUSCHIA)


def main():
    app = TransparentWindow(400, 400, 60)
    app.run()


if __name__ == "__main__":
    print(main())
