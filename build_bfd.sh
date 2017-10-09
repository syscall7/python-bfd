#!/bin/bash
# ------------------------------------------------------------------------------
# File: build_bfd.sh
# Description: Build BFD library for ALL targets
# Usage: ./build_bfd.sh
# 
# ------------------------------------------------------------------------------

# This is the URL for actual releases
#BINTUILS_URL=http://ftp.gnu.org/gnu/binutils

# This is the URL for snapshots, which we have to use to get some bug fixes
BINUTILS_URL=ftp://sourceware.org/pub/binutils/snapshots

# The full name of binutils
BINUTILS_FULL=binutils-2.24.51.tar.bz2

# The local directory to use
BINUTILS_DIR=binutils-2.24.51

# Where to install
PREFIX=/usr/local/oda

patch_bfd_format()
{
    patch --verbose -u -p0 << HERE_DOC
diff -ur binutils-2.23.1/bfd/format.c binutils-2.23.1-patched/bfd/format.c
--- binutils-2.23.1/bfd/format.c    2011-06-05 21:26:01.000000000 -0400
+++ binutils-2.23.1-patched/bfd/format.c    2013-08-06 22:18:05.935550856 -0400
@@ -278,6 +278,7 @@
    }
     }

+#if 0
   if (match_count > 1)
     {
       const bfd_target * const *assoc = bfd_associated_vector;
@@ -297,6 +298,7 @@
        }
    }
     }
+#endif

   if (match_count == 1)
     {
HERE_DOC

    if [[ $? -ne 0 ]]; then
        echo "Don't worry: Anthony needs to port this patch to binutils-2.24"
        exit 1
    fi
}

patch_bfd_lime()
{
    pushd $BINUTILS_DIR

    patch --verbose -u -p1 < ../bfd_lime.patch

    if [[ $? -ne 0 ]]; then
        echo "Failed to apply lime patch"
        exit 1
    fi

    popd
}


build()
{
    if [ -d $PREFIX ]; then
      # Clear out any pre-existing versions
      sudo rm -rf $PREFIX/*
    fi

    mkdir -p "./build-$BINUTILS_FULL"
    cd "./build-$BINUTILS_FULL"

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
    ../../$BINUTILS_DIR/libiberty/configure --prefix="$PREFIX" --enable-install-libiberty=yes > ../liberty_config.log
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
    wget -N $BINUTILS_URL/$BINUTILS_FULL

    echo "Extracting $BINUTILS_FULL"
    tar -xjf $BINUTILS_FULL

    # TODO: Port this to binutils-2.24
    #echo "Applying the bfd format patch to $BINUTILS_FULL"
    #patch_bfd_format

    echo "Applying the bfd lime patch to $BINUTILS_FULL"
    patch_bfd_lime
}

if [ ! -d "$BINUTILS_DIR" ]; then
   get_src
fi

# launch each build in background for a parallel build
build

wait

