"""
Created on Tuesday, April 19, 2022
@author: Sebastian Miki-Silva
"""

import auxiliary
import device_models


def main():
    a = device_models.SPD3303X(ip4_address='10.176.42.121')
    auxiliary.testing_SPD3303X(a)


if __name__ == '__main__':
    main()
