import string

from qol import clamp

class Car:
    def __init__(self, path, to_hub: bool = False, been_to_factory: bool = False):
        self.driven_percentage = 0.96

        self.to_hub = to_hub
        self.been_to_factory = been_to_factory

        self.acceleration = 0.3
        self.deceleration = 0
        self.speed = 0

        self.state = 1 #  0, 1 = stop, go

        self.path = path
        self.path_index = 0

        self.prev_direction = None
        self.direction = self.get_start_direction()

        self.relative_direction = self.direction
        self.relative_x, self.relative_y = 0, 0
        self.update_relative_position()

    def reset(self, path, to_hub: bool = False, been_to_factory: bool = False):
        self.driven_percentage = 0.96

        self.to_hub = to_hub
        self.been_to_factory = been_to_factory

        self.state = 1

        self.path = path
        self.path_index = 0

        self.direction = self.get_start_direction()

        self.relative_direction = self.direction
        self.update_relative_position()

    def get_start_direction(self):
        x1, y1 = self.path[0]
        x2, y2 = self.path[1]
        dx, dy = x2 - x1, y2 - y1

        return [[0, -1], [1, 0], [0, 1], [-1, 0]].index([dx, dy])

    def get_action(self, direction, step: int = 0):
        x1, y1 = self.path[self.path_index + step]
        x2, y2 = self.path[self.path_index + step + 1]
        dx, dy = x2 - x1, y2 - y1

        dx, dy = self.rotate_direction_vector(dx, dy, direction)

        return [[0, 1], [0, -1], [-1, 0], [1, 0]].index([dx, dy])

    def set_deceleration_amount(self):
        dist = 1 - self.driven_percentage
        deceleration = -(self.speed ** 2) / (2 * dist)
        self.deceleration = deceleration

    def update(self, dt, max_speed, acceleration):
        if self.state and self.speed < max_speed :
            self.speed += acceleration * dt
        elif not self.state and self.speed > 0 and self.driven_percentage > 0.5:
            self.speed += self.deceleration * dt

        self.speed = clamp(self.speed, 0, max_speed)
        self.driven_percentage += self.speed * dt

        if self.update_relative_position():
            self.prev_direction = self.direction * 1
            self.direction = self.get_next_direction()
            self.path_index += 1
            self.driven_percentage = 0

            self.relative_x, self.relative_y = self.rotate_relative_points(0.3 ,0, self.direction)

            if self.path_index >= len(self.path) - 1:
                return 2
            return 1

    def update_relative_position(self):
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

    def get_next_direction(self, step: int = 0):
        match self.get_action(self.direction, step):
            case 0:
                direction = self.direction + 2
            case 1:
                direction = self.direction
            case 2:
                direction = self.direction - 1
            case 3:
                direction = self.direction + 1

        direction %= 4

        return direction

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
            return True
