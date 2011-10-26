#!/bin/bash
# ------------------------------------------------------------------------------
# File: build_binutils.sh
# Description: Build binutils for mutliple target platforms in parallel
# Usage: ./build_binutils.sh
# 
# ------------------------------------------------------------------------------

BINUTILS_FULL=binutils-2.21.1a.tar.bz2
BINUTILS_DIR=binutils-2.21.1
PREFIX=/usr/local

TARGETS="
	mips-elf
	arm-elf
	i686-elf
	ppc-elf
"

# Texas Instruments targets
    #tic30-elf
    #tic4x-elf
    #tic54x-elf
    #tic6x-elf
    #tic80-elf

build()
{
	echo "Building $1"
	mkdir -p "./build/$1-build"
	cd "./build/$1-build"
	echo "Configuring $1"
	../../$BINUTILS_DIR/configure --target=$1 --prefix="$PREFIX" > /dev/null
	echo "Making $1"
	make > /dev/null
	echo "Installing $1"
	sudo make install > /dev/null
	echo "Done building $1"
}

# download and extract the binutils source
get_src()
{
    echo "Downloading $BINUTILS_FULL"
    wget http://ftp.gnu.org/gnu/binutils/$BINUTILS_FULL

    echo "Extracting $BINUTILS_FULL"
    tar -xjf $BINUTILS_FULL
}

# if the source directory doesn't exist, assume we need to download it
if [ ! -d "$BINUTILS_DIR" ]; then
    get_src
fi

# for each target platform
for target in $TARGETS
do
    # launch each build in background for a parallel build
	build $target &
done
wait
