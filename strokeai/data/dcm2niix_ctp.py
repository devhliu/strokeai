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
import pydicom
import pandas as pd

from pydicom.misc import is_dicom

#------------------------------------------------------------------------------
#
def rename(name_0):
    """
    :param name_0:
    :return:        new_name: PID.xxxx.PNAME.xxxx
    """
    _pid = name_0.split('_')[-1]
    return 'PID.2020.12.27.' + _pid + '.01'

#------------------------------------------------------------------------------
#
def organize_ncct_niix(niix_root_0, niix_root_1):
    """
    :param niix_root_0:
    :param niix_root_1:
    :return:
    """
    patient_name_ids = os.listdir(niix_root_0)
    for patient_name_id in patient_name_ids:
        pname = rename(patient_name_id)
        nii_file_ASPECT_mask_r_sr = os.path.join(niix_root_0, patient_name_id, 'Aspects-label-update.nii.gz')
        nii_file_r_sr = os.path.join(niix_root_0, patient_name_id, 'brain_image-3D-rotate.nii.gz')
        sub_root = os.path.join(niix_root_1, pname)
        os.makedirs(sub_root, exist_ok=True)
        nii_files_0 = [nii_file_ASPECT_mask_r_sr, nii_file_r_sr]
        nii_filenames_1 = ['ASPECT_mask_rotated_skullstripped_v1.nii.gz', 'NCCT_rotated_skullstripped.nii.gz']
        for nii_file_0, nii_filename_1 in zip(nii_files_0, nii_filenames_1):
            if not os.path.exists(nii_file_0):
                print('failed to read %s'%(nii_file_0))
                continue
            nii_file_1 = os.path.join(sub_root, nii_filename_1)
            if not os.path.exists(nii_file_1): shutil.copyfile(nii_file_0, nii_file_1)
    return
#------------------------------------------------------------------------------
#
def organize_clinical_csv(df, add_key, add_values, index_key, index_values):
    """
    :param df:
    :param add_values:
    :param index_values:
    :return:
    """
    return df
#------------------------------------------------------------------------------
#
def obselete_main():
    """
    :return:
    """
    root_working = 'D:\\UII'
    df = pd.read_csv(os.path.join(root_working, 'NCCT_CTP_clinical_new.csv'))
    patient_name_ids_4 = os.listdir(os.path.join(root_working, 'onset_4'))
    patient_name_ids_5 = os.listdir(os.path.join(root_working, 'onset_5'))
    patient_name_ids_6 = os.listdir(os.path.join(root_working, 'onset_6'))
    patient_name_ids_12 = os.listdir(os.path.join(root_working, 'onset_others'))

    fill_onsitetime = 12
    patient_name_ids_working = patient_name_ids_12

    subj_names = df['subj_name'].to_list()
    if df.get('OnsiteTime(h)') is None:
        df_onsitetime = pd.DataFrame({'OnsiteTime(h)': [0, ]*len(subj_names)})
        df = pd.concat([df, df_onsitetime], axis=1)
    onsitetimes = df['OnsiteTime(h)'].to_list()
    ages = df['Age'].to_list()
    genders = df['Gender'].to_list()
    newPIDs = []
    new_ages = []
    new_onsitetimes = []
    for subj_name, onsitetime, age in zip(subj_names, onsitetimes, ages):
        new_pid = 'PID.2020.12.27.' + subj_name.split('_')[-1] + '.01'
        newPIDs.append(new_pid)
        new_ages.append(age)
        if subj_name in patient_name_ids_working: new_onsitetimes.append(fill_onsitetime)
        else: new_onsitetimes.append(onsitetime)
    for patient_name_id in patient_name_ids_working:
        if patient_name_id in subj_names: continue
        new_pid = 'PID.2020.12.27.' + patient_name_id.split('_')[-1] + '.01'
        newPIDs.append(new_pid)
        new_ages.append(0)
        genders.append('NA')
        new_onsitetimes.append(fill_onsitetime)
        subj_names.append(patient_name_id)
    df = pd.DataFrame({'subj_name': subj_names, 'PID':newPIDs, 'Age': new_ages, 'Gender': genders, 'OnsiteTime(h)': new_onsitetimes})
    df.to_csv(os.path.join(root_working, 'NCCT_CTP_clinical_new.csv'))
    return
#------------------------------------------------------------------------------
#
# test purpose
#
#------------------------------------------------------------------------------

if __name__ == '__main__':
    niix_root_0 = 'D:\\UII\\CT_CTP_copy_annotation'
    niix_root_1 = 'E:\\DicomDB\\ASPECT_SEG\\002_NIIX_CT_working'
    organize_ncct_niix(niix_root_0, niix_root_1)
