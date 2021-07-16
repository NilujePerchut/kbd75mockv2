# Dirs
BUILD_DIR := $(CURDIR)/build
SRC_DIR := $(CURDIR)/src
RCS_DIR := $(CURDIR)/rcs

# Tools
NETLIST_GEN := $(SRC_DIR)/netlist_gen.py

# Objs
JSON := $(RCS_DIR)/v2.json
NETLIST := $(BUILD_DIR)/kdbd75_mock.netlist

# Rules
$(NETLIST): $(NETLIST_GEN) $(JSON) | $(BUILD_DIR) 
	$(NETLIST_GEN) $(JSON) $@

$(BUILD_DIR):
	mkdir -p $@