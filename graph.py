# Stock Oracle Group
# 4/10/2025
# Graph class
import random

class Graph:
    def __init__(self, data=None):
        self.__data = data if data is not None else []

    def generate_csv(self):
        # Generate the data
        for i in range(365):
            date = f"2025-{i // 30 + 1:02d}-{i % 30 + 1:02d}"

            # Generate random data, ensuring each point does not deviate too much from the previous one
            if i == 0:
                value = random.randint(100, 200)
            else:
                value = self.__data[-1][1]
                value += random.randint(-10, 10)
            self.__data.append((date, value))

        # Write the data to a CSV file
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

    @property
    def data(self):
        return self.__data