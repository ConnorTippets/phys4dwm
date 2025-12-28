import pygame
from pygame._sdl2.video import Window as W
from pygame.event import Event
import win32api  # type: ignore
import win32con  # type: ignore
import win32gui  # type: ignore
import pyautogui

pygame.font.init()

from utils import (
    add,
    sub,
    div,
    mul,
    in_rect,
    rotate,
    ray_aab_intersection,
    unit,
    length_sqr,
    calc_angular_torque,
    fvti,
    length,
    calc_impulse,
    cross,
)

FUSCHIA = (255, 0, 128)
TITLEBAR_H = 31
FONT = pygame.font.SysFont("Segoe UI Semilight", 13)


def rotate_img(
    image: pygame.Surface, center: tuple[int, int], angle: int
) -> tuple[pygame.Surface, pygame.Rect]:
    new_image = pygame.transform.rotate(image, angle)
    rect = new_image.get_rect(center=center)
    return new_image, rect


class Transform:
    def __init__(self):
        self.position: tuple[float, float] = div((1920, 1080), 2)
        self.velocity: tuple[float, float] = (0, 0)
        self.angle: float = 0
        self.angular_velocity: float = 0

    def local_to_world(self, local_pos: tuple[int, int]) -> tuple[int, int]:
        return add(rotate(local_pos, self.angle), self.position)

    def world_to_local(self, world_pos: tuple[int, int]) -> tuple[int, int]:
        return rotate(sub(world_pos, self.position), -self.angle)


