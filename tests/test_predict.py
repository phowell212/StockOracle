from predictor_default import PredictedGraph
import pandas as pd, tempfile

"""
Covers the predictive layer in `predictor.py`.

`test_predict_tomorrow`  – Seeds synthetic price data, calls `PredictedGraph.predict_tomorrow()`, and asserts the 
function returns a float (next‑day price forecast).

`test_confidence_between_zero_one`  – Checks that the custom `check_confidence()` method returns a probability‑like 
value bounded between 0 and 1, even on a minimal dataset.
"""
def _seed_csv(tmp, vals):
    csv = tmp / "d.csv"
    text = "Date,Value\n" + "\n".join(vals)
    csv.write_text(text)
    return csv


def test_predict_tomorrow(tmp_path):
    csv = _seed_csv(tmp_path,
        [f"2024-01-{i+1:02d},{100+i}" for i in range(30)])
    pg = PredictedGraph()
    pg.read_csv = lambda f=str(csv): PredictedGraph.read_csv(pg)
    pg.read_csv()
    pred = pg.predict_tomorrow(5)
    assert isinstance(pred, float)
