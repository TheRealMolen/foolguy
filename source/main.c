
#include <gba_base.h>
#include <gba_video.h>
#include <gba_interrupt.h>
#include <gba_systemcalls.h>
#include <gba_input.h>
#include <gba_interrupt.h>
#include <stdio.h>
#include <stdlib.h>

#define ARRAYCOUNT(_arr) ((sizeof(_arr) / sizeof(_arr[0])))

const u16 PALETTE[] =
{
	RGB8(0x00, 0x00, 0x00),
	RGB8(0x44, 0x44, 0x44),
	RGB8(0x88, 0x88, 0x88),
	RGB8(0xcc, 0xcc, 0xcc),
	RGB8(0xff, 0xff, 0xff),
	RGB8(0xff, 0x20, 0x20),
	RGB8(0x20, 0xff, 0x20),
	RGB8(0x20, 0x20, 0xff),
};

const u8 TILE_DATA[] =
{
	// tile 0
	0, 0, 0, 1, 1, 0, 0, 0,
	0, 0, 1, 2, 2, 1, 0, 0,
	0, 1, 2, 3, 3, 2, 1, 0,
	1, 2, 3, 4, 4, 3, 2, 1,
	1, 2, 3, 4, 4, 3, 2, 1,
	0, 1, 2, 3, 3, 2, 1, 0,
	0, 0, 1, 2, 2, 1, 0, 0,
	0, 0, 0, 1, 1, 0, 0, 0,

	// tile 1
	0, 1, 2, 3, 4, 5, 6, 7, 
	1, 2, 3, 4, 5, 6, 7, 0, 
	2, 3, 4, 5, 6, 7, 0, 1, 
	3, 4, 5, 6, 7, 0, 1, 2,
	4, 5, 6, 7, 0, 1, 2, 3,
	5, 6, 7, 0, 1, 2, 3, 4,
	6, 7, 0, 1, 2, 3, 4, 5,
	7, 0, 1, 2, 3, 4, 5, 6,

	// tile 2
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 5, 0, 0, 5, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 5, 0, 0, 0, 0, 5, 0, 
	0, 0, 5, 0, 0, 5, 0, 0, 
	0, 0, 0, 5, 5, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
};


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
	REG_BG0CNT = BG_256_COLOR | SCREEN_BASE(31);

	// copy the palette into palette 0
	memcpy16(BG_COLORS, PALETTE, ARRAYCOUNT(PALETTE));

	// copy the tile data into bank0 of VRAM
	memcpy16((void*)VRAM, TILE_DATA, ARRAYCOUNT(TILE_DATA) / 2);

	u16* map = MAP_BASE_ADR(31);
	map[0] = 1;
	map[1] = 2;

    for(;;)
	{
		VBlankIntrWait();
	}

	return 1;
}


