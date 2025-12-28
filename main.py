import pygame
from pygame._sdl2.video import Window as W
from pygame.event import Event
import win32api  # type: ignore
import win32con  # type: ignore
import win32gui  # type: ignore
import pyautogui

from utils import add, sub, div, in_rect, rotate

FUSCHIA = (255, 0, 128)
TITLEBAR_H = 28


def rotate_img(
    image: pygame.Surface, center: tuple[int, int], angle: int
) -> tuple[pygame.Surface, pygame.Rect]:
    new_image = pygame.transform.rotate(image, angle)
    rect = new_image.get_rect(center=center)
    return new_image, rect


class Transform:
    def __init__(self):
        self.position: tuple[int, int] = div((1920, 1080), 2)
        self.angle: int = 20

    def local_to_world(self, local_pos: tuple[int, int]) -> tuple[int, int]:
        return add(rotate(local_pos, self.angle), self.position)

    def world_to_local(self, world_pos: tuple[int, int]) -> tuple[int, int]:
        return rotate(sub(world_pos, self.position), -self.angle)


class SubWindow:
    def __init__(self, width: int, height: int):
        self.real_width, self.real_height = self.real_size = (
            width + 2,
            height + TITLEBAR_H + 1,
        )
        self.real_screen = pygame.Surface(self.real_size)

        self.width, self.height = self.size = width, height
        self.screen = pygame.Surface(self.size)

        self.transform = Transform()
        self.being_held = False

        self.image = pygame.image.load("./dankpods.png")

    def draw_loop(self):
        self.screen.blit(self.image, (0, 0))

    def draw(self):
        self.real_screen.fill(FUSCHIA)
        self.screen.fill(FUSCHIA)

        pygame.draw.rect(
            self.real_screen, "white", (0, 0, self.real_width, TITLEBAR_H), 0, -1, 5, 5
        )
        pygame.draw.rect(
            self.real_screen,
            "white",
            (0, 0, self.real_width, self.real_height),
            1,
            -1,
            5,
            5,
        )

        self.draw_loop()

        self.real_screen.blit(self.screen, (1, TITLEBAR_H))


class MainWindow:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            (1920, 1080), pygame.NOFRAME | pygame.DOUBLEBUF
        )
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.fps = 60

        self.make_transparent()

        self.sub_windows: list[SubWindow] = []

        self.mouse_pos = tuple(pyautogui.position())

    def add_window(self, window: SubWindow):
        self.sub_windows.append(window)

    def make_transparent(self):
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED,
        )

        win32gui.SetLayeredWindowAttributes(
            hwnd, win32api.RGB(*FUSCHIA), 0, win32con.LWA_COLORKEY
        )

    def process_event(self, event: Event):
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for window in self.sub_windows:
                topleft = window.transform.local_to_world(
                    (-window.real_width // 2, -window.real_height // 2)
                )

                if in_rect(
                    event.pos, topleft[0], topleft[1], window.real_width, TITLEBAR_H
                ):
                    window.being_held = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for window in self.sub_windows:
                window.being_held = False

    def handle_movement(self, window: SubWindow, rel_movement: tuple[int, int]):
        if not window.being_held:
            return

        window.transform.position = add(window.transform.position, rel_movement)

    def run(self):
        while True:
            for event in pygame.event.get():
                self.process_event(event)

            self.screen.fill(FUSCHIA)

            mouse_pos = tuple(pyautogui.position())
            rel_movement = sub(mouse_pos, self.mouse_pos)

            for window in self.sub_windows:
                self.handle_movement(window, rel_movement)

                window.draw()

                rotated = pygame.transform.rotate(
                    window.real_screen, -window.transform.angle
                )
                rect = rotated.get_rect(center=window.transform.position)

                self.screen.blit(rotated, rect)

            pygame.display.flip()
            self.dt = self.clock.tick(self.fps) / 1000

            self.mouse_pos = mouse_pos


def main():
    app = MainWindow()
    app.add_window(SubWindow(400, 400))
    app.run()


if __name__ == "__main__":
    main()
