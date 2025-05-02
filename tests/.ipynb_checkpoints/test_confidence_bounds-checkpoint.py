# +
from predictor import PredictedGraph

"""
Validates the statistical helper `check_confidence()` in `predictor.py`.

This test builds a small synthetic price series (four rows) in a temporary CSV, loads it through `PredictedGraph`, and 
asserts that the returned confidence score is a proper probability which is, it always falls between 0 and 1 regardless of 
dataset size. This guards against division or integration errors that could push the score outside the expected range.
"""
def test_confidence_between_zero_one(tmp_path):
    # supply tiny synthetic data
    csv = tmp_path / "d.csv"
    csv.write_text("\n".join([
        "Date,Value",
        "2024-01-01,100",
        "2024-01-02,101",
        "2024-01-03,102",
        "2024-01-04,103",]))
    pg = PredictedGraph()
    pg.read_csv = lambda f=str(csv): PredictedGraph.read_csv(pg)
    pg.read_csv()
    conf = pg.check_confidence(2, 1)
    assert 0.0 <= conf <= 1.0
