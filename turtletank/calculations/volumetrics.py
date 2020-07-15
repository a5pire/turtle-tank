

class Volumetrics:

    @staticmethod
    def calculate_volume(length, width, depth):
        return float(round((length * width) * depth / 1000000, 2))

    @staticmethod
    def calculate_salts(water_added):
        salt_ratio = water_added / 10  # 1 teaspoon per 10 litres of water added
        return salt_ratio * 1

    @staticmethod
    def calculate_conditioner(water_added):
        conditioner_ratio = water_added / 200  # 5ml per 200 litres of water added
        return conditioner_ratio * 5

    @staticmethod
    def calculate_stabiliser(water_added):
        stabiliser_ratio = water_added / 80  # 5ml per 80 litres of water added
        return stabiliser_ratio * 5
