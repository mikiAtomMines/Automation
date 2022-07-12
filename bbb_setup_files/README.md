#Setup of a BeagleBone Black rev C to be used as a pid controller using the Automation python library. 

Sebastian Miki-Silva \
miki@atommines.com


## Getting the BeagleBone Black ready

### Connecting to the board

If the BeagleBone Black comes preinstalled with an OS, it is recommended to try to use it either with a monitor, a 
keyboard, and a mouse, or through another computer using an `ssh` connection. More information on this in the following 
video:

https://www.youtube.com/watch?v=C2KVSy_yTWk


### Flashing the board

Before starting the installation, make sure to have a BeagleBone Black (BBB) rev C that has been freshly flashed with 
Debian 10.12. Although the installation files might work on different versions, it is not guaranteed. For more 
information on how to flash the BeagleBone, refer to the following link:

https://beagleboard.org/getting-started


## Installation with USB drive

### Getting installation files ready

Add the folder containing these files into a USB drive compatible with Linux.To make sure the USB drive is compatible, 
first format the USB drive in a Linux machine to the file system NTFS. Formatting the USB drive in a windows machine 
might cause issues.


### Installation steps

#### Reading from the USB drive

Plug in the USB drive containing the setup folder into the BBB. Wait a couple of seconds and run the following commands 
on the BBB terminal to ensure the USB drive is being recognized correctly and is working properly:

    $ cd /
    $ sudo fdisk -l

You might see the following prompt asking for the sudo password:

    We trust you have received the usual lecture from the local System
    Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

    [sudo] password for debian:
    
The default password for Debian is `temppwd`. After entering the password, you should see something similar to the 
following output:
    
    debian@beaglebone:/$ sudo fdisk -l                                        <--------- runs sudo fdisk -l
    Disk /dev/mmcblk1: 3.6 GiB, 3825205248 bytes, 7471104 sectors
    Units: sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disklabel type: dos
    Disk identifier: 0xbe1d2075
    
    Device         Boot Start     End Sectors  Size Id Type
    /dev/mmcblk1p1 *     8192 7471103 7462912  3.6G 83 Linux
    
    
    Disk /dev/sda: 28.9 GiB, 30979129856 bytes, 60506113 sectors
    Disk model: USB 3.2.1 FD
    Units: sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disklabel type: dos
    Disk identifier: 0x065da777
    
    Device     Boot Start      End  Sectors  Size Id Type
    /dev/sda1  *       64 60506111 60506048 28.9G  7 HPFS/NTFS/exFAT          <--------- usb drive info

If you do not see the bottom half of the output, please refer back to the section on Getting installation files ready. 
If the problem persists, try using a different USB drive.
After confirming that the USB drive is correctly detected by the board, write down in a piece of paper the path to the 
USB drive found under the 'Device' column. In the example above, the path is `/dev/sda1`. 

Run the following commands:

    $ sudo mkdir media/usb1
    $ sudo mount -o rw /dev/sda1 media/usb1

Note that if the path to your USB drive is different from `/dev/sda1`, you need to replace that path with your specific
correct path in the second command. If the command is succesful, the USB drive is now ready for use.

If the USB drive is mounted as read-only, meaning that the files inside cannot be executed, this might indicate an issue
with the formatting procedure of the USB drive. Try formatting the USB drive again in a Linux machine or try using a 
different USB drive.


#### Running installation files

To run the setup file bbb_setup.sh, run the following commands:

    $ cd /
    $ ./media/usb1/bbb_setup_files/bbb_setup.sh

The setup takes about 2 hours. If the setup file is working properly, no more work from the user is needed. 

Before unplugging the USB drive, run the following command:

    $ cd /
    $ sudo umount /media/usb1

If the command runs succesfully, there should be no output and the USB can be safely ejected. 


## Other Installation methods

Alternatively, you can copy the folder containing these files into the BBB using any other method. The destination of 
the folder does not matter. Once the folder has been copied into the BBB, set it as your working directory and run the 
setup file:

    $ ./bbb_setup.sh