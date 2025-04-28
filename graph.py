# Stock Oracle Group
# 4/10/2025
# Graph class

class Graph:
    def __init__(self, data=None):
        if data is None:
            data = []
        self.__data = data

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
