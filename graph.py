# Stock Oracle Group
# 4/10/2025
# Graph class
import random
import datetime

class Graph:
    def __init__(self, data=None):
        if data is None:
            data = []
        self.__data = data

    def generate_csv(self):
        self.__data = []
        start_date = datetime.date(2025, 1, 1)

        # Generate a year of datapoints
        current_value = random.randint(100, 200)
        for i in range(365):

            # Date of representation
            date_obj = start_date + datetime.timedelta(days=i)

            # Drift
            if i > 0:
                current_value += random.randint(-10, 10)

            date_str = date_obj.strftime("%Y-%m-%d")
            self.__data.append((date_str, current_value))

        # Write to CSV
        with open("data.csv", "w") as f:
            f.write("Date,Value\n")
            for date, value in self.__data:
                f.write(f"{date},{value}\n")

    def read_csv(self):
        self.__data = []
        with open("data.csv", "r") as f:
            lines = f.readlines()[1:]  # Skip the header
            for line in lines:
                date, value = line.strip().split(",")
                self.__data.append((date, int(value)))

    def clear_csv(self):
        with open("data.csv", "w") as f:
            f.write("Date,Value\n")
        self.__data = []

    @property
    def data(self):
        return self.__data
