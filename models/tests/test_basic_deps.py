from pydantic import BaseModel
import numpy as np

def test_numpy():
    arr = np.array([1, 2, 3])
    assert arr.sum() == 6
    