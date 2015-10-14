#!/bin/bash -e
# ------------------------------------------------------------------------------
# File: build.sh
# Description: ODA script to build the Python wrapper for Snowman
# ------------------------------------------------------------------------------

# assumes Cython and pydev are already installed
# install snowman dependencies
sudo apt-get install cmake libboost-dev qt5-default qt-sdk 

# version of snowman we are using
VERSION=0.0.8

# download snowman source
wget https://github.com/yegord/snowman/archive/v${VERSION}.zip

# extract source
unzip v${VERSION}.zip

# copy our pysnowman wrapper into the Snowman source tree
cp -R pysnowman ./snowman-$VERSION/src/

# apply ODA patch (generated with diff -u)
# NOTE: The patch turns on position independent code so we can build a shared
#       library and adds our pysnowman module to the build.
patch --verbose -u -d snowman-${VERSION}/src/ <<HERE_DOC
--- snowman-0.0.8/src/CMakeLists.txt	2015-09-15 12:50:58.000000000 -0400
+++ snowman-0.0.8-patched/src/CMakeLists.txt	2015-10-13 22:29:32.821880122 -0400
@@ -3,6 +3,9 @@
 
 enable_testing()
 
+set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")
+set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
+
 # Show what's going on when running make.
 #set(CMAKE_VERBOSE_MAKEFILE ON)
 
@@ -169,6 +172,7 @@
 
 add_subdirectory(nc)
 add_subdirectory(nocode)
+add_subdirectory(pysnowman)
 add_subdirectory(snowman)
 if(${IDA_PLUGIN_ENABLED})
     add_subdirectory(ida-plugin)
HERE_DOC

# create separate build directory for snowman
mkdir snowman-${VERSION}/build
cd snowman-${VERSION}/build

# build snowman and our pysnowman wrapper
# NOTE: For debug use cmake -D CMAKE_BUILD_TYPE=Debug ../src
cmake ../src
cmake --build .

# install the ODA pysnowman shared library 
sudo cp ./pysnowman/libpysnowman.so /usr/lib/

# build the snowman python module
cd -
sudo python setup.py build install
