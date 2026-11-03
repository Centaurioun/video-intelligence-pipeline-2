from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction

@dataclass(frozen=True)
class Rational:
    numerator:int; denominator:int
    def __post_init__(self):
        if self.denominator<=0: raise ValueError("rational denominator must be positive")
        f=Fraction(self.numerator,self.denominator)
        object.__setattr__(self,"numerator",f.numerator); object.__setattr__(self,"denominator",f.denominator)
    def _f(self): return Fraction(self.numerator,self.denominator)
    def _coerce(self,o): return o._f() if isinstance(o,Rational) else Fraction(o)
    def __add__(self,o): return _from_f(self._f()+self._coerce(o))
    def __sub__(self,o): return _from_f(self._f()-self._coerce(o))
    def __mul__(self,o): return _from_f(self._f()*self._coerce(o))
    def __truediv__(self,o): return _from_f(self._f()/self._coerce(o))
    def __lt__(self,o): return self._f()<self._coerce(o)
    def __le__(self,o): return self._f()<=self._coerce(o)
    def __gt__(self,o): return self._f()>self._coerce(o)
    def __ge__(self,o): return self._f()>=self._coerce(o)
    def to_decimal_str(self,places):
        q=Decimal(1).scaleb(-places)
        return str((Decimal(self.numerator)/Decimal(self.denominator)).quantize(q,rounding=ROUND_HALF_EVEN))
def _from_f(f): return Rational(f.numerator,f.denominator)

@dataclass(frozen=True)
class TimeBase:
    num:int; den:int
    def __post_init__(self):
        if self.num<=0 or self.den<=0: raise ValueError("time base must be positive")
    def ticks_to_seconds(self,ticks): return Rational(ticks*self.num,self.den)
    def seconds_to_ticks_floor(self,seconds): return (seconds.numerator*self.den)//(seconds.denominator*self.num)
