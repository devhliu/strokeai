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
def generate_dcm_index(dcm_root):
    """
    :param dcm_root:
    :return:
    """
    dcmtags = {'SeriesInstanceUID': [], 'SeriesDescription': [],
               'PatientName': [], 'PatientID': [],
               'Modality': [], 'StudyDateTime': [],
               'Spacing_X': [], 'Spacing_Y': [], 'Spacing_Z': [],
               'AKAFileName': [], 'SubRoot': []}
    for sub_root, _, files in os.walk(dcm_root):
        if len(files) <= 0: continue
        print('working on %s ...'%(sub_root))
        for file in files:
            dcm_file = os.path.join(sub_root, file)
            if dcm_file.endswith('.json'): continue
            if dcm_file.endswith('.nii'): continue
            if dcm_file.endswith('.nii.gz'): continue
            if dcm_file.endswith('.bval'): continue
            if dcm_file.endswith('.bvec'): continue
            if dcm_file.endswith('ICOMDIR'): continue
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
                dcmtags['SubRoot'].append(sub_root.replace(dcm_root, '..'))
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
def organize_dcm_byuid(src_dcm_root, target_dcm_root):
    """
    :param src_dcm_root:
    :param target_dcm_root:
    :return:
    """
    _pattern = re.compile('\w')
    for sub_root, _, files in os.walk(src_dcm_root):
        if len(files) <= 0: continue
        print('working on %s ...' % (sub_root))
        for file in files:
            dcm_file = os.path.join(sub_root, file)
            if dcm_file.endswith('.json'): continue
            if dcm_file.endswith('.nii'): continue
            if dcm_file.endswith('.nii.gz'): continue
            if dcm_file.endswith('.bval'): continue
            if dcm_file.endswith('.bvec'): continue
            if dcm_file.endswith('ICOMDIR'): continue
            if not is_dicom(dcm_file): continue
            ds = pydicom.read_file(dcm_file, stop_before_pixels=True, force=True)
            series_uid = str(ds.SeriesInstanceUID)
            study_uid = str(ds.StudyDate + ds.StudyTime) + '.' + str(ds.StudyInstanceUID)
            _patient_name = _pattern.match(str(ds.PatientName)).string.upper().replace(' ', '')
            patient_uid = 'PID.' + str(ds.PatientID) + '.PNAME.' + _patient_name.replace('_', '')
            filename = str(ds.SOPInstanceUID) + '.dcm'
            file_root = os.path.join(target_dcm_root, patient_uid, study_uid, series_uid)
            os.makedirs(file_root, exist_ok=True)
            shutil.copyfile(dcm_file, os.path.join(file_root, filename))
    return
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
# test purpose
#
#------------------------------------------------------------------------------

if __name__ == '__main__':
    dcmroot = '/Users/LiuHui/DicomDB/Shanghai_6th_Hospital/Stroke/WangFeng'
    dcmroot_2 = '/Users/LiuHui/DicomDB/Shanghai_6th_Hospital/Stroke/dcm'
    tmproot = 'D:\\DICOMDB\\Shanghai_6th_Hospital\\001_Stroke_DWI\\tmp'
    niiroot = 'D:\\DICOMDB\\Shanghai_6th_Hospital\\001_Stroke_DWI\\002_niix_2'

    #organize_dcm_byuid(dcmroot, dcmroot_2)
    df = generate_dcm_index(dcmroot_2)
    df.to_excel(os.path.join(dcmroot_2, 'dcm_index.xlsx'))
    # step 1: dump dcm tags into dump.xlsx
    #sub_dcmroots = [os.path.join(dcmroot, o) for o in os.listdir(dcmroot) if os.path.isdir(os.path.join(dcmroot, o))]
    #dfs = []
    #for sub_dcmroot in sub_dcmroots:
    #    if sub_dcmroot.endswith('.xlsx'): continue
    #    print('working on %s'%os.path.basename(sub_dcmroot))
    #    dfs.append(generate_dcm_index(sub_dcmroot))
    # df = pd.concat(dfs, axis=0)
    #df = generate_dcm_index(dcmroot)
    #df.to_excel(os.path.join(dcmroot, 'dcm_index.xlsx'))


    # step 2: update dump.xlsx

    # step 3: dcm2niix dcmroot into tmproot

    # step 4: arrange tmproot into niiroot
    #cp_nii_by_info(tmproot, niiroot, os.path.join(dcmroot, 'dump-working.xlsx'))