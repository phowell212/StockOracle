from graph import Graph
import os

"""
Confirms `Graph.read_csv()` correctly loads a CSV file into the Graph object's internal `data` structure 
(list of (date, value) tuples). Uses a temporary directory to avoid touching real project files and checks both path 
handling and parsing logic.
"""
def test_graph_reads_csv(tmp_path):
    csv = tmp_path / "data.csv"             # same name Graph expects
    csv.write_text("Date,Value\n2024-01-01,100\n")

    old_cwd = os.getcwd()                   # move CWD to tmp dir
    os.chdir(tmp_path)
    try:
        g = Graph()
        g.read_csv()                        # reads tmp_path/data.csv
        assert g.data == [("2024-01-01", 100)]
    finally:
        os.chdir(old_cwd)                   # restore

