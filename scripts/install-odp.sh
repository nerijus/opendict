#!/bin/bash

# OpenDict Plugin installation helper script
# Copyright (c) 2005 Martynas Jocius <mjoc at akl.lt>
#
# With this script one can install OpenDict plugins without using
# OpenDict itself. This may be handy for installing plugins from
# scripts or other automatic method.

PLUGINDIR=/home/`id -un`/.opendict/plugins

if [ ! $1 ]
then
    echo "OpenDict plugin installation helper"
    echo "Copyright (c) 2005 Martynas Jocius <mjoc at akl.lt>"
    echo
    echo "Usage: $0 <plugin> [--global]"
    echo
    echo "   --global          Install plugin globally to /usr/share/opendict"
    exit 1
fi

if [ ! -e $1 ]
then
    echo "Error: File '$1' does not exist"
    exit 1
fi


if [[ $2 = "--global" ]]
then
    if [[ ! `id -u` = '0' ]]
    then
	echo "Error: You must be root (system administrator)" \
             "to install globally"
        exit 1
    fi

    PLUGINDIR=/usr/share/opendict/plugins
fi

mkdir -p $PLUGINDIR/$1
unzip -d $PLUGINDIR/$1 $1

echo "Done."
