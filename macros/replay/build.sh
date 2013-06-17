#!/bin/sh

SDK=/opt/android/sdk

javac -target 1.6 -source 1.6 -classpath $SDK/platforms/android-16/android.jar Replay.java
$SDK/build-tools/17.0.0/dx --dex --output=Replay.apk Replay.class 'Replay$ReplaySlot.class'
