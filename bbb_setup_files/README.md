#Setup of a BeagleBone Black rev C to be used as a pid controller using the Automation python library. 

Sebastian Miki-Silva \
miki@atommines.com


## Getting the BeagleBone Black ready

### Connecting to the board

If the BeagleBone Black comes preinstalled with an OS, it is recommended to try to use it either with a monitor, a 
keyboard, and a mouse, or through another computer using an `ssh` connection. The second option with an ethernet cable 
connected to the network is recommended for ease of integration with the rest of the production system. More information
on this in the following video:

https://www.youtube.com/watch?v=C2KVSy_yTWk


### Flashing the board

Before starting the installation, make sure to have a BeagleBone Black (BBB) rev C that has been freshly flashed with 
Debian 10.3. Although the installation files might work on different versions, it is not guaranteed. For more 
information on how to flash the BeagleBone, refer to the following link:

https://beagleboard.org/getting-started

After flashing the board, get it ready to use its Linux terminal followin the steps in Connecting to the board.

## Getting installation files ready

Add the folder containing these files into a USB drive compatible with Linux.To make sure the USB drive is compatible, 
first format the USB drive in a Linux machine to the file system NTFS. 


## Installation 

### Getting the USB drive ready

Plug in the USB drive into the BBB.

Wait a couple seconds and run the following commands on the BBB terminal to ensure the USB drive is working properly:

    $ cd /
    $ sudo fdisk -l

You might see the following prompt for the sudo password:

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
After confirming that the USB drive is correctly detected by the board, save the path to the USB drive under the 
'Device' column for later use. In the example above, the path is `/dev/sda1`. 

Run the following commands:

    $ sudo mkdir media/usb1
    $ sudo mount -o rw /dev/sda1 media/usb1

Note that if your path to your USB drive is different from `/dev/sda1`, you need to replace that path with your specific
correct path in the second command. 

If the command is succesful, the USB drive is now ready for use.

 # TODO: add section about mounting the USB drive being read-only and not writtable

### Running installation files

The installation file will automatically move to the home directory `/~` to install all the files. To run the setup file
bbb_setup.sh, run the following commands:

    $ cd /
    $ ./media/usb1/bbb_setup_files/bbb_setup.sh

The setup takes about 2 hours. If the setup file is working properly, no more work from the user is needed. After the 
setup is done, the USB can be safely disconnected.