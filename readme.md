# KBD75mockV2

![The PCB](/doc/pictures/PCB_top.jpg)


An open-source KBD75V2 alternative PCB with the following features:
- STM32F103 microcontroller
- Per-Key RGB backlight (SK6812MINI-E)
- 16 RGB backlight LEDs (compatible with offical foam hole location)
- USB-C connector
- AINSI & ISO layouts
- Alternate layout for spacebar right side keys
- Mechanicaly compatible with the KBDFans KBD75V2 case
- Also compatible with the YMDK84 case (tested with acrylic case)
- QMK compatible (see [qmk firmware support](https://github.com/NilujePerchut/qmk_firmware/tree/kbd75mockv2))
- JLCPCB friendly workflow:
    - Complies with JLCPCB design rules
    - Uses component available at JLCPCB SMT part

## Disclamers
I am not affiliated in any way with the KBDFans corporation. This is NOT a KBDFans product.

This design comes with no warranty at all. See LICENSE file for more details.

# Status
Rev A0 prototype assembled and functionnal.
See Bug section below for more details.

## RevA0 Bugs
- Some fixing holes are not aligned with official KBD75V2 case inserts.
- Missing one RGB backlight led on each lateral side. This creates a hole in the surrounding ring.

## Usage

Be sure to understand the [Status](#status) and [Bugs](reva0-bugs) sections before investing money in such project.

```
git clone --recurse-submodules https://github.com/NilujePerchut/kbd75mockv2
```
_Note:_ This project uses [skidl](https://github.com/devbisme/skidl) to produce a netlist instead of using a regular schematics editor. It also relies on some automatic routing via python scripts for repetitive placement and routing tasks. The PCB is then completed by hand using kicad's pcbnew.

### PCB manufaturing & assembly
Open the [Routed PCB](hard/pcb/final_pcb/kbd75mock_v2_routed.kicad_pcb) with kicad and generate the GERBER files.

All relevant footprints have a _JLCC_ field with JLCPCB SMT command code. This can be used to generate JLCPCB assembly request.

### Configuration
If you need the per-key RGB backlight feature, make a solder joint between pins 1 and 2 of P3.

### QMK firmware

All related files are located in the [qmk_firmware](qmk_firmware) directory.

The compilation and flashing steps use the convenient `qmk` cli tool provided by qmk_firmware. See [QMK cli](https://docs.qmk.fm/#/cli) for more details. 

## Bootloader installation
This board uses the standard stm32duino bootloader. The SWD P2 connector to flash it using your prefered method (tested with an STLINKV2 clone).

## Compilation
```
cd qmk_firmware
qmk compile -km default -kb kbd75mockv2
```

## Flashing
```
qmk flash -km default -kb kbd75mockv2
```

_WARNING_: Default RGB MATRIX (per key LEDs) max brightness is set to 0x100. This value causes the whole PCB (including RGB backlight) to drain around 400mA on the USB bus.This represents more than 2W of power consumption and clearly heats the whole structure. You might want to lower this value to lower heat dissipation.

## RevA1 TODO
- [ ] Rework PCB routing to enhance performances
- [ ] Fix location of mechanical fixing holes
- [ ] Move backlight RGB LEDs to be compliant with official foam
- [ ] Add one more RGB backlight LED one each lateral side
- [ ] (if possible) Add split backspace option
- [ ] (if possible) Add alternate tab key option
- [ ] (if possible) Add split spacebar option

## Galerie

![KBD75V2 Plate](/doc/pictures/zelios.jpg)

![YMDK84 case](/doc/pictures/unicorn.jpg)

![KBD75V2 case](/doc/pictures/kbd75v2.jpeg)

## Credits & Thanks
- Benoit, Tor-Rolf, Damien & Pascale for the precious help
- [KBDFans](https://kbdfans.com/)
- [QMK](https://qmk.fm/)
- [SKIDL](https://github.com/devbisme/skidl)
- [Kicad]