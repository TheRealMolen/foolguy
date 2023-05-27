#pragma once

#include <gba_sound.h>


#define FastCopy16(dst, src, numShorts)	CpuFastSet((src), (dst), COPY16 | ((unsigned int)(numShorts)))
#define FastCopy32(dst, src, numWords)	CpuFastSet((src), (dst), COPY32 | ((unsigned int)(numWords)))
#define FastFill16(dst, src, numShorts)	CpuFastSet((src), (dst), COPY16 | FILL | ((unsigned int)(numShorts)))

#define ARRAYCOUNT(_arr) ((sizeof(_arr) / sizeof(_arr[0])))


#define TILES_PER_ROW	32


// use loosely tonc/tepples-style sound register names, plus some tweaks

#define REG_SNDSTATUS   REG_SOUNDCNT_X
#define SNDSTATUS_ENABLE    (1 << 7)

#define REG_SNDMIX      REG_SOUNDCNT_L
#define SNDMIX_LVOL(vol0_7)     ((vol0_7))
#define SNDMIX_RVOL(vol0_7)     ((vol0_7) << 4)
#define SNDMIX_SND1_C           (SND1_R_ENABLE | SND1_L_ENABLE)
#define SNDMIX_SND2_C           (SND2_R_ENABLE | SND2_L_ENABLE)
#define SNDMIX_SND3_C           (SND3_R_ENABLE | SND3_L_ENABLE)
#define SNDMIX_SND4_C           (SND4_R_ENABLE | SND4_L_ENABLE)

#define REG_SNDMIX2     REG_SOUNDCNT_H
#define SNDMIX2_DMGVOL_MAX  DSOUNDCTRL_DMG100

// shared FREQ / TIMBRE
#define SND_TRIGGER     (0x8000)
#define SNDFREQ(hz)     ((2048 - ((1<<17) / (hz))) & 2047)

// sound1 - pulse w/ freq sweep support
#define	REG_SND1SWEEP	REG_SOUND1CNT_L
#define	REG_SND1CTRL    REG_SOUND1CNT_H
#define	REG_SND1FREQ	REG_SOUND1CNT_X

// sound2 - pulse
#define	REG_SND2CTRL    REG_SOUND2CNT_L
#define	REG_SND2FREQ	REG_SOUND2CNT_H

// sound3 - wavetable
#define	REG_SND3CFG	    (*((u16 volatile *) (REG_BASE + 0x070)))
#define	REG_SND3CTRL    (*((u16 volatile *) (REG_BASE + 0x072)))
#define	REG_SND3FREQ	(*((u16 volatile *) (REG_BASE + 0x074)))
#define REG_SND3WAV0    (*((u32 volatile *) (REG_BASE + 0x090)))    // MSB | sample 6 | sample 7 | .... | sample 1 | LSB
#define REG_SND3WAV1    (*((u32 volatile *) (REG_BASE + 0x094)))
#define REG_SND3WAV2    (*((u32 volatile *) (REG_BASE + 0x098)))
#define REG_SND3WAV3    (*((u32 volatile *) (REG_BASE + 0x09c)))

// sound4 - noise
#define	REG_SND4CTRL    (*((u16 volatile *) (REG_BASE + 0x078)))
#define	REG_SND4TIMBRE	(*((u16 volatile *) (REG_BASE + 0x07c)))

