#---------------------------------------------------------------------------------
.SUFFIXES:
#---------------------------------------------------------------------------------

ifeq ($(strip $(DEVKITARM)),)
$(error "Please set DEVKITARM in your environment. export DEVKITARM=<path to>devkitARM")
endif

include $(DEVKITARM)/gba_rules

#  raw\art\bg_gradient.png -o source/gen/bg_gradient 

#---------------------------------------------------------------------------------
# TARGET is the name of the output
# BUILD is the directory where object files & intermediate files will be placed
# SOURCES is a list of directories containing source code
# INCLUDES is a list of directories containing extra header files
# DATA is a list of directories containing binary data
# GRAPHICS is a list of directories containing files to be processed by grit
#
# All directories are specified relative to the project directory where
# the makefile is found
#
#---------------------------------------------------------------------------------
TARGET		:= $(notdir $(CURDIR))
BUILD		:= build
SOURCES		:= source
INCLUDES	:= include build
DATA		:=
MUSIC		:=

GENDIR	:= source/gen

#---------------------------------------------------------------------------------
# options for code generation
#---------------------------------------------------------------------------------
ARCH	:=	-mthumb -mthumb-interwork

CFLAGS	:=	-Wall -Werror -O2\
		-mcpu=arm7tdmi -mtune=arm7tdmi\
		$(ARCH)

CFLAGS	+=	$(INCLUDE)

CXXFLAGS	:=	$(CFLAGS) -fno-rtti -fno-exceptions

ASFLAGS	:=	-g $(ARCH)
LDFLAGS	=	-g $(ARCH) -Wl,-Map,$(notdir $*.map)

#---------------------------------------------------------------------------------
# any extra libraries we wish to link with the project
#---------------------------------------------------------------------------------
LIBS	:= -lmm -lgba


#---------------------------------------------------------------------------------
# list of directories containing libraries, this must be the top level containing
# include and lib
#---------------------------------------------------------------------------------
LIBDIRS	:=	$(LIBGBA)

#---------------------------------------------------------------------------------
# no real need to edit anything past this point unless you need to add additional
# rules for different file extensions
#---------------------------------------------------------------------------------


ifneq ($(BUILD),$(notdir $(CURDIR)))

#---------------------------------------------------------------------------------
# gfx defs
MAX_UI_TILES		:= 512
MAX_SPRITE_TILES	:= 512
GFX_DEFS			:= -Dmax_ui_tiles=$(MAX_UI_TILES) -Dmax_sprite_tiles=$(MAX_SPRITE_TILES)
GFX_DEF_TEMPL		:= raw/template/gfx_defs.templ.h
GFX_DEF_H			:= source/gen/$(subst .templ,,$(notdir $(GFX_DEF_TEMPL)))

#---------------------------------------------------------------------------------

