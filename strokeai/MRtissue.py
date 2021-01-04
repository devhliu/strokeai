# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import subprocess
import shutil

import numpy as np
import nibabel as nib

from glob import glob


#------------------------------------------------------------------------------
#
def rename(name_0):
    """
    :param name_0:
    :return:        new_name: PID.xxxx.PNAME.xxxx
    """
    _pid = name_0.split('_')[-2]
    return 'PID.2020.12.27.' + _pid + '.{:02d}'.format(int(name_0.split('_')[-1]))


#----------------------------------------------------------------------------------------------
#
# Test Purpose
#
#----------------------------------------------------------------------------------------------
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    niix_root_0 = 'D:\\ISLES\\MR_SkullStrip_LR'
    niix_root_1 = 'D:\\ISLES\\struct_mask'

    pnames = os.listdir(niix_root_0)
    pnames_1 = os.listdir(niix_root_1)
    for pname in pnames:
        if pname in pnames_1:
            shutil.copyfile(os.path.join(niix_root_1, pname, 'struct_109.nii.gz'),
                            os.path.join(niix_root_0, pname, 'struct_109.nii.gz'))
            shutil.copyfile(os.path.join(niix_root_1, pname, 'tissue.nii.gz'),
                            os.path.join(niix_root_0, pname, 'tissue.nii.gz'))
        else:
            print(pname)