from map import Map
from time import time
from hud import Hud
from pathfinding import AStar
from qol import seconds_to_time
from prices import Prices
from psuedo_random_number import PseudoRandomNumber
import screen
import pygame


def game(seed: str):
    prn = PseudoRandomNumber()
    prn.set_seed(seed)

    map = Map(prn)
    hud = Hud()

    path = None

    num_trucks = 0
    num_roads_available = 0
    time_left = 15
    money = 0

    money_per_click = 1
    money_per_truck = 50

    total_time = 0
    total_money = 0

    prices = Prices()

    build_mode = False

    dragging = 0
    clicked = 0
    clicked_type = 0
    run = 1
    prev = time() - 0.001
    while run:
        if time_left <= 0:
            run = 0

        now = time()
        dt = now - prev
        prev = now

        time_left -= dt
        total_time += dt

        button_statuses = [False, False, False, False]

        mb1 = 0

        for e in pygame.event.get():
            if e.type == pygame.MOUSEWHEEL:
                map.change_scale(e.y)

            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    button_statuses = hud.update_buttons(True)

                    if pygame.mouse.get_pos()[0] < screen.WIN.get_width() - hud.size_x:
                        mb1 = 1
                        clicked = 1
                        if clicked_type == 0:
                            clicked_type = 1

                if e.button == 2:
                    if pygame.mouse.get_pos()[0] < screen.WIN.get_width() - hud.size_x:
                        dragging = 1
                        prev_pos = pygame.mouse.get_pos()

                if e.button == 3:
                    if pygame.mouse.get_pos()[0] < screen.WIN.get_width() - hud.size_x:
                        clicked = 1
                        if clicked_type == 0:
                            clicked_type = 2

            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    hud.update_buttons(False)
                    clicked = 0
                    clicked_type = 0

                if e.button == 2:
                    dragging = 0

                if e.button == 3:
                    clicked = 0
                    clicked_type = 0

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    run = 0

                if e.key == pygame.K_b:
                    build_mode = not build_mode

                if e.key == pygame.K_r:
                    if map.hover_tile_pos is not None:
                        tile = map.tile_grid[map.hover_tile_pos[1]][map.hover_tile_pos[0]]
                        tile.tile_rotation += 1
                        tile.tile_rotation %= 4

                if e.key == pygame.K_t:
                    if map.hover_tile_pos is not None:
                        tile = map.tile_grid[map.hover_tile_pos[1]][map.hover_tile_pos[0]]
                        tile.tile_type += 1
                        tile.tile_rotation = 0
                        tile.tile_type %= len(map.images[tile.tile_set])

                if e.key == pygame.K_y:
                    if map.hover_tile_pos is not None:
                        tile = map.tile_grid[map.hover_tile_pos[1]][map.hover_tile_pos[0]]
                        tile.tile_set += 1
                        tile.tile_type = 0
                        tile.tile_rotation = 0
                        tile.tile_set %= len(map.images)

        if dragging:
            current_pos = pygame.mouse.get_pos()
            map.change_offset(current_pos[0] - prev_pos[0], current_pos[1] - prev_pos[1])
            prev_pos = current_pos

        if clicked:
            if build_mode and (num_roads_available > 0 or clicked_type == 2):
                if map.on_click(bool(clicked_type-1)):
                    num_roads_available += clicked_type * 2 - 3

        if not build_mode and mb1 and map.check_factory_clicked():
            money += money_per_click
            total_money += money_per_click

        pygame.event.clear()

        trucks_completed = map.update(dt)
        money += trucks_completed * money_per_truck
        total_money += trucks_completed * money_per_truck

        frame_prices = prices.get_prices()
        for button, price in zip(hud.buttons, frame_prices):
            if money >= price:
                button.deactivated = False
            else:
                button.deactivated = True

        if button_statuses[0]:
            money -= frame_prices[0]
            num_roads_available += 1
            prices.roads_bought += 1
        if button_statuses[1]:
            money -= frame_prices[1]
            num_trucks += 1
            map.add_car()
            prices.vehicles_bought += 1
        if button_statuses[2]:
            money -= frame_prices[2]
            time_left += 10
            prices.time_bought += 1
        if button_statuses[3]:
            money -= frame_prices[3]
            map.expand_grid()
            prices.land_bought += 1

        screen.WIN.fill((52, 52, 52))

        map.draw(build_mode, path)
        hud.draw(seconds_to_time(int(time_left)), str(money), str(num_roads_available), str(num_trucks),
                 frame_prices, time_left)

        pygame.display.flip()

    return total_time, total_money