PALDIR		:= raw/art
PALETTES	:= $(wildcard $(PALDIR)/*.gpl)
PALCFILES	:= $(subst $(PALDIR),gen,$(subst .gpl,.c,$(PALETTES)))

FNTDIR		:= raw/art
FONTS		:= $(wildcard $(FNTDIR)/*.fnt)
FONTSFILES	:= $(subst $(FNTDIR),gen,$(subst .fnt,.s,$(FONTS)))

.SUFFIXES += .gpl

GRIT				:= $(DEVKITPRO)/tools/bin/grit.exe
GRIT_BG_FLAGS		:= -gB 4 -mRtf4 -p! -fa
GRIT_SPRITE_FLAGS	:= -gB 4 -m! -p!


TRIGCFILES	:= gen/trig.c

UI_SHARED	:= GFX_UI
UI_PNGDIR	:= raw/art/export/main_ui
UI_PNGLIST	:= $(shell cat ${UI_PNGDIR}/manifest.txt)
UI_PNGFILES	:= $(foreach png,$(UI_PNGLIST),$(UI_PNGDIR)/$(png))
UI_SFILE	:= gen/$(UI_SHARED).s

SPRITE_PNGDIR	:=	raw/art/export/sprites
SPRITE_PNGLIST	:=	SPR_guy.png
SPRITE_PNGFILES	:=	$(foreach png,$(SPRITE_PNGLIST),$(SPRITE_PNGDIR)/$(png))
SPRITE_SFILES	:=	$(foreach png,$(SPRITE_PNGLIST),gen/$(subst .png,.s,$(png)))


#---------------------------------------------------------------------------------

export OUTPUT	:=	$(CURDIR)/$(TARGET)

export VPATH	:=	$(foreach dir,$(SOURCES),$(CURDIR)/$(dir)) \
			$(foreach dir,$(DATA),$(CURDIR)/$(dir)) \
			$(foreach dir,$(GRAPHICS),$(CURDIR)/$(dir))

export DEPSDIR	:=	$(CURDIR)/$(BUILD)

DATAFILES	:= $(UI_PNGFILES)

CFILES		:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.c)))
CFILES		+=	$(PALCFILES) $(TRIGCFILES)
CPPFILES	:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.cpp)))
SFILES		:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.s)))
SFILES		+=	$(UI_SFILE) $(FONTSFILES) $(SPRITE_SFILES)
BINFILES	:=	$(foreach dir,$(DATA),$(notdir $(wildcard $(dir)/*.*)))

GENFILES	:= $(foreach cfile,$(PALCFILES),source/$(cfile))
GENFILES	+= $(GENDIR)/$(UI_SHARED).s
GENFILES	+= $(foreach cfile,$(TRIGCFILES),source/$(cfile))
GENFILES	+= $(foreach sfile,$(FONTSFILES),source/$(sfile))
GENFILES	+= $(foreach sfile,$(SPRITE_SFILES),source/$(sfile))
GENFILES	+= $(GFX_DEF_H)

XTRATOOLS	:= $(GRIT) $(wildcard tools/*.py)

ifneq ($(strip $(MUSIC)),)
	export AUDIOFILES	:=	$(foreach dir,$(notdir $(wildcard $(MUSIC)/*.*)),$(CURDIR)/$(MUSIC)/$(dir))
	BINFILES += soundbank.bin
endif

#---------------------------------------------------------------------------------
# use CXX for linking C++ projects, CC for standard C
#---------------------------------------------------------------------------------
ifeq ($(strip $(CPPFILES)),)
#---------------------------------------------------------------------------------
	export LD	:=	$(CC)
#---------------------------------------------------------------------------------
else
#---------------------------------------------------------------------------------
	export LD	:=	$(CXX)
#---------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------

export OFILES_BIN := $(addsuffix .o,$(BINFILES))

export OFILES_SOURCES := $(CPPFILES:.cpp=.o) $(CFILES:.c=.o) $(SFILES:.s=.o)

export OFILES := $(OFILES_BIN) $(OFILES_SOURCES)

export BIN_HFILES := $(addsuffix .h,$(subst .,_,$(BINFILES)))

export INCLUDE	:=	$(foreach dir,$(INCLUDES),-iquote $(CURDIR)/$(dir)) \
					$(foreach dir,$(LIBDIRS),-I$(dir)/include) \
					-I$(CURDIR)/$(BUILD)

export LIBPATHS	:=	$(foreach dir,$(LIBDIRS),-L$(dir)/lib)

.PHONY: $(BUILD) clean gen

#---------------------------------------------------------------------------------
# entry point - jumps into build/ and re-runs this makefile, dropping into the second part below
$(BUILD): $(GENFILES) Makefile $(XTRATOOLS) $(DATAFILES)
	@echo all generated deps: $(GENFILES)
	@echo all extra tools: $(XTRATOOLS)
	@echo all object files: $(OFILES)
	@[ -d $@ ] || mkdir -p $@
	@[ -d $@/gen ] || mkdir -p $@/gen
	@$(MAKE) --no-print-directory -C $(BUILD) -f $(CURDIR)/Makefile

gen: $(GENFILES) Makefile $(XTRATOOLS) $(DATAFILES)
	@echo all data files: $(DATAFILES)
	@echo all generated deps: $(GENFILES)
	@echo generating...

#---------------------------------------------------------------------------------
clean:
	@echo clean ...
	@rm -fr $(BUILD) $(TARGET).elf $(TARGET).gba $(GENDIR)


#####-----------------------------------------------------------------------------
##### molen rules lol
#####

# palette files
$(GENDIR)/%.c $(GENDIR)/%.h: $(PALDIR)/%.gpl tools/gpl2c.py
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	python tools/gpl2c.py -o $@ $<

# font files
$(GENDIR)/%.s $(GENDIR)/%.h: $(FNTDIR)/%.fnt tools/fnt2c.py
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	python tools/fnt2c.py -o $@ $<

# ui files
$(GENDIR)/$(UI_SHARED).s $(GENDIR)/$(UI_SHARED).h: $(UI_PNGFILES)
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	$(GRIT) $^ $(GRIT_BG_FLAGS) -W£ -fx $(UI_SHARED).png -o $(GENDIR)/$(UI_SHARED)

# sprite files
$(GENDIR)/%.s $(GENDIR)/%.h: $(SPRITE_PNGDIR)/%.png
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	$(GRIT) $^ $(GRIT_SPRITE_FLAGS) -o $(subst .s,,$@)

# trig lookups
$(GENDIR)/trig.c $(GENDIR)/trig.h: tools/trigtables.py
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	python $< -o $@

# gfx defs
$(GFX_DEF_H): $(GFX_DEF_TEMPL) Makefile
	@[ -d $(dir $@) ] || mkdir -p $(dir $@)
	python tools/xpand.py -o $@ $< $(GFX_DEFS)


#---------------------------------------------------------------------------------



#---------------------------------------------------------------------------------
else  ##### this part is run by the $(BUILD) target above from within the build/ folder

#---------------------------------------------------------------------------------
# main targets
#---------------------------------------------------------------------------------

$(OUTPUT).gba	:	$(OUTPUT).elf

$(OUTPUT).elf	:	$(OFILES)

$(OFILES_SOURCES) : $(BIN_HFILES)

#---------------------------------------------------------------------------------
# The bin2o rule should be copied and modified
# for each extension used in the data directories
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# rule to build soundbank from music files
#---------------------------------------------------------------------------------
soundbank.bin soundbank.h : $(AUDIOFILES)
	@mmutil $^ -osoundbank.bin -hsoundbank.h

#---------------------------------------------------------------------------------
# This rule links in binary data with the .bin extension
#---------------------------------------------------------------------------------
%.bin.o	%_bin.h :	%.bin
	@echo $(notdir $<)
	@$(bin2o)


# NB. missing build/gen folder, but that's probably ok?
-include $(DEPSDIR)/*.d
#---------------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------------
