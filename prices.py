def generate_price(starting_price: int, units_bought: int, interest_rate: float = 1.15):
    return int(starting_price * interest_rate ** units_bought)

class Prices:
    def __init__(self):
        self.roads_bought = 0
        self.vehicles_bought = 0
        self.time_bought = 0
        self.land_bought = 0
    def get_road_price(self):
        return generate_price(15, self.roads_bought, 1.10)

    def get_vehicle_price(self):
        return generate_price(50, self.vehicles_bought)

    def get_time_price(self):
        return generate_price(100, self.time_bought)

    def get_land_price(self):
        return generate_price(250, self.land_bought)

    def get_prices(self):
        return (self.get_road_price(), self.get_vehicle_price(),
                self.get_time_price(), self.get_land_price())
