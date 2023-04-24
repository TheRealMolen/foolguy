
#include <gba_video.h>
#include <gba_interrupt.h>
#include <gba_systemcalls.h>
#include <gba_input.h>
#include <stdio.h>
#include <stdlib.h>


int main(void)
{
    REG_DISPCNT = BG2_ON | MODE_3;

	for (int i=0; i<100; ++i)
	{
		MODE3_FB[i][i] = i << 2;
	}

    MODE3_FB[80][120] = 0x001F;
	MODE3_FB[80][136] = 0x03E0;
	MODE3_FB[96][120] = 0x7c00;

    for(;;) {}

	return 1;
}


