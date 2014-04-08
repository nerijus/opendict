#!/bin/bash
if [ -f "/usr/bin/festival" ]
then
    if [ ! -f "$HOME/.festivalrc" ]
    then
       touch $HOME/.festivalrc
    fi
    A=`cat $HOME/.festivalrc|grep opendict_settings`
    if [ "$A" = "" ]
    then
      echo '#opendict_settings' >> $HOME/.festivalrc
      echo '(Parameter.set '\''Audio_Command "paplay $FILE")' >> $HOME/.festivalrc
      echo '(Parameter.set '\''Audio_Method '\''Audio_Command)' >> $HOME/.festivalrc
      echo '(Parameter.set '\''Audio_Required_Format '\''snd)' >> $HOME/.festivalrc
    fi
fi
exec /usr/share/opendict/opendict.py
