#pragma once

#include "gen/trig.h"


// 1 deg256ree is 1/256 of a circle

// returns a 18.14 fixed point value for sin of theta deg256rees (where theta is in 18.14 fixed point)
int sin256_14(int theta_14);

inline int cos256_14(int theta_14)
{
    return sin256_14(theta_14 + (64 << 6));
}