class SubWindow:
    def __init__(self, width: int, height: int, title: str = "File Explorer"):
        self.real_width, self.real_height = self.real_size = (
            width + 2,
            height + TITLEBAR_H + 1,
        )
        self.real_screen = pygame.Surface(self.real_size, pygame.SRCALPHA)

        self.width, self.height = self.size = width, height
        self.screen = pygame.Surface(self.size)

        self.title = title

        self.transform = Transform()
        self.being_held = False

        self.mass: int = 20
        self.moment_of_inertia: float = (self.mass * length_sqr(self.real_size)) / 12

        self.image = [pygame.image.load(f"./gilled{i}.png") for i in range(1, 8)]
        self.im_index = 0

    def get_local_corners(
        self, titlebar: bool = False
    ) -> tuple[tuple, tuple, tuple, tuple]:
        topleft = (-self.real_width // 2, -self.real_height // 2)
        topright = (self.real_width // 2, -self.real_height // 2)
        bottomright = (
            (self.real_width // 2, -self.real_height // 2 + TITLEBAR_H)
            if titlebar
            else (self.real_width // 2, self.real_height // 2)
        )
        bottomleft = (
            (-self.real_width // 2, -self.real_height // 2 + TITLEBAR_H)
            if titlebar
            else (-self.real_width // 2, self.real_height // 2)
        )

        return topleft, topright, bottomright, bottomleft

    def process_event(self, event: Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            self.im_index = (self.im_index + 1) % 7

    def get_world_corners(
        self, titlebar: bool = False
    ) -> tuple[tuple, tuple, tuple, tuple]:
        topleft, topright, bottomright, bottomleft = list(
            map(self.transform.local_to_world, self.get_local_corners(titlebar))
        )

        return topleft, topright, bottomright, bottomleft

    def draw_loop(self):
        self.screen.blit(self.image[self.im_index], (0, 0))

    def draw(self):
        self.real_screen.fill(FUSCHIA)
        self.screen.fill(FUSCHIA)

        pygame.draw.rect(
            self.real_screen, "black", (0, 0, self.real_width, TITLEBAR_H), 0
        )
        pygame.draw.rect(
            self.real_screen,
            (46, 46, 46),
            (0, 0, self.real_width, self.real_height),
            1,
        )

        title = FONT.render(self.title, True, "white")

        self.real_screen.blit(title, (8, 5))

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
                topleft, topright, bottomright, bottomleft = window.get_world_corners(
                    True
                )

                if in_rect(event.pos, topleft, topright, bottomright, bottomleft):
                    window.being_held = True
                else:
                    hit_point = ray_aab_intersection(
                        window.transform.world_to_local((1920 // 3 * 2, 1080 // 2)),
                        rotate(
                            unit(sub(event.pos, (1920 // 3 * 2, 1080 // 2))),
                            -window.transform.angle,
                        ),
                        window.get_local_corners()[0],
                        window.real_size,
                    )

                    if not hit_point:
                        continue

                    dir = rotate(
                        unit(sub(event.pos, (1920 // 3 * 2, 1080 // 2))),
                        -window.transform.angle,
                    )

                    # I = F*dT = M*A*dT
                    impulse_vec = mul(dir, window.mass * 250 * 4)
                    angular_torque = calc_angular_torque(hit_point, dir, impulse_vec)
                    window.transform.angular_velocity += (
                        angular_torque / window.moment_of_inertia
                    )
                    window.transform.velocity = add(
                        window.transform.velocity, div(impulse_vec, window.mass)
                    )
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for window in self.sub_windows:
                window.being_held = False

        for window in self.sub_windows:
            window.process_event(event)

    def handle_movement(self, window: SubWindow, rel_movement: tuple[int, int]):
        # if window.transform.position[0] < 0:
        #     window.transform.velocity = (
        #         -window.transform.velocity[0],
        #         window.transform.velocity[1],
        #     )
        #     window.transform.position = (20, window.transform.position[1])
        # if window.transform.position[0] > 1920:
        #     window.transform.velocity = (
        #         -window.transform.velocity[0],
        #         window.transform.velocity[1],
        #     )
        #     window.transform.position = (1900, window.transform.position[1])
        # if window.transform.position[1] < 0:
        #     window.transform.velocity = (
        #         window.transform.velocity[0],
        #         -window.transform.velocity[1],
        #     )
        #     window.transform.position = (window.transform.position[1], 20)
        # if window.transform.position[1] > 1080:
        #     window.transform.velocity = (
        #         window.transform.velocity[0],
        #         -window.transform.velocity[1],
        #     )
        #     window.transform.position = (window.transform.position[1], 1060)

        # if (
        #     not length(sub(window.transform.position, (1920 // 2, 1080 // 2)))
        #     == 1920 // 6
        # ):
        #     desired_position = add(
        #         (1920 // 2, 1080 // 2),
        #         mul(
        #             unit(sub(window.transform.position, (1920 // 2, 1080 // 2))),
        #             1920 // 6,
        #         ),
        #     )
        #
        #     window.transform.velocity = add(
        #         window.transform.velocity,
        #         mul(sub(desired_position, window.transform.position), 0.1),
        #     )

        if not window.being_held:
            window.transform.velocity = add(window.transform.velocity, (0, 20))
            window.transform.velocity = mul(window.transform.velocity, 0.99)
            window.transform.angular_velocity *= 0.99

            window.transform.angle += window.transform.angular_velocity * self.dt

            window.transform.position = add(
                window.transform.position,
                mul(window.transform.velocity, self.dt),
            )

            for corner in window.get_world_corners():
                if corner[1] > 1080:
                    hit_vector = sub(corner, window.transform.position)
                    impulse = calc_impulse(
                        window.transform.velocity,
                        0.65,
                        (0, -1),
                        window.mass,
                        window.moment_of_inertia,
                        hit_vector,
                    )

                    window.transform.angular_velocity += (
                        cross(hit_vector, mul((0, -1), impulse))
                        / window.moment_of_inertia
                    )

                    window.transform.velocity = add(
                        window.transform.velocity,
                        div(mul((0, -1), impulse), window.mass),
                    )

            penetration_depth = max(
                corner[1] - 1080 for corner in window.get_world_corners()
            )

            if penetration_depth > 0.01:
                correction = (penetration_depth - 0.01) * 0.2
                window.transform.position = add(
                    window.transform.position, mul((0, -1), correction)
                )

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
                rect = rotated.get_rect(center=fvti(window.transform.position))

                self.screen.blit(rotated, rect)

                intersect = ray_aab_intersection(
                    window.transform.world_to_local((1920 // 3 * 2, 1080 // 2)),
                    rotate(
                        unit(sub(mouse_pos, (1920 // 3 * 2, 1080 // 2))),
                        -window.transform.angle,
                    ),
                    window.get_local_corners()[0],
                    window.real_size,
                )

                pygame.draw.circle(self.screen, "red", (1920 // 3 * 2, 1080 // 2), 10)

                if not intersect is False:
                    pygame.draw.circle(
                        self.screen,
                        "red",
                        window.transform.local_to_world(intersect),
                        10,
                    )

            pygame.display.flip()
            self.dt = self.clock.tick(self.fps) / 1000

            self.mouse_pos = mouse_pos


def main():
    app = MainWindow()
    app.add_window(SubWindow(150, 150))
    # app.add_window(SubWindow(400, 400))
    app.sub_windows[0].transform.position = (1920 // 3, 1080 // 2)
    # app.sub_windows[1].transform.position = (1920 // 3 * 2, 1080 // 2)
    app.run()


if __name__ == "__main__":
    main()
