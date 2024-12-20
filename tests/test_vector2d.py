import pytest
import math
#from TruckSimulator.Utils import Vector2D
from Utils import Vector2D

def test_vector2d_init():
    assert Vector2D(1, 2).x == 1
    assert Vector2D(1, 2).y == 2
    assert Vector2D(0, 0).x == 0
    assert Vector2D(0, 0).y == 0
    assert Vector2D(-1, -2).x == -1
    assert Vector2D(-1, -2).y == -2
    assert Vector2D(3.14, 2.71).x == 3.14
    assert Vector2D(3.14, 2.71).y == 2.71
    assert Vector2D(1, 2) != Vector2D(2, 1)
    assert Vector2D(1, 2) == Vector2D(1, 2)
    assert Vector2D(1, 2) != Vector2D(1, 2.1)

def test_vector2d_add():
    assert (Vector2D(1, 2) + Vector2D(3, 4)) == Vector2D(4, 6)
    assert (Vector2D(0, 0) + Vector2D(0, 0)) == Vector2D(0, 0)
    assert (Vector2D(-1, -2) + Vector2D(1, 2)) == Vector2D(0, 0)
    assert (Vector2D(1, 2) + Vector2D(-1, -2)) == Vector2D(0, 0)
    assert (Vector2D(1.5, 2.5) + Vector2D(0.5, 0.5)) == Vector2D(2, 3)
    assert (Vector2D(1, 2) + Vector2D(3, 4)) != Vector2D(5, 5)
    assert (Vector2D(1, 2) + Vector2D(0, 0)) == Vector2D(1, 2)
    assert (Vector2D(0, 0) + Vector2D(1, 2)) == Vector2D(1, 2)
    assert (Vector2D(1, 2) + Vector2D(1, 2)) == Vector2D(2, 4)
    assert (Vector2D(1, 2) + Vector2D(1, 2)) != Vector2D(2, 5)

def test_vector2d_sub():
    assert (Vector2D(1, 2) - Vector2D(1, 2)) == Vector2D(0, 0)
    assert (Vector2D(5, 5) - Vector2D(3, 3)) == Vector2D(2, 2)
    assert (Vector2D(0, 0) - Vector2D(1, 2)) == Vector2D(-1, -2)
    assert (Vector2D(1, 2) - Vector2D(0, 0)) == Vector2D(1, 2)
    assert (Vector2D(1, 2) - Vector2D(1, 1)) == Vector2D(0, 1)
    assert (Vector2D(1, 2) - Vector2D(1, 2)) != Vector2D(1, 1)
    assert (Vector2D(1, 2) - Vector2D(0, 1)) == Vector2D(1, 1)
    assert (Vector2D(1, 2) - Vector2D(1, 1)) != Vector2D(1, 0)
    assert (Vector2D(1, 2) - Vector2D(1, 2)) == Vector2D(0, 0)
    assert (Vector2D(1, 2) - Vector2D(0, 0)) != Vector2D(0, 0)

def test_vector2d_mul_scalar():
    assert Vector2D(1, 2) * 2 == Vector2D(2, 4)
    assert Vector2D(1, 2) * 0 == Vector2D(0, 0)
    assert Vector2D(1, 2) * -1 == Vector2D(-1, -2)
    assert Vector2D(1, 2) * 1 == Vector2D(1, 2)
    assert Vector2D(1, 2) * 0.5 == Vector2D(0.5, 1)
    assert Vector2D(1, 2) * 2 != Vector2D(3, 4)
    assert Vector2D(1, 2) * 2 == 2 * Vector2D(1, 2)
    assert Vector2D(1, 2) * 3 == Vector2D(3, 6)
    assert Vector2D(1, 2) * 1.5 == Vector2D(1.5, 3)
    assert Vector2D(1, 2) * 2 != Vector2D(2, 3)

def test_vector2d_eq():
    assert Vector2D(1, 2) == Vector2D(1, 2)
    assert Vector2D(1, 2) != Vector2D(2, 1)
    assert Vector2D(0, 0) == Vector2D(0, 0)
    assert Vector2D(1, 2) != Vector2D(1, 3)
    assert Vector2D(1, 2) != Vector2D(1.01, 2)
    assert Vector2D(1, 2) == Vector2D(1.0, 2.0)
    assert Vector2D(1, 2) != Vector2D(1, 2.1)
    assert Vector2D(1, 2) != Vector2D(2, 2)
    assert Vector2D(1, 2) == Vector2D(1, 2)
    assert Vector2D(1, 2) != Vector2D(1, 1)

@pytest.mark.skip(reason="Not implemented")
def test_vector2d_mag():
    assert Vector2D(3, 4).magnitude() == 5
    assert Vector2D(0, 0).magnitude() == 0
    assert Vector2D(1, 0).magnitude() == 1
    assert Vector2D(0, 1).magnitude() == 1
    assert Vector2D(1, 1).magnitude() == 2**0.5
    assert Vector2D(3, 4).magnitude() != 6
    assert Vector2D(-3, -4).magnitude() == 5
    assert Vector2D(3, -4).magnitude() == 5
    assert Vector2D(-3, 4).magnitude() == 5
    assert Vector2D(4, 3).magnitude() == 5

