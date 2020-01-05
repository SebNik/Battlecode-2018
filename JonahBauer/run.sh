#!/bin/sh
# This file should build and run your code.
# It will run if you're in nodocker mode on Mac or Linux,
# or if you're running in docker.

# Run our code.
echo java -Xmx40M -cp ./:../battlecode/java/ com.jonahbauer.Player
java -Xmx40M -cp ./:../battlecode/java/ com.jonahbauer.Player
