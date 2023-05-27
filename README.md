
gba shenanigans
===============

building & running:
-------------------
* install [devkitARM](https://devkitpro.org/wiki/Getting_Started) with GBA support
* make sure that `...\devkitPro\msys2\usr\bin` is on your path, and that `which make` both works and returns `/opt/devkitpro/msys2/usr/bin/make`
* cross your fingers and run `make` in the directory that this readme is in
* it should spit out a `.gba` file - pop that in an emulator! these all worked for me:
    * [mGBA](https://mgba.io/)
    * [no$gba](https://www.nogba.com/)
    * [online gba](https://gba.js.org/player#-DEBUG-hello) *select the rom from File->Game, and press Play*


custom tools:
-------------

### fnt2c.py
Reads a simple font definition file and emits `.h` and `.s` files containing mapping table from ascii -> glyph index

### gpl2c.py
Reads a GIMP palette and emits `.h`/`.c` files containing the palette data in GBA-friendly format

### trigtables.py
Generates trig lookup tables

### xpand.py
Simple template/variable replacement tool *(used to emit a header with constant values that are defined in the Makefile)*

### trax/mktrax.py
Tracker editor supporting live update:
1. start mGBA
2. from Tools->Scripting, load trax/mktrax_server.lua
3. run mktrax.py
4. load / edit .trx file
5. hit `live` button and wait for initial sync
6. enjoy live music editing & playback experience. don't forget to save your music when you're happy with it.


refs:
-----

### general
* tonc *(classic GBA docs/tutorial/guide)*: https://www.coranac.com/projects/tonc/
* libgba source: https://github.com/devkitPro/libgba/tree/master


### audio
* audio advance - decent docs with working sample code: http://belogic.com/gba/index.php
* tonc audio: https://www.coranac.com/tonc/text/sndsqr.htm
* gbatek / audio: https://problemkaputt.github.io/gbatek.htm#gbasoundcontroller
* good details on some audio regs: https://badd10de.dev/notes/gba-programming.html
* GBSOUND.txt - original GB hardware info: http://www.devrs.com/gb/files/hosted/GBSOUND.txt
* mostly repeated from audio advance: https://gbadev.net/gbadoc/audio/introduction.html

* bios sound function deets: http://www.problemkaputt.de/gbatek-bios-sound-functions.htm


### gfx
* tonc: https://www.coranac.com/tonc/text/bitmaps.htm
* gbadoc gfx: https://gbadev.net/gbadoc/graphics.html
* tonc transforms page: https://www.coranac.com/tonc/text/affine.htm
* cowbite emu docs with lots of details: https://www.cs.rit.edu/~tjh8300/CowBite/CowBiteSpec.htm


### build
* grit docs: https://www.coranac.com/man/grit/html/grit.htm
* https://www.coranac.com/tonc/text/bitmaps.htm


