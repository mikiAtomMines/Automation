#!/bin/bash

<< comment

Sebastian Miki-Silva
miki@atommines.com

Run this file right after flashing a BeagleBone Black rev C to set it up for use as a pid temperature controller with
the Automation python library. Will install all required prerequisites. This was tested using Debian 10.12. Might not
work as expected in other versions, depending on what comes preinstalled with the OS.

This file runs the installation steps in steps.sh. Some installation steps require a user input to answer some prompts
like "Do you want to continue? [Y/n]" or "[sudo] password for debian:". To answer the prompts automatically, the
contents of the file prompts.txt are given as answers.
comment

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
/bin/bash $DIR/lib/steps.sh < $DIR/lib/prompts.txt