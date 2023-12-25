

class Car:
    def __init__(self, road, road_pos, action, direction):
        self.driven_percentage = 0

        # self.acceleration = 4
        # self.deceleration = 5
        # self.max_speed = 4
        self.speed = 0.2

        self.road = road
        self.road_pos = road_pos
        self.action = action # U-turn, Straight on, Left turn, Right turn
        self.direction = direction

        self.relative_direction = 0
        self.relative_x = 0.5
        self.relative_y = 0.5

    def update_relative_position(self, dt):
        self.driven_percentage += self.speed * dt

        match self.action:
            case 0:
                self.u_turn()
            case 1:
                self.straight_on()
            case 2:
                self.left_turn()
            case 3:
                self.right_turn()

    @staticmethod
    def rotate_points(x: float, y: float, direction: int):
        for _ in range(direction):
            x = y
            y = 1 - x

        return x, y

    def u_turn(self):
        if self.driven_percentage < 0.3:
            relative_x = 0.3
            relative_y = (7/3) * self.driven_percentage
            self.relative_x, self.relative_y = self.rotate_points(relative_x, relative_y, self.direction)
            self.relative_direction = self.direction
        elif self.driven_percentage < 0.7:
            relative_x = 0.3 + (self.driven_percentage - 0.3)
            relative_y = 0.7
            self.relative_x, self.relative_y = self.rotate_points(relative_x, relative_y, self.direction)
            self.relative_direction = (self.direction + 1) % 4
        elif self.driven_percentage < 1:
            relative_x = 0.7
            relative_y = 0.7 - (7/3) * (self.driven_percentage - 0.7)
            self.relative_x, self.relative_y = self.rotate_points(relative_x, relative_y, self.direction)
            self.relative_direction = (self.direction + 2) % 4
        else:
            pass

    def straight_on(self):
        if self.driven_percentage < 1:
            relative_x = 0.3
            relative_y = self.driven_percentage
            self.relative_x, self.relative_y = self.rotate_points(relative_x, relative_y, self.direction)
            self.relative_direction = self.direction
        else:
            pass

    def left_turn(self):
        if self.driven_percentage < 0.5:
            relative_x = 0.3
            relative_y = (3/5) * self.driven_percentage
            self.relative_x, self.relative_y = self.rotate_points(relative_x, relative_y, self.direction)
            self.relative_direction = self.direction
        elif self.driven_percentage < 1:
            relative_x = 0.3 - (3/5) * (self.driven_percentage - 0.5)
            relative_y = 0.3
            self.relative_x, self.relative_y = self.rotate_points(relative_x, relative_y, self.direction)
            self.relative_direction = (self.direction - 1) % 4
        else:
            pass

    def right_turn(self):
        if self.driven_percentage < 0.5:
            relative_x = 0.3
            relative_y = (7/5) * self.driven_percentage
            self.relative_x, self.relative_y = self.rotate_points(relative_x, relative_y, self.direction)
            self.relative_direction = self.direction
        elif self.driven_percentage < 1:
            relative_x = 0.3 + (7/5) * (self.driven_percentage - 0.5)
            relative_y = 0.7
            self.relative_x, self.relative_y = self.rotate_points(relative_x, relative_y, self.direction)
            self.relative_direction = (self.direction + 1) % 4
        else:
            pass
