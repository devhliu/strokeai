"""
    Program: strokeai/data

    A python wrapped medical imaging processing tools for stroke

    file name: __init__.py
    date of creation: 2020-10-04
    date of modification: 2020-10-04
    Author: Liu Hui (huiliu.liu@gmail.com)
    purpose:

"""
import os
import re
import shutil
import pandas as pd
import SimpleITK as sitk

from glob import glob

#------------------------------------------------------------------------------
#
def newname(name_0):
    """
    :param name_0:
    :return:        new_name: PID.xxxx.PNAME.xxxx
    """
    code = re.findall('[0-9]+', name_0)
    return 'PID.2021.01.01.ICH.' + '{:06d}.'.format(int(code[0])) + 'P.{:02d}'.format(int(code[1]))


#------------------------------------------------------------------------------
#
def copy_origin_image(patient_root_0, niix_root_1):
    """
    :param patient_root_0:
    :param niix_root_1:
    :return:
    """
    new_pname_root = os.path.join(niix_root_1, newname(os.path.basename(patient_root_0)))
    os.makedirs(new_pname_root, exist_ok=True)
    input_files = glob(os.path.join(patient_root_0, '*.nii.gz'))
    for input_file in input_files:
        nii_file_0 = os.path.join(patient_root_0, input_file)
        nii_file_1 = os.path.join(new_pname_root, os.path.basename(nii_file_0))
        shutil.copyfile(nii_file_0, nii_file_1)
    return
#------------------------------------------------------------------------------
#
def copy_origin_mhd_image(patient_root_0, niix_root_1):
    """
    :param patient_root_0:
    :param niix_root_1:
    :return:
    """
    new_pname_root = os.path.join(niix_root_1, newname(os.path.basename(patient_root_0)))
    os.makedirs(new_pname_root, exist_ok=True)
    input_files = glob(os.path.join(patient_root_0, '*.mhd'))
    for input_file in input_files:
        nii_file_0 = os.path.join(patient_root_0, input_file)
        if nii_file_0.endswith('artery_mask.mhd'): continue
        print('working on %s'%(nii_file_0))
        nii_file_1 = os.path.join(new_pname_root, os.path.basename(nii_file_0).replace('.mhd', '.nii.gz'))
        sitk_img = sitk.ReadImage(nii_file_0)
        sitk.WriteImage(sitk_img, nii_file_1)
        #shutil.copyfile(nii_file_0, nii_file_1)
    return
#------------------------------------------------------------------------------
#
def index_ich_niix(niix_root):
    """
    :param niix_root:
    :return:
    """
    tags = {'PID': [], 'PHASE': [], 'SLICETHICK': [], 'SLICETHIN': [], 'ANNOTATED': [], 'SUBROOT': []}
    pnames = os.listdir(niix_root)
    for pname in pnames:
        if not pname.startswith('PID.'): continue
        tags['PID'].append(str('P{:06d}'.format(int(pname[19:25]))))
        tags['PHASE'].append(str('P{:02d}'.format(int(pname[28:]))))
        tags['SUBROOT'].append(pname)
        tags['SLICETHIN'].append(os.path.exists(os.path.join(niix_root, pname, 'image_thin.nii.gz')))
        tags['SLICETHICK'].append(os.path.exists(os.path.join(niix_root, pname, 'image_thick.nii.gz'))
                                  or os.path.exists(os.path.join(niix_root, pname, 'rotated_image.nii.gz')))
        tags['ANNOTATED'].append(os.path.exists(os.path.join(niix_root, pname, 'partition.nii.gz')))
    return pd.DataFrame(tags)

#------------------------------------------------------------------------------
#
# test purpose
#
#------------------------------------------------------------------------------

if __name__ == '__main__':
    niix_root = 'D:\\ISLES\\ICH\\001_JDYY\\001_NIIX'
    df = index_ich_niix(niix_root)
    df.to_csv(os.path.join(niix_root, 'index.csv'))

