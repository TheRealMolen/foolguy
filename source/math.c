#include "math.h"


// returns a 18.14 fixed point value for sin of theta deg256rees (where theta is in 18.14 fixed point)
int sin256_14(int theta_14)
{
    // round down to 256 range for lookup
    int lookup = (theta_14 >> 6) & 0xff;

    int lo = sintbl_256[lookup];
    int hi = sintbl_256[(lookup + 1) & 0xff];

    int d = hi - lo;
    int extra = (d * (theta_14 & ((1 << 6) - 1))) >> 14;

    return lo + extra;
}