@pytest.mark.skip(reason="Not implemented")
def test_vector2d_norm():
    assert Vector2D(3, 4).normalize().magnitude() == 1
    assert Vector2D(0, 0).normalize() == Vector2D(0, 0)
    assert Vector2D(1, 0).normalize() == Vector2D(1, 0)
    assert Vector2D(0, 1).normalize() == Vector2D(0, 1)
    assert Vector2D(1, 1).normalize() == Vector2D(1/2**0.5, 1/2**0.5)
    assert Vector2D(3, 4).normalize() != Vector2D(3, 4)
    assert Vector2D(-3, -4).normalize().magnitude() == 1
    assert Vector2D(3, -4).normalize().magnitude() == 1
    assert Vector2D(-3, 4).normalize().magnitude() == 1
    assert Vector2D(4, 3).normalize().magnitude() == 1

def test_vector2d_dot():
    assert Vector2D(1, 0).dot(Vector2D(0, 1)) == 0
    assert Vector2D(1, 2).dot(Vector2D(3, 4)) == 11
    assert Vector2D(0, 0).dot(Vector2D(1, 2)) == 0
    assert Vector2D(1, 1).dot(Vector2D(1, 1)) == 2
    assert Vector2D(1, 2).dot(Vector2D(2, 1)) == 4
    assert Vector2D(1, 2).dot(Vector2D(1, 2)) == 5
    assert Vector2D(1, 2).dot(Vector2D(0, 0)) == 0
    assert Vector2D(1, 2).dot(Vector2D(-1, -2)) == -5
    assert Vector2D(1, 2).dot(Vector2D(1, -2)) == -3
    assert Vector2D(1, 2).dot(Vector2D(-1, 2)) == 3

def test_vector2d_str():
    assert str(Vector2D(1, 2)) == "(1.0, 2.0)"
    assert str(Vector2D(0, 0)) == "(0.0, 0.0)"
    assert str(Vector2D(-1, -2)) == "(-1.0, -2.0)"
    assert str(Vector2D(1.5, 2.5)) == "(1.5, 2.5)"
    assert str(Vector2D(3, 4)) != "(4.0, 3.0)"
    assert str(Vector2D(1, 2)) == str(Vector2D(1, 2))
    assert str(Vector2D(1, 2)) != str(Vector2D(2, 1))
    assert str(Vector2D(1, 2)) == "(1.0, 2.0)"
    assert str(Vector2D(1, 2)) != "(1.0, 2.1)"
    assert str(Vector2D(1, 2)) != "(1.0, 1.0)"

def test_vector2d_neg():
    assert -Vector2D(1, -2) == Vector2D(-1, 2)
    assert -Vector2D(0, 0) == Vector2D(0, 0)
    assert -Vector2D(-1, 2) == Vector2D(1, -2)
    assert -Vector2D(1, 1) == Vector2D(-1, -1)
    assert -Vector2D(1, 2) != Vector2D(1, 2)
    assert -Vector2D(1, 2) == Vector2D(-1, -2)
    assert -Vector2D(1, 2) != Vector2D(-1, 2)
    assert -Vector2D(1, 2) != Vector2D(1, -2)
    assert -Vector2D(1, 2) == -1 * Vector2D(1, 2)
    assert -Vector2D(1, 2) != Vector2D(1, 2)

def test_vector2d_extract():
    assert Vector2D(1, 2).extract() == (1, 2)
    assert Vector2D(0, 0).extract() == (0, 0)
    assert Vector2D(-1, -2).extract() == (-1, -2)
    assert Vector2D(1.5, 2.5).extract() == (1.5, 2.5)
    assert Vector2D(1000000, 2000000).extract() == (1000000, 2000000)
    assert Vector2D(1, 0).extract() == (1, 0)
    assert Vector2D(-1, 1).extract() == (-1, 1)
    assert Vector2D(0.1, 0.2).extract() == (0.1, 0.2)
    assert Vector2D(10, 20).extract() == (10, 20)
    assert Vector2D(5, 5).extract() == (5, 5)

def test_vector2d_rotate():
    print (Vector2D(1, 0).rotate(math.pi / 4))
    print (Vector2D(math.sqrt(2) / 2, math.sqrt(2) / 2))
    assert Vector2D(1, 0).rotate(math.pi / 2) == Vector2D(0, 1)
    assert Vector2D(1, 0).rotate(math.pi) == Vector2D(-1, 0)
    assert Vector2D(1, 0).rotate(3 * math.pi / 2) == Vector2D(0, -1)
    assert Vector2D(1, 1).rotate(0) == Vector2D(1, 1)
    assert Vector2D(1, 0).rotate(math.pi / 4) == Vector2D(math.sqrt(2) / 2, math.sqrt(2) / 2)
    assert Vector2D(0, 1).rotate(-math.pi / 2) == Vector2D(1, 0)
    assert Vector2D(1, 1).rotate(math.pi / 4) == Vector2D(0, math.sqrt(2))
    assert Vector2D(1, 2).rotate(2 * math.pi) == Vector2D(1, 2)
    assert Vector2D(1, 0).rotate(math.pi / 3) == Vector2D(0.5, math.sqrt(3) / 2)
    assert Vector2D(-1, 0).rotate(math.pi / 2) == Vector2D(0, -1)
