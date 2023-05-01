
#include <gba_base.h>
#include <gba_video.h>
#include <gba_interrupt.h>
#include <gba_systemcalls.h>
#include <gba_input.h>
#include <gba_interrupt.h>
#include <stdio.h>
#include <stdlib.h>

#include "gen/foolguy_pal.h"
#include "gen/bg_gradient.h"

#define CPUFASTSET16(dst, src, numShorts)	CpuFastSet((src), (dst), COPY16 | ((unsigned int)(numShorts)))
#define CPUFASTSET32(dst, src, numWords)	CpuFastSet((src), (dst), COPY32 | ((unsigned int)(numWords)))


#define ARRAYCOUNT(_arr) ((sizeof(_arr) / sizeof(_arr[0])))


inline void memcpy16(void* dest, const void* src, int nWords)
{
	// NB. should just wrap CpuFastSet()
	
	u16* dest16 = (u16*)dest;
	const u16* src16 = (const u16*)src;
	const u16* src16End = src16 + nWords;

	for (; src16 != src16End; ++src16, ++dest16)
		*dest16 = *src16;
}


int main()
{
	// set up interrupts and enable vblank wait
	irqInit();
	irqEnable(IRQ_VBLANK);
	REG_IME = 1;

	REG_DISPCNT = MODE_0 | BG0_ON;
	REG_BG0CNT = BG_16_COLOR | SCREEN_BASE(31);

	// copy the palette into palette 0
	memcpy16(BG_COLORS, FOOLGUY_PAL_paldata, FOOLGUY_PAL_palcount);

	// copy the tile data into bank0 of VRAM
	CPUFASTSET32((void*)VRAM, bg_gradientTiles, bg_gradientTilesLen / 4);

	// copy map across
	memcpy16(MAP_BASE_ADR(31), bg_gradientMap, bg_gradientMapLen / 2);

    for(;;)
	{
		VBlankIntrWait();
	}

	return 1;
}


