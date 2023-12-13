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
    def find_path(grid: dict, start_pos: tuple, end_pos: tuple, prn, old_path=None) -> list:
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

        def can_travel_check(x1: int, y1: int, x2: int, y2: int) -> bool:
            if [x2, y2] in grid[y1][x1].tile_connections:
                return 1
            return 0

        neighbours = [
            [0, -1],
            [1, 0],
            [0, 1],
            [-1, 0]
        ]

        nodes = [[None for _ in range(len(grid[0]))] for _ in range(len(grid))]
        to_check_list = [start_pos]
        checked_list = []
        nodes[start_pos] = generate_node(start_pos)

        path_found = 0
        while not path_found and len(to_check_list) > 0:
            to_check = to_check_list[0]
            for node in to_check_list:
                if nodes[node].f_cost < nodes[to_check].f_cost:
                    to_check = node

            to_check_list.remove(to_check)
            checked_list.append(to_check)

            # check if current node is the end node
            if to_check == f"{end_x}_{end_y}":
                path_found = 1

            else:
                # check the neighbours
                for dx, dy in neighbours:
                    x, y = to_check.split("_")
                    x, y = int(x), int(y)
                    n_x, n_y = x + dx, y + dy
                    n_node = f"{n_x}_{n_y}"

                    # check if node is accessible and not checked already
                    if n_node not in checked_list and can_travel_check(x, y, to_check, n_x, n_y, n_node):

                        new_node = generate_node(n_x, n_y, nodes[to_check])
                        if n_node not in to_check_list or new_node.f_cost < nodes[n_node].f_cost:
                            nodes[n_node] = new_node
                            if n_node not in to_check_list:
                                to_check_list.append(n_node)

        path = []
        if path_found:
            path.insert(0, to_check)
            while nodes[to_check].parent is not None:
                p = nodes[to_check].parent
                to_check = f"{p.x}_{p.y}"
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

