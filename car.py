

class Car:
    def __init__(self, path, to_hub: bool = False, been_to_factory: bool = False):
        self.driven_percentage = 0

        self.to_hub = to_hub
        self.been_to_factory = been_to_factory

        # self.acceleration = 4
        # self.deceleration = 5
        # self.max_speed = 4
        self.speed = 0.5

        self.path = path
        self.path_index = 1

        self.direction = self.get_start_direction()

        self.relative_direction = self.direction
        self.relative_x, self.relative_y = self.rotate_relative_points(0.3, 0, self.relative_direction)

    def reset(self, path, to_hub: bool = False, been_to_factory: bool = False):
        self.driven_percentage = 0

        self.to_hub = to_hub
        self.been_to_factory = been_to_factory

        self.path = path
        self.path_index = 1

        self.direction = self.get_start_direction()

        self.relative_direction = self.direction
        self.relative_x, self.relative_y = self.rotate_relative_points(0.3, 0, self.relative_direction)

    def get_start_direction(self):
        x1, y1 = self.path[0]
        x2, y2 = self.path[1]
        dx, dy = x2 - x1, y2 - y1

        return [[0, -1], [1, 0], [0, 1], [-1, 0]].index([dx, dy])

    def get_action(self, direction):
        x1, y1 = self.path[self.path_index]
        x2, y2 = self.path[self.path_index + 1]
        dx, dy = x2 - x1, y2 - y1

        dx, dy = self.rotate_direction_vector(dx, dy, direction)

        return [[0, 1], [0, -1], [-1, 0], [1, 0]].index([dx, dy])


    def update(self, dt):
        if self.update_relative_position(dt):
            self.path_index += 1
            self.driven_percentage = 0

            self.relative_x, self.relative_y = self.rotate_relative_points(0.3 ,0, self.direction)

            if self.path_index >= len(self.path) - 1:
                return True

    def update_relative_position(self, dt):
        self.driven_percentage += self.speed * dt

        match self.get_action(self.direction):
            case 0:
                action_complete = self.u_turn()
            case 1:
                action_complete = self.straight_on()
            case 2:
                action_complete = self.left_turn()
            case 3:
                action_complete = self.right_turn()

        return action_complete

    @staticmethod
    def rotate_relative_points(x: float, y: float, direction: int):
        for _ in range(direction):
            x, y = y, 1 - x

        return x, y

    @staticmethod
    def rotate_points(x: float, y: float, direction: int):
        for _ in range(direction):
            x, y = -y, x

        return x, y

    @staticmethod
    def rotate_direction_vector(x: float, y: float, direction: int):
        for _ in range(direction):
            x, y = y, -x

        return x, y

    # def next_pos(self, dx, dy):
    #     x, y = self.road_pos
    #     dx, dy = self.rotate_points(dx, dy, self.direction)
    #     self.road_pos = x + dx, y + dy

    def u_turn(self):
        if self.driven_percentage < 0.3:
            relative_x = 0.3
            relative_y = (7/3) * self.driven_percentage
            self.relative_x, self.relative_y = self.rotate_relative_points(relative_x, relative_y, self.direction)
            self.relative_direction = self.direction
        elif self.driven_percentage < 0.7:
            relative_x = 0.3 + (self.driven_percentage - 0.3)
            relative_y = 0.7
            self.relative_x, self.relative_y = self.rotate_relative_points(relative_x, relative_y, self.direction)
            self.relative_direction = (self.direction + 1) % 4
        elif self.driven_percentage < 1:
            relative_x = 0.7
            relative_y = 0.7 - (7/3) * (self.driven_percentage - 0.7)
            self.relative_x, self.relative_y = self.rotate_relative_points(relative_x, relative_y, self.direction)
            self.relative_direction = (self.direction + 2) % 4
        else:
            # self.next_pos(0, 1)

            self.direction += 2
            self.direction %= 4

            return True

    def straight_on(self):
        if self.driven_percentage < 1:
            relative_x = 0.3
            relative_y = self.driven_percentage
            self.relative_x, self.relative_y = self.rotate_relative_points(relative_x, relative_y, self.direction)
            self.relative_direction = self.direction
        else:
            # self.next_pos(0, -1)

            return True

    def left_turn(self):
        if self.driven_percentage < 0.5:
            relative_x = 0.3
            relative_y = (3/5) * self.driven_percentage
            self.relative_x, self.relative_y = self.rotate_relative_points(relative_x, relative_y, self.direction)
            self.relative_direction = self.direction
        elif self.driven_percentage < 1:
            relative_x = 0.3 - (3/5) * (self.driven_percentage - 0.5)
            relative_y = 0.3
            self.relative_x, self.relative_y = self.rotate_relative_points(relative_x, relative_y, self.direction)
            self.relative_direction = (self.direction - 1) % 4
        else:
            # self.next_pos(-1, 0)

            self.direction -= 1
            self.direction %= 4

            return True

    def right_turn(self):
        if self.driven_percentage < 0.5:
            relative_x = 0.3
            relative_y = (7/5) * self.driven_percentage
            self.relative_x, self.relative_y = self.rotate_relative_points(relative_x, relative_y, self.direction)
            self.relative_direction = self.direction
        elif self.driven_percentage < 1:
            relative_x = 0.3 + (7/5) * (self.driven_percentage - 0.5)
            relative_y = 0.7
            self.relative_x, self.relative_y = self.rotate_relative_points(relative_x, relative_y, self.direction)
            self.relative_direction = (self.direction + 1) % 4
        else:
            # self.next_pos(1, 0)

            self.direction += 1
            self.direction %= 4

            return True
