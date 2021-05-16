#!/usr/bin/env bash

declare -a maps=( \
    "Exodus" \
    "Cashews" \
    "Island of Mystery" \
    "Pure Hate" \
    "Fortress of Damnation" \
    "Trifling" \
    "Simply Dead" \
    "Tingsryd" \
    "Core Annihilation" \
    "Total Recall" \
    "Warborn" \
    "Damnation" \
    "Unleash the Fire" \
    "Damned Legion" \
    "Doomherolandia" \
    "Twobox" \
    "Electric Wizard" \
    "Last Cup of Sorrow" \
    "Split Wide Open" \
    "True Grit" \
    "Walk With Me in Hell" \
    "Royale Arena" \
    "Castle Lava" \
    "Bane's Atrium" \
    "Fourtress" \
    "Crimson" \
    "Decimal Error" \
    "Slaughterstein" \
    "Degrassi" \
    "Anathema" \
    "sworf" \
    "Brookhaven Hospital" \
    "BoomTown" \
    "Hard Contact" \
    "KSP" \
)

rm csv
map_num=1
for map in "${maps[@]}"
do
    printf "Slaugherfest 2012,DOOM2.WAD,SF2012_final.wad,2,2013-07-30,Episode 1,1,%s,%d,%d,false\n" \
        "$map" $map_num $map_num >> csv
    ((map_num++))
done
