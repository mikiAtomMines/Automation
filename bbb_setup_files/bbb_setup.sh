#!/bin/bash

<< comment

Sebastian Miki-Silva
miki@atommines.com

Run this file right after flashing a BeagleBone Black rev C to set it up for use as a pid temperature controller with
the Automation python library. Will install all required prerequisites. This was tested using Debian 10.3. Might not
work as expected in other versions, depending on what comes preinstalled with the OS.

comment

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
/bin/bash $DIR/lib/steps.sh < $DIR/lib/prompts.txt