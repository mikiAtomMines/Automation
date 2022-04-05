"""
Created on Tuesday, April 5, 2022

@author: Sebastian Miki-Silva
"""

from mcculw import ul
from mcculw.enums import TempScale
from mcculw.enums import InterfaceType
from mcculw.device_info import DaqDeviceInfo

# def config_first_detected_device(board_num, dev_id_list=None):
#     """Adds the first available device to the UL.  If a types_list is specified,
#     the first available device in the types list will be add to the UL.
#
#     Parameters
#     ----------
#     board_num : int
#         The board number to assign to the board when configuring the device.
#
#     dev_id_list : list[int], optional
#         A list of product IDs used to filter the results. Default is None.
#         See UL documentation for device IDs.
#     """
#     ul.ignore_instacal()
#     devices = ul.get_daq_device_inventory(InterfaceType.ANY)
#     if not devices:
#         raise Exception('Error: No DAQ devices found')
#
#     print('Found', len(devices), 'DAQ device(s):')
#     for device in devices:
#         print('  ', device.product_name, ' (', device.unique_id, ') - ',
#               'Device ID = ', device.product_id, sep='')
#
#     device = devices[0]
#     if dev_id_list:
#         device = next((device for device in devices
#                        if device.product_id in dev_id_list), None)
#         if not device:
#             err_str = 'Error: No DAQ device found in device ID list: '
#             err_str += ','.join(str(dev_id) for dev_id in dev_id_list)
#             raise Exception(err_str)
#
#     # Add the first DAQ device to the UL with the specified board number
#     ul.create_daq_device(board_num, device)


def main():
    """
    The following command words fine because instacal is adding the device to the library.

    print(ul.t_in(0, 0, TempScale.CELSIUS))

    """

    # Does not work. Not sure why.
    ul.ignore_instacal()
    print(ul.get_net_device_descriptor('10.176.42.222', 54211, 2000))


if __name__ == "__main__":
    main()



























