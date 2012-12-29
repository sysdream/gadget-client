#!/bin/sh

SDK=/opt/android-sdk-linux

javac -classpath $SDK/platforms/android-16/android.jar DeepInspect.java
$SDK/platform-tools/dx --dex --output=DeepInspect.apk DeepInspect.class
