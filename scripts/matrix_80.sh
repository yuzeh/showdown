#!/usr/bin/env sh

i=$1
j=$2

case "$j" in
  1) loadout=1_coverage ;;
  2) loadout=2_psyspam ;;
  3) loadout=3_trickroom ;;
  *) echo "Unknown loadout '$j', bailing"; exit 1 ;;
esac

export WEBSOCKET_URI=homebase.yuzeh.com:8000
export PS_USERNAME=abut-shipful-$i-$j
export BOT_MODE=SEARCH_LADDER
export POKEMON_MODE=gen7ouc${i}v${j}
export TEAM_NAME=${loadout}_80
export RUN_COUNT=200

python run.py
