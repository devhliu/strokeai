# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import subprocess

import numpy as np
import pandas as pd
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
    return 'PID.2020.12.27.' + _pid + '.{:02d}'.format(1), 'SERIESID.{:02d}'.format(int(name_0.split('_')[-1]))
#------------------------------------------------------------------------------
#


#----------------------------------------------------------------------------------------------
#
def create_annotation(niix_root_0, niix_root_1):
    """
    :param niix_root_0:
    :param niix_root_1:
    :return:
    """
    masks = ['右丘脑', '右基底节区', '右小脑半球', '右枕叶', '右脑组织', '右顶叶', '右额叶', '右颞叶',
             '左丘脑', '左基底节区', '左小脑半球', '左枕叶', '左脑组织', '左顶叶', '左额叶', '左颞叶',
             '脑室', '脑干']
    pnames = os.listdir(niix_root_0)
    for pname in pnames:
        print(pname)
        newpname, newsubdir = rename(pname)
        newpname_root = os.path.join(niix_root_1, newpname, newsubdir)
        if not os.path.exists(os.path.join(niix_root_0, pname, 'brain_mask.nii.gz')): continue
        os.makedirs(newpname_root, exist_ok=True)

        nii_file_partition = os.path.join(newpname_root, 'brain_partition.nii.gz')
        if os.path.exists(nii_file_partition): continue

        nib_img = nib.load(os.path.join(niix_root_0, pname, 'origin.nii.gz'))
        nib_mask = nib.load(os.path.join(niix_root_0, pname, 'brain_mask.nii.gz'))
        np_mask = np.zeros(nib_mask.get_fdata().shape, dtype=np.int)
        for i, mask in enumerate(masks):
            np_idx = nib.load(os.path.join(niix_root_0, pname, mask+'.nii.gz')).get_fdata()
            np_mask[np_idx > 0.0] = i + 1
        nib_mask_1 = nib.Nifti1Image(np_mask, affine=nib_mask.affine)
        nib.save(nib_mask_1, nii_file_partition)
        nib.save(nib_img, os.path.join(newpname_root, 'image_rotated.nii.gz'))
        nib.save(nib_mask, os.path.join(newpname_root, 'brain_mask.nii.gz'))

#----------------------------------------------------------------------------------------------
#
# Test Purpose
#
#----------------------------------------------------------------------------------------------
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #niix_root_0 = 'D:\\ISLES\\001_RAPID_HX\\002_SEG_ANNO\\001_CTP_PARTITION_ANNO'
    #niix_root_1 = 'D:\\ISLES\\001_RAPID_HX\\002_SEG_ANNO\\001_CTP_PARTITION_ANNO_1'

    #os.makedirs(niix_root_1, exist_ok=True)
    #create_annotation(niix_root_0, niix_root_1)
    project_root = '\\\\dataserver03\\ai_test\\Neurolab\\ct-ctp-strokeProject\\download'
    dirnames = os.listdir(os.path.join(project_root, 'RAPID_Result_0'))
    dirnames += os.listdir(os.path.join(project_root, 'RAPID_Result_1'))
    tags = {'PID': [], 'SID': []}
    for dirname in dirnames:
        newname = rename(dirname)
        tags['PID'].append(newname[0])
        tags['SID'].append(newname[1])
    df = pd.DataFrame(tags)
    df.to_csv('E:\\ctp.csv')