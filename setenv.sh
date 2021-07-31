#!/usr/bin/zsh

# Just a script to ensure portability over osdemammouth and osdegirouette
# For other platform, just define the env variables before calling the script

printf "Setting up the environnement\n"

host=`hostname`

if [ "$host" = "osdemammouth" ] ; then
	printf "osdemammouth detected\n"
	export NILUJE_KICAD_LIBS=/home/niluje/Work_local/kicad_libs
elif [ "$host" = "osdegirouette" ] ; then
	printf "osdegirouette detected\n"
	export NILUJE_KICAD_LIBS=/home/niluje/Work/kicad_libs
else
	printf "Unknown host. Using existing env variables"
fi

printf "NILUJE_KICAD_LIBS: %s\n" $NILUJE_KICAD_LIBS 
