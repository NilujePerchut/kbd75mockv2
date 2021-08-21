# Libs
KICAD_LIBS := "/usr/share/kicad/library"
KICAD_MODS := /usr/share/kicad/modules
NILUJE_KICAD_LIBS ?= /home/niluje/Work_local/kicad_libs  # osdemammouth by default

# Dirs
BUILD_DIR := $(CURDIR)/build
SRC_DIR := $(CURDIR)/src
RCS_DIR := $(CURDIR)/rcs
UNITS_DIR := $(CURDIR)/units
PYTHONPATH := $(NILUJE_KICAD_LIBS):$(CURDIR)

# Tools
PCB_EXPLORER := $(NILUJE_KICAD_LIBS)/pcb_explorer.py

# Unit tests
UNITS_SRC := $(wildcard $(UNITS_DIR)/*.py)
UNITS_NETS := $(addprefix $(BUILD_DIR)/,$(notdir $(patsubst %.py,%.net,$(UNITS_SRC))))
UNITS_PCB := $(patsubst %.net,%.kicad_pcb,$(UNITS_NETS))

# Objs
JSON := $(RCS_DIR)/v2.json
NETLIST := $(BUILD_DIR)/kbd75mock_v2.net
UNITS := $(UNITS_PCB)
PCB := $(BUILD_DIR)/kbd75mock_v2.kicad_pcb
PLACED_PCB := $(BUILD_DIR)/kbd75mock_v2_placed.kicad_pcb
PLACEMENT := $(SRC_DIR)/placement.yaml

# Rules
.PRECIOUS: $(UNITS_NETS) $(NETLIST)
.PHONY: update_placement

all: $(UNITS) $(PCB)

clean:
	rm -rf $(BUILD_DIR)

units: $(UNITS)

pcb: $(PCB)

place: $(PLACED_PCB)

netlist: $(NETLIST)

update_placement: $(PLACEMENT)
	$(PCB_EXPLORER) dump $(PLACED_PCB) > $(PLACEMENT)

$(PLACED_PCB): $(PCB) $(PLACEMENT)
	@echo building $@ from $<
	@# SKIDL is generating log, erc and net files in the
	@# top-level dir. So launch it from the build dir
	( export KICAD_SYMBOL_DIR=$(KICAD_LIBS) && \
	  export KIPRJLIB=$(NILUJE_KICAD_LIBS) && \
	  export PYTHONPATH=$(PYTHONPATH) && \
	  python3 $(SRC_DIR)/place.py $< $@)
	@echo Apply manual placement from $(PLACEMENT)
	$(PCB_EXPLORER) apply $@ $(PLACEMENT) $@


$(BUILD_DIR)/%.kicad_pcb: $(BUILD_DIR)/%.net
	@echo building $@ from $<
	@# SKIDL is generating log, erc and net files in the
	@# top-level dir. So launch it from the build dir
	( export KIPRJMOD=$(NILUJE_KICAD_LIBS) && \
	  export KISYSMOD=$(KICAD_MODS) && \
	  python $(NILUJE_KICAD_LIBS)/kinet2pcb.py -d7 -w -nb --input $< --output $@ && \
	  sed -i 's/page A4/page A3/' $@ \
	)

$(BUILD_DIR)/%.net: $(UNITS_DIR)/%.py | $(BUILD_DIR) 
	@echo building $@ from $<
	@# SKIDL is generating log, erc and net files in the
	@# top-level dir. So launch it from the build dir
	( export KICAD_SYMBOL_DIR=$(KICAD_LIBS) && \
	  export KIPRJLIB=$(NILUJE_KICAD_LIBS) && \
	  export PYTHONPATH=$(PYTHONPATH) && \
	  cd $(BUILD_DIR) && $<)

$(BUILD_DIR)/%.net: $(SRC_DIR)/%.py | $(BUILD_DIR) 
	@echo building $@ from $<
	@# SKIDL is generating log, erc and net files in the
	@# top-level dir. So launch it from the build dir
	( export KICAD_SYMBOL_DIR=$(KICAD_LIBS) && \
	  export KIPRJLIB=$(NILUJE_KICAD_LIBS) && \
	  export PYTHONPATH=$(PYTHONPATH) && \
	  cd $(BUILD_DIR) && $<)

$(BUILD_DIR):
	mkdir -p $@