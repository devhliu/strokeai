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
import shutil
import random
import pydicom
import subprocess
import pandas as pd
import nibabel as nib
import numpy as np

from glob import glob
from pydicom.misc import is_dicom

#------------------------------------------------------------------------------
#
def generate_info(dcm_root):
    """
    :param dcm_root:
    :return:
    """
    dcmtags = {'SeriesInstanceUID': [], 'SeriesDescription': [], 'PatientName': [],
               'PatientID': [], 'Modality': [], 'StudyDateTime': [],
               'Spacing_X': [], 'Spacing_Y': [], 'Spacing_Z': [],
               'AKAFileName': [], 'SubRoot': []}
    for sub_root, _, files in os.walk(dcm_root):
        if len(files) <= 0: continue
        for file in files:
            dcm_file = os.path.join(sub_root, file)
            if dcm_file.endswith('.json'): continue
            if dcm_file.endswith('.nii'): continue
            if dcm_file.endswith('.nii.gz'): continue
            if not is_dicom(dcm_file): continue
            ds = pydicom.read_file(dcm_file, stop_before_pixels=True, force=True)
            if ds.SeriesInstanceUID in dcmtags['SeriesInstanceUID']: continue
            try:
                suid = ds.SeriesInstanceUID
                sdesp = ds.SeriesDescription
                pname = ds.PatientName
                pid = ds.PatientID
                modality = ds.Modality
                studydatetime = ds.StudyDate + ds.StudyTime
                dcmtags['SeriesInstanceUID'].append(suid)
                dcmtags['SeriesDescription'].append(sdesp)
                dcmtags['PatientName'].append(pname)
                dcmtags['PatientID'].append(pid)
                dcmtags['StudyDateTime'].append(studydatetime)
                dcmtags['Modality'].append(modality)
                dcmtags['AKAFileName'].append('')
                dcmtags['SubRoot'].append(sub_root)
            except: continue
            try:
                spacing = (float(ds.PixelSpacing[0]), float(ds.PixelSpacing[1]), float(ds.SliceThickness))
                dcmtags['Spacing_X'].append(spacing[0])
                dcmtags['Spacing_Y'].append(spacing[1])
                dcmtags['Spacing_Z'].append(spacing[2])
            except:
                dcmtags['Spacing_X'].append('NA')
                dcmtags['Spacing_Y'].append('NA')
                dcmtags['Spacing_Z'].append('NA')
    return pd.DataFrame(dcmtags)
#------------------------------------------------------------------------------
#
def cp_nii_by_info(tmp_folder, nii_folder, info_xlsx_file):
    """
    :param tmp_folder:
    :param nii_folder:
    :param info_xlsx_file:
    :return:
    """
    df = pd.read_excel(info_xlsx_file)
    suids = df['SeriesInstanceUID'].values
    pnames = df['PatientName'].values
    pids = df['PatientID'].values
    study_datetimes = df['StudyDateTime'].values
    akafilenames = df['AKAFileName'].values

    for suid, pname, pid, sdt, akafilename in zip(suids, pnames, pids, study_datetimes, akafilenames):
        # print('working on %s - %s - %s - %s'%(pid, pname, str(sdt)[:12], akafilename))
        studyroot = os.path.join(nii_folder, str(pid) + '-' + str(pname).replace(' ', '_'), str(sdt)[:12])
        os.makedirs(studyroot, exist_ok=True)
        src_nii_file = os.path.join(tmp_folder, 'suid_' + str(suid) + '.nii.gz')
        src_json_file = os.path.join(tmp_folder, 'suid_' + str(suid) + '.json')
        target_nii_file = os.path.join(studyroot, akafilename + '.nii.gz')
        target_json_file = os.path.join(studyroot, akafilename + '.json')
        if not os.path.exists(target_nii_file) or not os.path.exists(target_json_file):
            try:
                shutil.copyfile(src_nii_file, target_nii_file)
                shutil.copyfile(src_json_file, target_json_file)
            except: print('... failed to copy %s - %s - %s - %s'%(pid, pname, str(sdt)[:12], akafilename))
        if akafilename == 'DWI':
            src_bval_file = os.path.join(tmp_folder, 'suid_' + str(suid) + '.bval')
            src_bvec_file = os.path.join(tmp_folder, 'suid_' + str(suid) + '.bvec')
            target_bval_file = os.path.join(studyroot, akafilename + '.bval')
            target_bvec_file = os.path.join(studyroot, akafilename + '.bvec')
            if not os.path.exists(target_bval_file) or not os.path.exists(target_bvec_file):
                try:
                    shutil.copyfile(src_bval_file, target_bval_file)
                    shutil.copyfile(src_bvec_file, target_bvec_file)
                except:
                    print('... failed to copy %s - %s - %s - %s' % (pid, pname, str(sdt)[:12], akafilename))
    return
