from pydantic import BaseModel
import numpy as np
import torch

def test_numpy():
    arr = np.array([1, 2, 3])
    assert arr.sum() == 6

def test_tensor():
    t = torch.rand(3, 4)
    
    print(repr(t[0].shape))
    assert t.shape == (3, 4)