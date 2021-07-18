# Libs
KICAD_LIBS := "/usr/share/kicad/library"
KICAD_MODS := /usr/share/kicad/modules
KICAD_PRJ_LIBS ?= /home/niluje/Work_local/kicad_libs

# Dirs
BUILD_DIR := $(CURDIR)/build
SRC_DIR := $(CURDIR)/src
RCS_DIR := $(CURDIR)/rcs
UNITS_DIR := $(CURDIR)/units
PYTHONPATH := $(KICAD_PRJ_LIBS):$(CURDIR)

# Unit tests
UNITS_SRC := $(wildcard $(UNITS_DIR)/*.py)
UNITS_NETS := $(addprefix $(BUILD_DIR)/,$(notdir $(patsubst %.py,%.net,$(UNITS_SRC))))
UNITS_PCB := $(patsubst %.net,%.kicad_pcb,$(UNITS_NETS))

# Objs
JSON := $(RCS_DIR)/v2.json
NETLIST := $(BUILD_DIR)/kbd75_mock.net
UNITS := $(UNITS_PCB)

# Rules
.PRECIOUS: $(UNITS_NETS)

all: $(UNITS) $(NETLIST)

clean:
	rm -rf $(BUILD_DIR)

$(BUILD_DIR)/%.kicad_pcb: $(BUILD_DIR)/%.net
	@echo building $@ from $<
	@# SKIDL is generating log, erc and net files in the
	@# top-level dir. So launch it from the build dir
	( export KIPRJMOD=$(KICAD_PRJ_LIBS) && \
	  export KISYSMOD=$(KICAD_MODS) && \
	  python $(KICAD_PRJ_LIBS)/kinet2pcb.py -d7 -w -nb --input $< --output $@ \
	)

$(BUILD_DIR)/%.net: $(UNITS_DIR)/%.py | $(BUILD_DIR) 
	@echo building $@ from $<
	@# SKIDL is generating log, erc and net files in the
	@# top-level dir. So launch it from the build dir
	( export KICAD_SYMBOL_DIR=$(KICAD_LIBS) && \
	  export KIPRJLIB=$(KICAD_PRJ_LIBS) && \
	  export PYTHONPATH=$(PYTHONPATH) && \
	  cd $(BUILD_DIR) && $<)

$(BUILD_DIR)/%.net: $(SRC_DIR)/%.py $(JSON) | $(BUILD_DIR) 
	@echo building $@ from $<
	@# SKIDL is generating log, erc and net files in the
	@# top-level dir. So launch it from the build dir
	( export KICAD_SYMBOL_DIR=$(KICAD_LIBS) && \
	  export KIPRJLIB=$(KICAD_PRJ_LIBS) && \
	  export PYTHONPATH=$(PYTHONPATH) && \
	  cd $(BUILD_DIR) && $< $(JSON))

$(BUILD_DIR):
	mkdir -p $@