#------------------------------------------------------------------------------
#
def create_nii_by_info(nii_folder, info_xlsx_file):
    """
    :param nii_folder:
    :param info_xlsx_file:
    :return:
    """
    df = pd.read_excel(info_xlsx_file)
    pnames = df['PatientName'].values
    study_datetimes = df['StudyDateTime'].values
    modalities = df['Modality'].values
    akafilenames = df['AKAFileName'].values
    subroots = df['SubRoot'].values
    for pname, sdt, modality, akafilename, subroot in zip(pnames, study_datetimes, modalities, akafilenames, subroots):
        print('working on  %s - %s - %s'%(pname, str(sdt)[:12], akafilename))
        if akafilename == 'NoImport': continue
        studyroot = os.path.join(nii_folder, str(pname).replace(' ', '_'), str(sdt)[:12] + '-' + modality)
        os.makedirs(studyroot, exist_ok=True)
        if os.path.exists(os.path.join(studyroot, akafilename + '.nii.gz')): continue
        subprocess.call(['dcm2niix', '-o', studyroot, '-f', akafilename, subroot])
    return
#------------------------------------------------------------------------------
#
def organize_by_uid(src_dcm_root, target_dcm_root):
    """
    :param src_dcm_root:
    :param target_dcm_root:
    :return:
    """
    for sub_root, _, files in os.walk(src_dcm_root):
        if len(files) <= 0: continue
        print(sub_root)
        for file in files:
            dcm_file = os.path.join(sub_root, file)
            if dcm_file.endswith('.json'): continue
            if dcm_file.endswith('.nii'): continue
            if dcm_file.endswith('.nii.gz'): continue
            if dcm_file.endswith('.img'): continue
            if dcm_file.endswith('.hdr'): continue
            if dcm_file.endswith('DICOMDIR'): continue
            if dcm_file.endswith('LOCKFILE'): continue
            if dcm_file.endswith('VERSION'): continue
            if not is_dicom(dcm_file): continue
            ds = pydicom.read_file(dcm_file, stop_before_pixels=True, force=True)
            suid = str(ds.SeriesInstanceUID)
            study_uid = str(ds.StudyInstanceUID)
            filename = '{:06d}.dcm'.format(int(ds.InstanceNumber))
            file_root = os.path.join(target_dcm_root, study_uid, suid)
            os.makedirs(file_root, exist_ok=True)
            out_file = os.path.join(file_root, filename)
            if os.path.exists(out_file): continue
            shutil.copyfile(dcm_file, out_file)
    return
#------------------------------------------------------------------------------
#
def organize_by_uid_dcm(src_dcm_root, target_dcm_root):
    """
    :param src_dcm_root:
    :param target_dcm_root:
    :return:
    """
    for sub_root, _, files in os.walk(src_dcm_root):
        if len(files) <= 0: continue
        print(sub_root)

        # check whether files[0] in dcm
        dcm_file = os.path.join(sub_root, files[0])
        if dcm_file.endswith('.json'): continue
        if dcm_file.endswith('.nii'): continue
        if dcm_file.endswith('.nii.gz'): continue
        if dcm_file.endswith('.img'): continue
        if dcm_file.endswith('.hdr'): continue
        if dcm_file.endswith('DICOMDIR'): continue
        if dcm_file.endswith('LOCKFILE'): continue
        if dcm_file.endswith('VERSION'): continue
        if not is_dicom(dcm_file): continue
        ds = pydicom.read_file(dcm_file, stop_before_pixels=True, force=True)
        study_uid = str(ds.StudyInstanceUID)
        if os.path.exists(os.path.join(os.path.dirname(target_dcm_root), '001_DCM', study_uid)): continue

        for file in files:
            dcm_file = os.path.join(sub_root, file)
            if dcm_file.endswith('.json'): continue
            if dcm_file.endswith('.nii'): continue
            if dcm_file.endswith('.nii.gz'): continue
            if dcm_file.endswith('.img'): continue
            if dcm_file.endswith('.hdr'): continue
            if dcm_file.endswith('DICOMDIR'): continue
            if dcm_file.endswith('LOCKFILE'): continue
            if dcm_file.endswith('VERSION'): continue
            if not is_dicom(dcm_file): continue
            ds = pydicom.read_file(dcm_file, stop_before_pixels=True, force=True)
            suid = str(ds.SeriesInstanceUID)
            study_uid = str(ds.StudyInstanceUID)
            filename = '{:06d}.dcm'.format(int(ds.InstanceNumber))
            file_root = os.path.join(os.path.dirname(target_dcm_root), '000_RAW', study_uid, suid)
            os.makedirs(file_root, exist_ok=True)
            out_file = os.path.join(file_root, filename)
            if os.path.exists(out_file): continue
            shutil.copyfile(dcm_file, out_file)
    return
