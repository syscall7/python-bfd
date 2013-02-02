#!/bin/bash
# ------------------------------------------------------------------------------
# File: build_bfd.sh
# Description: Build BFD library for ALL targets
# Usage: ./build_bfd.sh
# 
# ------------------------------------------------------------------------------

BINUTILS_FULL=binutils-2.22.tar.bz2
BINUTILS_DIR=binutils-2.22
PREFIX=/usr/local/oda

build()
{

    mkdir -p "./build"
    cd "./build"

    export CPPFLAGS="-fPIC"

    mkdir -p "./bfd"
    cd "./bfd"
    echo "Configuring bfd"
    ../../$BINUTILS_DIR/bfd/configure --enable-targets=all --enable-64-bit-bfd --disable-nls --prefix="$PREFIX" > ../bfd_config.log
    echo "Making bfd"
    make > ../bfd_make.log
    echo "Installing bfd"
    sudo make install > ../bfd_install.log
    cd ".."

    export CPPFLAGS="$CPPFLAGS -I`pwd`/libbfd"
    mkdir -p "./libiberty"
    cd "./libiberty"
    echo "Configuring libiberty"
    ../../$BINUTILS_DIR/libiberty/configure --prefix="$PREFIX" > ../liberty_config.log
    echo "Making libiberty"
    make > ../liberty_make.log
    echo "Installing libiberty"
    sudo make install > ../liberty_install.log
    cd ".."

    mkdir -p "./libopcodes"
    cd "./libopcodes"
    echo "Configuring libopcodes"
    ../../$BINUTILS_DIR/opcodes/configure --enable-targets=all --prefix="$PREFIX" > ../opcodes_config.log
    echo "Making libopcodes"
    make > ../opcodes_make.log
    echo "Installing libopcdoes"
    sudo make install > ../opcodes_install.log
    cd ".."
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

# launch each build in background for a parallel build
build

wait

