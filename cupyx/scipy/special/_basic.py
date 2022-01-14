"""basic special functions

cotdg and tandg implementations are adapted from the following SciPy code:

https://github.com/scipy/scipy/blob/master/scipy/special/cephes/tandg.c

Cephes Math Library Release 2.0:  April, 1987
Copyright 1984, 1987 by Stephen L. Moshier
Direct inquiries to 30 Frost Street, Cambridge, MA 02140
"""

from cupy import _core


log1p = _core.create_ufunc(
    "cupyx_scipy_log1p",
    ("f->f", "d->d"),
    "out0 = out0_type(log1p(in0));",
    doc="""Elementwise function for scipy.special.log1p

    Calculates log(1 + x) for use when `x` is near zero.

    Notes
    -----
    This implementation currently does not support complex-valued `x`.

    .. seealso:: :meth:`scipy.special.log1p`

    """,
)

cbrt = _core.create_ufunc(
    'cupyx_scipy_special_cbrt', ('f->f', 'd->d'),
    'out0 = cbrt(in0)',
    doc='''Cube root.

    .. seealso:: :meth:`scipy.special.cbrt`

    ''')


exp2 = _core.create_ufunc(
    'cupyx_scipy_special_exp2', ('f->f', 'd->d'),
    'out0 = exp2(in0)',
    doc='''Computes ``2**x``.

    .. seealso:: :meth:`scipy.special.exp2`

    ''')


exp10 = _core.create_ufunc(
    'cupyx_scipy_special_exp10', ('f->f', 'd->d'),
    'out0 = exp10(in0)',
    doc='''Computes ``10**x``.

    .. seealso:: :meth:`scipy.special.exp10`

    ''')


expm1 = _core.create_ufunc(
    'cupyx_scipy_special_expm1', ('f->f', 'd->d'),
    'out0 = expm1(in0)',
    doc='''Computes ``exp(x) - 1``.

    .. seealso:: :meth:`scipy.special.expm1`

    ''')


pi180_preamble = """
    __constant__ double PI180 = 1.74532925199432957692E-2;  // pi/180
"""

cosdg = _core.create_ufunc(
    'cupyx_scipy_special_cosdg', ('f->f', 'd->d'),
    'out0 = cos(PI180 * in0)',
    preamble=pi180_preamble,
    doc='''Cosine of x with x in degrees.

    .. seealso:: :meth:`scipy.special.cosdg`

    ''')


sindg = _core.create_ufunc(
    'cupyx_scipy_special_sindg', ('f->f', 'd->d'),
    'out0 = sin(PI180 * in0)',
    preamble=pi180_preamble,
    doc='''Sine of x with x in degrees.

    .. seealso:: :meth:`scipy.special.sindg`

    ''')


tancot_implementation = pi180_preamble + """


// include for CUDART_INF
#include <cupy/math_constants.h>

__constant__ double  lossth = 1.0e14;

__device__ static double tancot(double, int);

__device__ static double tandg(double x)
{
    return tancot(x, 0);
}


__device__ static double cotdg(double x)
{
    return tancot(x, 1);
}


__device__ static double tancot(double xx, int cotflg)
{
    double x;
    int sign;

    /* make argument positive but save the sign */
    if (xx < 0) {
        x = -xx;
        sign = -1;
    }
    else {
        x = xx;
        sign = 1;
    }

    if (x > lossth) {
        // sf_error("tandg", SF_ERROR_NO_RESULT, NULL);
        return 0.0;
    }

    /* modulo 180 */
    x = x - 180.0 * floor(x / 180.0);
    if (cotflg) {
        if (x <= 90.0) {
            x = 90.0 - x;
        } else {
            x = x - 90.0;
            sign *= -1;
        }
    } else {
        if (x > 90.0) {
            x = 180.0 - x;
            sign *= -1;
        }
    }
    if (x == 0.0) {
        return 0.0;
    }
    else if (x == 45.0) {
        return sign * 1.0;
    }
    else if (x == 90.0) {
        // sf_error((cotflg ? "cotdg" : "tandg"), SF_ERROR_SINGULAR, NULL);
        return CUDART_INF;
    }
    /* x is now transformed into [0, 90) */
    return sign * tan(x * PI180);
}
"""

tandg = _core.create_ufunc(
    'cupyx_scipy_special_tandg', ('f->f', 'd->d'),
    'out0 = tandg(in0)',
    preamble=tancot_implementation,
    doc='''Tangent of x with x in degrees.

    .. seealso:: :meth:`scipy.special.tandg`

    ''')


cotdg = _core.create_ufunc(
    'cupyx_scipy_special_cotdg', ('f->f', 'd->d'),
    'out0 = cotdg(in0)',
    preamble=tancot_implementation,
    doc='''Cotangent of x with x in degrees.

    .. seealso:: :meth:`scipy.special.cotdg`

    ''')
