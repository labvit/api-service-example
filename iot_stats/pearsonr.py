from math import sqrt, lgamma, log, exp, sqrt

from operator import mul,add

__all__ = ['pearsonr_py']

def contfractbeta(a : float,b : float, x: float, ITMAX = 200) -> float:
    """ contfractbeta() evaluates the continued fraction form of the incomplete Beta function; incompbeta().  
    (Code translated from: Numerical Recipes in C.)"""
     
    EPS = 3.0e-7
    bm = az = am = 1.0e0
    qab = a+b
    qap = a+1.0e0
    qam = a-1.0e0
    bz = 1.0e0-qab*x/qap
     
    for i in range(ITMAX+1):
        em = float(i+1)
        tem = em + em
        d = em*(b-em)*x/((qam+tem)*(a+tem))
        ap = az + d*am
        bp = bz+d*bm
        d = -(a+em)*(qab+em)*x/((qap+tem)*(a+tem))
        app = ap+d*az
        bpp = bp+d*bz
        aold = az
        am = ap/bpp
        bm = bp/bpp
        az = app/bpp
        bz = 1.0
        if (abs(az-aold)<(EPS*abs(az))):
            return az
         
def incompbeta(a : float, b : float, x: float) -> float:
     
    ''' incompbeta(a,b,x) evaluates incomplete beta function, here a, b > 0 and 0 <= x <= 1. This function requires contfractbeta(a,b,x, ITMAX = 200) 
    (Code translated from: Numerical Recipes in C.)'''
     
    if (x == 0):
        return 0;
    elif (x == 1):
        return 1;
    else:
        lbeta = lgamma(a+b) - lgamma(a) -lgamma(b) + a * log(x) + b * log(1-x)
        if (x < (a+1) / (a+b+2)):
            return exp(lbeta) * contfractbeta(a, b, x) / a;
        else:
            return 1 - exp(lbeta) * contfractbeta(b, a, 1-x) / b;

def pearsonr_py(x : list,y : list) -> list:
  if len(x) != len(y):
    raise RuntimeError('argument length mismatch')

  sx = sum(x)
  sy = sum(y)
  sx2= sum(map(mul,x,x))
  sy2= sum(map(mul,y,y))
  n = len(x)
  r = (n*sum(map(mul, x,y)) - sx*sy)\
         / sqrt((n*sx2-sx*sx)*(n*sy2 - sy*sy))
  df = n-2
  TINY = 1.0e-20
  t = r*sqrt(df/((1.0-r+TINY)*(1.0+r+TINY)))
  prob = incompbeta(0.5*df,0.5,df/(df+t*t))
  return r,prob