#------------------------------------------------------------------------------
#
def extract_hb_dwi(niix_root):
    """
    :param niix_root:
    :return:
    """
    for sub_root, _, files in os.walk(niix_root):
        if len(files) <= 0: continue
        for file in files:
            if not file == 'DWI.nii.gz': continue
            nib_dwi = nib.load(os.path.join(sub_root, 'DWI.nii.gz'))
            np_nib_dwi = nib_dwi.get_fdata()
            if len(list(np.shape(np_nib_dwi))) == 4:
                nib_dwi_hb = nib.four_to_three(nib_dwi)[0]
            else: nib_dwi_hb = nib_dwi
            print(np.sum(nib_dwi_hb.get_fdata()))
            nib.save(nib_dwi_hb, os.path.join(sub_root, 'DWI_hb.nii.gz'))
    return


#------------------------------------------------------------------------------
#
# test purpose
#
#------------------------------------------------------------------------------

if __name__ == '__main__':
    dcmroot = '\\\\dataserver03\\ai_test\\Neurolab\\ct-ctp-strokeProject\\renji_377'
    #tmproot = 'D:\\DICOMDB\\Shanghai_6th_Hospital\\001_Stroke_DWI\\tmp'
    #niiroot = 'D:\\DICOMDB\\Shanghai_6th_Hospital\\001_Stroke_DWI\\002_niix_3'
    dcmroot_1 = 'D:\\hl\\renji_377\\000_RAW'
    organize_by_uid_dcm(dcmroot, dcmroot_1)


    # step 1: dump dcm tags into dump.xlsx
    """
    sub_dcmroots = [os.path.join(dcmroot, o) for o in os.listdir(dcmroot_1) if os.path.isdir(os.path.join(dcmroot_1, o))]
    dfs = []
    for sub_dcmroot in sub_dcmroots:
        print('working on %s'%os.path.basename(sub_dcmroot))
        dfs.append(generate_info(sub_dcmroot))
    df = pd.concat(dfs, axis=0)
    df.to_excel(os.path.join(dcmroot, 'dump.xlsx'))
    """

    # step 2: update dump.xlsx

    # step 3: dcm2niix dcmroot into tmproot

    # step 4: arrange tmproot into niiroot

    #create_nii_by_info(niiroot, os.path.join(dcmroot_1, 'dump_working.xlsx'))
    # extract_hb_dwi(niiroot)

    """
    niix_root = 'D:\\UII\\organizedImages'
    tar_niix_root = 'H:\\data\\CT_ASPECT\\nomi'
    filenames = ['brain_aspects_seg.nii.gz', 'ct_3D_rotated_skull_stripped.nii.gz',
                 'cbf.nii.gz', 'mask_cbf.nii.gz']
    tfilenames = ['NCCT_aspects_seg.nii.gz', 'NCCT_skull_stripped.nii.gz',
                  'cbf.nii.gz', 'cbf_mask.nii.gz']
    sub_patient_roots = os.listdir(niix_root)
    for sub_patient_root in sub_patient_roots:
        patient_id = sub_patient_root.split('_')[-1]
        _files = glob(os.path.join(niix_root, sub_patient_root, '*.nii.gz'))
        files = [os.path.basename(_file) for _file in _files]
        mask = [False, ] * len(filenames)
        for i, filename in enumerate(filenames):
            if filename in files: mask[i] = True
        print(mask)
        if all(mask):
            sub = os.path.join(tar_niix_root, '1001'+patient_id+'1001')
            os.makedirs(sub, exist_ok=True)
            print('working on %s'%(sub_patient_root))
            for f1, f2 in zip(filenames, tfilenames):
                shutil.copyfile(os.path.join(os.path.join(niix_root, sub_patient_root, f1)),
                                os.path.join(os.path.join(sub, f2)))
    """