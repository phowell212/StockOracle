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
        self.__data = []  # start fresh

        # Start from Jan 1, 2025
        start_date = datetime.date(2025, 1, 1)

        # Generate 365 daily points
        current_value = random.randint(100, 200)
        for i in range(365):
            # get the actual date
            date_obj = start_date + datetime.timedelta(days=i)
            # random “drift”
            if i > 0:
                current_value += random.randint(-10, 10)
            # store as string (e.g. "2025-01-01")
            date_str = date_obj.strftime("%Y-%m-%d")

            self.__data.append((date_str, current_value))

        # Write to CSV
        with open("data.csv", "w") as f:
            f.write("Date,Value\n")
            for date, value in self.__data:
                f.write(f"{date},{value}\n")

    def read_csv(self):
        self.__data = []  # Clear existing data
        with open("data.csv", "r") as f:
            lines = f.readlines()[1:]  # Skip the header
            for line in lines:
                date, value = line.strip().split(",")
                self.__data.append((date, int(value)))

    def clear_csv(self):
        # Clear the CSV file
        with open("data.csv", "w") as f:
            f.write("Date,Value\n")
        self.__data = []

    @property
    def data(self):
        return self.__data