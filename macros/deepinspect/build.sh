#!/bin/sh

javac -classpath /opt/android-sdk-linux/platforms/android-16/android.jar DeepInspect.java
/opt/android-sdk-linux/platform-tools/dx --dex --output=DeepInspect.apk DeepInspect.class
