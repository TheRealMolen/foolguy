#include "trax.h"

#include "mlngba.h"


static const TraxPattern* getPattern(const TraxHdr* song, u32 patIx)
{
    return (const TraxPattern*)(song + 1);
}


void trax_startPlaying(const void* song, TraxPlayerState* state)
{
    state->song = (const TraxHdr*)song;
    
	REG_SNDSTATUS = SNDSTATUS_ENABLE;
	REG_SNDMIX2 = SNDMIX2_DMGVOL_MAX;
	REG_SNDMIX = SNDMIX_LVOL(7) | SNDMIX_RVOL(7) | SNDMIX_SND1_C | SNDMIX_SND2_C | SNDMIX_SND3_C | SNDMIX_SND4_C;

    state->curPat = 0;
    state->nextStep = 0;

    // select banked samples; select bank 1 for playback so we write to bank 0
    REG_SND3CFG = 0x40;
    REG_SND3WAV0 = state->song->wavetable.samples[0];
    REG_SND3WAV1 = state->song->wavetable.samples[1];
    REG_SND3WAV2 = state->song->wavetable.samples[0];
    REG_SND3WAV3 = state->song->wavetable.samples[1];
    // now switch back to bank 0 and enable playback
    REG_SND3CFG = 0x80;

    state->ticksTillNextStep = 1;
    trax_tick(state);
}


void trax_tick(TraxPlayerState* state)
{
    --state->ticksTillNextStep;
    if (state->ticksTillNextStep > 0)
        return;
    state->ticksTillNextStep = state->song->ticksPerStep;

    const TraxPattern* pattern = getPattern(state->song, state->curPat);
    const TraxStep* step = &pattern->steps[state->nextStep];

    if (step->sqr1Freq)
    {
        REG_SND1CTRL = step->sqr1Ctrl;
        REG_SND1FREQ = step->sqr1Freq;
    }

    if (step->sqr2Freq)
    {
        REG_SND2CTRL = step->sqr2Ctrl;
        REG_SND2FREQ = step->sqr2Freq;
    }

    if (step->wtblFreq)
    {
        // TODO: track current instrument & update if it's changed
        REG_SND3CTRL = step->wtblCtrl;
        REG_SND3FREQ = step->wtblFreq;
    }

    if (step->noizTimbre)
    {
        REG_SND4CTRL = step->noizCtrl;
        REG_SND4TIMBRE = step->noizTimbre;
    }

    ++state->nextStep;
    if (state->nextStep >= pattern->numSteps)
        state->nextStep = 0;
}

