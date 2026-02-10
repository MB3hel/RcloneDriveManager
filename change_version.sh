#!/usr/bin/env bash

if [ $# -ne 1 ]; then
    echo "Usage: change_version.sh version"
    exit 1
fi

VERSION="$1"

cd "$(dirname "$(realpath "$0")")"
printf "$VERSION" > res/version.txt
sed -i "s/Version:.*/Version: $VERSION/g" packaging/deb_control
sed -i "s/Version:.*/Version:    $VERSION/g" packaging/rpm.spec

