#pragma once

#include <gba_base.h>


#define TRAX_MAGIC      'XART'      // little endian
#define TRAX_VERSION    1

typedef struct
{
    u32 magic;  // TRAX
    u8  version;
    u8  patternCount;
    u16 ticksPerStep;

    // TODO: song def
    // TODO: snd3 instrument def
    
} TraxHdr;


typedef struct
{
    u16 sqr1Ctrl;
    u16 sqr1Freq;

    u16 sqr2Ctrl;
    u16 sqr2Freq;

    u16 wtblCtrl;
    u16 wtblFreq;

    u16 noizCtrl;
    u16 noizTimbre;

} TraxStep;


typedef struct
{
    u8          numSteps;

    u8          _unused[3];

    TraxStep    steps[0];

} TraxPattern;



typedef struct
{
    const TraxHdr* song;

    u16     ticksTillNextStep;
    u8      curPat;
    u8      nextStep;

} TraxPlayerState;


void trax_startPlaying(const void* song, TraxPlayerState* state);
void trax_tick(TraxPlayerState* state);
