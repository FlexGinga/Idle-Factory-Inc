from map import Map
from time import time
from hud import Hud
from pathfinding import AStar
from qol import seconds_to_time
from prices import Prices
from psuedo_random_number import PseudoRandomNumber
from upgrade import Upgrade
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
    time_left = 60
    money = 2000

    money_per_click = 1
    money_per_truck = 50
    car_speed = 0.6
    car_acceleration = 0.3

    total_time = 0
    total_money = 0

    prices = Prices()

    upgrade_titles = [
        ["Turbocharged Clicks", "Precision Profits", "Gold Rush Clicker", "Click Mastery", "Platinum Clicker"],
        ["Cargo Expansion Module", "MaxLoad Capacity Upgrade", "Freight Fortress Enhancement", "MegaHaul Storage Expansion", "Payload Powerhouse Kit"],
        ["Velocity Boost Package", "Swift Acceleration Upgrade", "High-Speed Overhaul", "Turbocharged Hauler Kit", "Rapid Transport Enhancement"]
    ]

    upgrade_descriptions = ["Income from mouse click is doubled.", "Income from trucks increases by 50%.", "Trucks receive an upgraded engine."]

    upgrades = [
        Upgrade(title="Precision Profits",price=prices.get_upgrade_0_price(),desc=upgrade_descriptions[0],func=0),
        Upgrade(title="Increase Truck Storage", price=prices.get_upgrade_1_price(), desc=upgrade_descriptions[1],func=1),
        Upgrade(title="Engine Swap", price=prices.get_upgrade_2_price(), desc=upgrade_descriptions[2],func=2),
    ]

    build_mode = False

    reset_timer = 0
    reset_timer_start = False
    cooldown_timer = 0
    cooldown_timer_start = False

    dragging = 0
    clicked = 0
    clicked_type = 0
    run = 1
    prev = time() - 0.001
    while run:
        now = time()
        dt = now - prev
        prev = now

        time_left -= dt
        total_time += dt

        button_statuses = [False, False, False, False]

        mb1 = 0
        money_click = False
        hud_clicked = 0

        for e in pygame.event.get():
            if e.type == pygame.MOUSEWHEEL:
                if pygame.mouse.get_pos()[0] < screen.WIN.get_width() - hud.size_x:
                    map.change_scale(e.y)

            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    button_statuses = hud.update_buttons(True)
                    hud_clicked = 1

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

                if e.key in [pygame.K_z, pygame.K_x]:
                    money_click = True

                if e.key == pygame.K_SPACE:
                    reset_timer_start = True

                if e.key == pygame.K_c:
                    map.reset_offset()

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

            if e.type == pygame.KEYUP:
                if e.key == pygame.K_SPACE:
                    reset_timer_start = False

        if reset_timer_start:
            reset_timer += dt
            hud.add_message(f"Reset vehicles in {round(2-reset_timer, 1)}", 0.1, (255, 191, 0))
            if reset_timer >= 2:
                hud.add_message(f"Vehicles resetting", 5, (255, 191, 0))
                map.reset_cars()
                cooldown_timer_start = True
                reset_timer_start = False
        else:
            reset_timer = 0

        if cooldown_timer_start:
            cooldown_timer += dt
            if cooldown_timer >= 5:
                hud.add_message(f"Vehicles reset", 5, (255, 191, 0))
                cooldown_timer = 0
                cooldown_timer_start = False
        else:
            cooldown_timer = 0

        if dragging:
            current_pos = pygame.mouse.get_pos()
            map.change_offset(current_pos[0] - prev_pos[0], current_pos[1] - prev_pos[1])
            prev_pos = current_pos

        if clicked:
            if build_mode and (num_roads_available > 0 or clicked_type == 2):
                if map.on_click(bool(clicked_type-1)):
                    num_roads_available += clicked_type * 2 - 3

        if (not build_mode and mb1 and map.check_factory_clicked()) or money_click:
            map.add_effect((map.grid_size_x // 2, map.grid_size_y // 2), 0, 0.25)

            money += money_per_click
            total_money += money_per_click

        trucks_completed = map.update(dt, car_speed, car_acceleration, cooldown_timer_start)
        money += trucks_completed * money_per_truck
        total_money += trucks_completed * money_per_truck

        frame_prices = prices.get_prices()
        hud.update(dt, frame_prices, upgrades, money, hud_clicked)

        for upgrade in upgrades:
            if upgrade.pressed:
                if upgrade.activated:
                    money -= upgrade.price
                    prices.upgrades_bought[upgrade.func] += 1
                    upgrades.remove(upgrade)
                    match upgrade.func:
                        case 0:
                            money_per_click *= 2
                            hud.add_message("Cursor income doubled!", colour=(20, 255, 60))
                        case 1:
                            money_per_truck *= 1.5
                            hud.add_message("Truck income increased", colour=(20, 255, 60))
                        case 2:
                            car_speed += 0.05
                            car_acceleration += 0.1
                            hud.add_message("Truck speed has been increased", colour=(20, 255, 60))

                    level = prices.upgrades_bought[upgrade.func]
                    title = upgrade_titles[upgrade.func][level % 5]
                    if level >= 5:
                        title += f" V{level // 5}"
                    upgrades.append(Upgrade(title=title, price=prices.get_upgrade_prices()[upgrade.func],
                                            desc=upgrade_descriptions[upgrade.func], func=upgrade.func))

                else:
                    hud.add_message("Not enough money!")


        if button_statuses[0]:
            if not hud.buttons[0].deactivated:
                money -= frame_prices[0]
                num_roads_available += 1
                prices.roads_bought += 1
            else:
                hud.add_message("Not enough money!")
        if button_statuses[1]:
            if not hud.buttons[1].deactivated:
                if map.add_car():
                    money -= frame_prices[1]
                    num_trucks += 1
                    prices.vehicles_bought += 1
                else:
                    hud.add_message("No available factories for truck!")
            else:
                hud.add_message("Not enough money!")
        if button_statuses[2] or time_left <= 0:
            if not hud.buttons[2].deactivated:
                money -= frame_prices[2]
                time_left += 20
                prices.time_bought += 1
            else:
                hud.add_message("Not enough money!")
        if button_statuses[3]:
            if not hud.buttons[3].deactivated:
                money -= frame_prices[3]
                map.expand_grid()
                prices.land_bought += 1
            else:
                hud.add_message("Not enough money!")

        screen.WIN.fill((52, 52, 52))

        map.draw(build_mode, path)
        hud.draw(seconds_to_time(int(time_left)), money, str(num_roads_available), str(num_trucks),
                 frame_prices, time_left, upgrades)

        pygame.display.flip()

        if time_left <= 0:
            run = 0

    return total_time, total_money