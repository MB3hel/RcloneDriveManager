#!/usr/bin/env bash
# BSD 3-Clause License

# Copyright (c) 2022, Marcus Behel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Create Ubuntu package using system libraries

DIR=$(realpath $(dirname "$0"))

pushd "$DIR" > /dev/null

echo "*** Run compile.py before packaging! ***"


echo "Creating directory structure..."
rm -rf build
mkdir -p build/rclone-drive-manager
cd build/rclone-drive-manager
mkdir -p usr/share/applications/
mkdir -p usr/lib/rclone-drive-manager/
mkdir -p usr/share/doc/rclone-drive-manager/
mkdir -p DEBIAN

cp ../../../LICENSE usr/share/doc/rclone-drive-manager/copyright
cp -r ../../../src/*.py usr/lib/rclone-drive-manager/
cp ../../start.sh usr/lib/rclone-drive-manager/
chmod 755 usr/lib/rclone-drive-manager/start.sh
cp ../../rclone-drive-manager.desktop usr/share/applications/
chmod 755 usr/share/applications/rclone-drive-manager.desktop
cp ../../../res/icon.png usr/lib/rclone-drive-manager/
cp ../../deb_control DEBIAN/control
chmod 755 DEBIAN/control


echo "Making deb package..."
cd ..
dpkg-deb --build rclone-drive-manager

popd > /dev/null
