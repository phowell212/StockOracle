# Stock Oracle Group
# 4/10/2025
# Graph class

class Graph:
    """
       A class to represent and manipulate stock data stored as (date, value) tuples.
    """
    def __init__(self, data=None):
        """
            Initializes the Graph object with optional preloaded data.

            Parameters:
                data (list of tuple): List of (date, value) tuples. Defaults to an empty list.
        """
        if data is None:
            data = []
        self.__data = data

    def read_csv(self):
        """
            Reads stock data from 'data.csv', skipping the header.
            Assumes the CSV format is: Date,Value
        """
        self.__data = []
        with open("data.csv", "r") as f:
            lines = f.readlines()[1:]  # Skip the header
            for line in lines:
                date, value = line.strip().split(",")
                self.__data.append((date, int(value)))

    def clear_csv(self):
        """
            Clears the contents of 'data.csv', leaving only the header.
            Also resets the internal data list.
        """
        with open("data.csv", "w") as f:
            f.write("Date,Value\n")
        self.__data = []

    @property
    def data(self):
        """
            Getter for the internal data list.

            Returns:
                list of tuple: The stored (date, value) pairs.
        """
        return self.__data

    @data.setter
    def data(self, value):
        """
            Setter for the internal data list.

            Parameters:
                value (list of tuple): New data to replace current internal data.
        """
        self.__data = value
