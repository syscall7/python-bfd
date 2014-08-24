#!/bin/bash
# ------------------------------------------------------------------------------
# File: build_bfd.sh
# Description: Build BFD library for ALL targets
# Usage: ./build_bfd.sh
# 
# ------------------------------------------------------------------------------

BINUTILS_FULL=binutils-2.24.tar.bz2
BINUTILS_DIR=binutils-2.24
PREFIX=/usr/local

patch_bfd()
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
        echo "Failed to apply patch"
        exit 1
    fi
}


build()
{

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

    #echo "Patching $BINUTILS_FULL"
    #patch_bfd
}

# if the source directory doesn't exist, assume we need to download it
if [ ! -d "$BINUTILS_DIR" ]; then
    get_src
fi

# launch each build in background for a parallel build
build

wait

