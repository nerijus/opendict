#!/bin/bash
if [ -f "/usr/bin/festival" ]
then
    if [ ! -f "$HOME/.festivalrc" ]
    then
       touch $HOME/.festivalrc
    fi
    A=`cat $HOME/.festivalrc|grep Parameter|grep Audio_Command|grep paplay`
    if [ "$A" = "" ]
    then
      B=`cat $HOME/.festivalrc|grep Parameter|grep Audio_Method|grep Audio_Command`
      if [ "$B" = "" ]
      then
        C=`cat $HOME/.festivalrc|grep Parameter|grep Audio_Required_Format|grep snd`
        if [ "$C" = "" ]
        then
          echo '(Parameter.set '\''Audio_Command "paplay $FILE")' >> $HOME/.festivalrc
          echo '(Parameter.set '\''Audio_Method '\''Audio_Command)' >> $HOME/.festivalrc
          echo '(Parameter.set '\''Audio_Required_Format '\''snd)' >> $HOME/.festivalrc
        fi
      fi
    fi
fi
exec /usr/share/opendict/opendict.py
