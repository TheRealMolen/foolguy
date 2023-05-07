
#include <gba_base.h>
#include <gba_video.h>
#include <gba_interrupt.h>
#include <gba_systemcalls.h>
#include <gba_input.h>
#include <gba_interrupt.h>

#include "gen/foolguy_pal.h"
#include "gen/GFX_UI.h"
#include "gen/GUI_font.h"
#include "math.h"

#define FastCopy16(dst, src, numShorts)	CpuFastSet((src), (dst), COPY16 | ((unsigned int)(numShorts)))
#define FastCopy32(dst, src, numWords)	CpuFastSet((src), (dst), COPY32 | ((unsigned int)(numWords)))
#define FastFill16(dst, src, numShorts)	CpuFastSet((src), (dst), COPY16 | FILL | ((unsigned int)(numShorts)))

#define ARRAYCOUNT(_arr) ((sizeof(_arr) / sizeof(_arr[0])))


#define BG_BASE	31
#define UI_BASE	29
#define TXT_BASE 27


int bgang = 0;
static const int BG_RADIUS = 9;

void updateBg0()
{
	BG_OFFSET[0].x = 16 + ((BG_RADIUS * sin256_14(bgang)) >> 14);
	BG_OFFSET[0].y = 16 + ((BG_RADIUS * cos256_14(bgang)) >> 14);
}


#define TILES_PER_ROW	32

void drawText(const char* msg, u32 x, u32 y)
{
	u16* textBase = (u16*)MAP_BASE_ADR(TXT_BASE);
	u16* out = textBase + (x + (y * TILES_PER_ROW));

	for (const char* pc = msg; *pc; ++pc)
	{
		u32 c = *pc;
		if (c == '\n')
		{
			++y;
			out = textBase + (x + (y * TILES_PER_ROW));
			continue;
		}

		if (c < GUI_FONT_firstchar || c > GUI_FONT_lastchar)
		{
			++out;
			continue;
		}

		u16 glyph = GUI_FONT_glyphtiles[c - GUI_FONT_firstchar];
		*out = glyph;
		++out;
	}
}


int main()
{
	// set up interrupts and enable vblank wait
	irqInit();
	irqEnable(IRQ_VBLANK);
	REG_IME = 1;

	REG_DISPCNT = MODE_0 | BG0_ON | BG1_ON | BG2_ON;
	REG_BG0CNT = BG_16_COLOR | SCREEN_BASE(BG_BASE) | BG_PRIORITY(3);
	REG_BG1CNT = BG_16_COLOR | SCREEN_BASE(UI_BASE) | BG_PRIORITY(2);
	REG_BG2CNT = BG_16_COLOR | SCREEN_BASE(TXT_BASE) | BG_PRIORITY(1);

	// alpha blend text layer (bg2) on top of window layer (bg1) to enable antialiasing
	REG_BLDCNT	= (1<<2)		// 1st target from bg2
				| (1<<9)		// 2nd target from bg1
				| (1<<6);		// alpha blend
	REG_BLDALPHA = 15 | (8<<8);

	// copy the palette into palette 0
	FastCopy16(BG_COLORS, FOOLGUY_PAL_paldata, FOOLGUY_PAL_palcount);

	// copy the tile data into bank0 of VRAM
	FastCopy32((void*)VRAM, GFX_UISharedTiles, GFX_UISharedTilesLen / 4);

	// copy map across
	FastCopy16(MAP_BASE_ADR(BG_BASE), BG_GradientMap, BG_GradientMapLen / 2);
	FastCopy16(MAP_BASE_ADR(UI_BASE), GUI_WindowMap, GUI_WindowMapLen / 2);

	// blank out text bg
	u16 zero = 0;
	FastFill16(MAP_BASE_ADR(TXT_BASE), &zero, 1024);

	drawText("HELLO ME DUCKS\n"
			"OH WHAT A LOVELY\n"
			"BUNCH O COCONUTS\n"
			"YOU HAVE THERE\n"
			"...\n"
			"I ALWAYS FANCIED\n"
			"THE BEACH LIFE\n\n\n"
			"SIPPIN A PINA\n"
			"COLADA WHILE THE\n"
			"WORLD DRIFTS BY",
		7, 4);

	BG_OFFSET[1].x = -12;
	BG_OFFSET[1].y = 17;

	updateBg0();

    for(;;)
	{
		VBlankIntrWait();

		bgang += 30;
		updateBg0();
	}

	return 1;
}


