
#include <gba_base.h>
#include <gba_video.h>
#include <gba_interrupt.h>
#include <gba_systemcalls.h>
#include <gba_input.h>
#include <gba_interrupt.h>

#include "gen/bg_gradient.h"
#include "gen/foolguy_pal.h"
#include "math.h"

#define FastCopy16(dst, src, numShorts)	CpuFastSet((src), (dst), COPY16 | ((unsigned int)(numShorts)))
#define FastCopy32(dst, src, numWords)	CpuFastSet((src), (dst), COPY32 | ((unsigned int)(numWords)))

#define ARRAYCOUNT(_arr) ((sizeof(_arr) / sizeof(_arr[0])))


int bgang = 0;
static const int BG_RADIUS = 9;

void updateBg0()
{
	BG_OFFSET[0].x = 16 + ((BG_RADIUS * sin256_14(bgang)) >> 14);
	BG_OFFSET[0].y = 16 + ((BG_RADIUS * cos256_14(bgang)) >> 14);
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
	FastCopy16(BG_COLORS, FOOLGUY_PAL_paldata, FOOLGUY_PAL_palcount);

	// copy the tile data into bank0 of VRAM
	FastCopy32((void*)VRAM, bg_gradientTiles, bg_gradientTilesLen / 4);

	// copy map across
	FastCopy16(MAP_BASE_ADR(31), bg_gradientMap, bg_gradientMapLen / 2);


	updateBg0();

    for(;;)
	{
		VBlankIntrWait();

		bgang += 30;
		updateBg0();
	}

	return 1;
}


