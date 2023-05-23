#pragma once

#include <gba_base.h>


#define TRAX_MAGIC      'XART'      // little endian
#define TRAX_VERSION    1

typedef struct
{
    u32 magic;  // TRAX
    u8  version;
    u8  patternCount;
    u16 ticksPerBeat;

    // TODO: song def
    // TODO: snd3 instrument def
    
} ALIGN(4) TraxHdr;


typedef struct
{
    u16 sqr1_ctrl;
    u16 sqr1_freq;

    u16 sqr2_ctrl;
    u16 sqr2_freq;

    u16 wtbl_ctrl;
    u16 wtbl_freq;

    u16 noiz_ctrl;
    u16 noiz_freq;

} ALIGN(4) TraxBeat;


typedef struct
{
    u8  numBeats;

    u8  dummy[3];

    TraxBeat    beats[0];

} ALIGN(4) TraxPattern;

