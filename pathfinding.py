from dataclasses import dataclass


@dataclass
class Node:
    x: int
    y: int

    g_cost: int
    h_cost: int
    f_cost: int

    parent: "Node" = None


class AStar:
    @staticmethod
    def find_path(grid: list, start_pos: list, end_pos: list, prn, old_path=None) -> list:
        end_x, end_y = end_pos

        deactivated_nodes = []
        if old_path is not None and len(old_path) > 2:
            for node in old_path:
                if prn.generate() % 20 == 0:
                    deactivated_nodes.append(node)

        def generate_g_cost(parent: Node = None) -> int:
            dist = 0
            while parent is not None:
                dist += 10 + prn.generate() % 5
                parent = parent.parent

            return dist

        def generate_h_cost(x1, y1, x2, y2) -> int:
            dx2 = (x2 - x1) ** 2
            dy2 = (y2 - y1) ** 2

            dist = (dx2 + dy2) ** 0.5

            return int(dist * 10)

        def generate_node(start_pos: list, parent: Node = None) -> Node:
            x, y = start_pos

            g_cost = generate_g_cost(parent)
            h_cost = generate_h_cost(x, y, end_x, end_y)
            f_cost = g_cost + h_cost
            temp_node = Node(x=x, y=y, g_cost=g_cost, h_cost=h_cost, f_cost=f_cost, parent=parent)
            return temp_node

        def can_travel_check(pos1: list, pos2: list) -> bool:
            if pos2 in grid[pos1[1]][pos1[0]].tile_connections and (grid[pos2[1]][pos2[0]].tile_set != 2 or pos2 == end_pos):
                return 1
            return 0

        neighbours = [
            [0, -1],
            [1, 0],
            [0, 1],
            [-1, 0]
        ]

        nodes = [[Node for _ in range(len(grid[0]))] for _ in range(len(grid))]
        to_check_list = [start_pos]
        checked_list = []
        nodes[start_pos[1]][start_pos[0]] = generate_node(start_pos)

        path_found = 0
        while not path_found and len(to_check_list) > 0:
            to_check = to_check_list[0]
            for node in to_check_list:
                if nodes[node[1]][node[0]].f_cost < nodes[to_check[1]][to_check[0]].f_cost:
                    to_check = node

            to_check_list.remove(to_check)
            checked_list.append(to_check)

            # check if current node is the end node
            if to_check[0] == end_pos[0] and to_check[1] == end_pos[1]:
                path_found = 1

            else:
                # check the neighbours
                for dx, dy in neighbours:
                    n_x, n_y = to_check[0] + dx, to_check[1] + dy
                    n_pos = [n_x, n_y]

                    # check if node is accessible and not checked already
                    if n_pos not in checked_list and can_travel_check(to_check, n_pos):

                        new_node = generate_node([n_x, n_y], nodes[to_check[1]][to_check[0]])
                        if n_pos not in to_check_list or new_node.f_cost < nodes[n_y][n_x].f_cost:
                            nodes[n_y][n_x] = new_node
                            if n_pos not in to_check_list:
                                to_check_list.append(n_pos)

        path = []
        if path_found:
            path.insert(0, to_check)
            while nodes[to_check[1]][to_check[0]].parent is not None:
                p = nodes[to_check[1]][to_check[0]].parent
                to_check = [p.x, p.y]
                path.insert(0, to_check)
        return path

    @staticmethod
    def generate_paths(grid: dict, start_pos: tuple, end_pos: tuple, prn, num_paths: int = 1) -> list:
        paths = []
        old_paths = []
        for i in range(num_paths):
            path = AStar.find_path(grid, start_pos, end_pos, prn, old_paths)
            paths.append(path)
            old_paths += path

        return paths
