from outerr import quaternion
import numpy as np
class q():
    def __init__(self,a):
        self.a=a
    def __add__(self,b):
        return q(self.a + b)
    def __radd__(self,b):
        return q(self.a + b)
    def __mul__(self,b):
        return q(self.a * b)
    def __rmul__(self,b):
        return q(self.a * b)
    def __neg__(self,b):
        return q(-self.a)
    def __sub__(self, other):
        return q(self.a-other)
    def __rsub__(self, other):
        return q(other - self.a)
    def __repr__(self):
        return str(self.a)
    def __matmul__(self, other):
        return self

A = np.array([[q(1),q(2)],[q(3),q(4)]])
print(A @ A)

