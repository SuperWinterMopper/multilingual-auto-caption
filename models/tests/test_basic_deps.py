from pydantic import BaseModel
import numpy as np

class TestModel(BaseModel):
    message: str

def test_model():
    test_instance = TestModel(message="Hello, Pydantic!")
    assert test_instance.message == "Hello, Pydantic!"

def test_numpy():
    arr = np.array([1, 2, 3])
    assert arr.sum() == 6
    