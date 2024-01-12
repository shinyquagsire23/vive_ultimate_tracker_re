#!/bin/zsh
adb shell rm -rf /data/lambda/ 
adb shell mkdir -p /data/lambda/
adb shell rm -rf /data/mapdata
adb shell mkdir /data/mapdata