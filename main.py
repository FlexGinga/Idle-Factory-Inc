
if __name__ == '__main__':
    from map import Map
    from time import time
    from hud import Hud
    from pathfinding import AStar
    from qol import seconds_to_time
    from psuedo_random_number import PseudoRandomNumber
    import screen
    import pygame

    screen.init("Idle Factory Inc", "assets/icon.png")

    map = Map()
    hud = Hud()

    prn = PseudoRandomNumber()
    prn.set_seed("fdsf")
    FONT = pygame.font.SysFont('Comic Sans MS', 30)

    path = None

    num_trucks = 0
    num_roads_available = 0
    time_left = 0
    money = 0

    dragging = 0
    clicked = 0
    clicked_type = 0
    run = 1
    prev = time() - 0.001
    while run:
        now = time()
        dt = now - prev
        prev = now

        button_statuses = [False, False, False, False]

        for e in pygame.event.get():
            if e.type == pygame.MOUSEWHEEL:
                map.change_scale(e.y)

            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    button_statuses = hud.update_buttons(True)
                    clicked = 1
                    if clicked_type == 0:
                        clicked_type = 1

                if e.button == 2:
                    dragging = 1
                    prev_pos = pygame.mouse.get_pos()

                if e.button == 3:
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
                    for b in hud.buttons:
                        b.set_activation(b.deactivated)
                    clicked = 0
                    clicked_type = 0

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    run = 0

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

                if e.key == pygame.K_SPACE:
                    path = AStar.find_path(map.tile_grid, [0, 0], map.hover_tile_pos, prn)
                    print(path)

        if dragging:
            current_pos = pygame.mouse.get_pos()
            map.change_offset(current_pos[0] - prev_pos[0], current_pos[1] - prev_pos[1])
            prev_pos = current_pos

        if clicked:
            map.on_click(bool(clicked_type-1))

        pygame.event.clear()

        map.update()

        if button_statuses[0]:
            num_roads_available += 1
        if button_statuses[1]:
            num_trucks += 1
        if button_statuses[2]:
            time_left += 10
        if button_statuses[3]:
            map.expand_grid()

        screen.WIN.fill((52, 52, 52))

        map.draw(path)
        hud.draw(seconds_to_time(time_left), str(money), str(num_roads_available), str(num_trucks))

        # draw_text(WIN, FONT, f"FPS:: {int(1 / dt)}", 10, 40)

        pygame.display.flip()

    pygame.quit()
