#!/usr/bin/zsh

# Just define some usefull paths and env vars

printf "Setting up the environnement\n"

export NILUJE_KICAD_LIBS=$(realpath kicad_libs)

printf "NILUJE_KICAD_LIBS: %s\n" $NILUJE_KICAD_LIBS
