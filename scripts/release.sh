#!/bin/sh

#
# Easy releasy script. Use before releasing software.
#

NAME=$1
INDIR=$2
OUTDIR=$3

if [[ $NAME == "" ]] || [[ $INDIR == "" ]]; then
    echo "Usage: $0 <release name> <source dir> <tmp dir>"
    exit 1;
fi

if [[ $UID != "0" ]]; then
    echo "You should be root (or modify this script to avoid root :)"
    exit 1;
fi

cd $INDIR && make clean

rm -rf "$OUTDIR/$NAME*"
cp -r "$INDIR" "$OUTDIR/$NAME"

cd $OUTDIR
rm -rf $NAME.zip
rm -rf $NAME.tar.gz

for f in `find "$NAME" -name ".svn"`; do echo Removing "$f" && rm -rf "$f"; done;

zip -r "$NAME.zip" "$NAME"
tar -cf "$NAME.tar" "$NAME"
gzip "$NAME.tar"

echo
echo "Release files created. Do not forget to create SVN TAG when tested."
