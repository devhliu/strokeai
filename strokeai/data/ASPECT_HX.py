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
def _is_dcm_ext(file):
    """
    :param file:
    :return:
    """
    if file.endswith('.txt'): return False
    if file.endswith('.json'): return False
    if file.endswith('.nii'): return False
    if file.endswith('.nii.gz'): return False
    if file.endswith('.bval'): return False
    if file.endswith('.bvec'): return False
    if file.endswith('.xlsx'): return False
    if file.endswith('.hdr'): return False
    if file.endswith('.img'): return False
    if file.endswith('.raw'): return False
    if file.endswith('.roi'): return False
    if file.endswith('.mat'): return False
    if file.endswith('.ps'): return False
    if file.endswith('ICOMDIR'): return False
    return True
#------------------------------------------------------------------------------
#
def _create_pid_pname(ds):
    """
    :param ds:  pydicom dataset
    :return:    PID.xxxx.PNAME....
    """
    _pattern = re.compile('\w')
    # patient uid
    if ds.get('PatientName') is None:
        _patient_name = str(ds.StudyInstanceUID)
    else:
        _patient_name_0 = _pattern.match(str(ds.PatientName))
        if _patient_name_0 is None:
            _patient_name = str(ds.PatientName).upper().replace(' ', '')
        else:
            _patient_name = _patient_name_0.string.upper().replace(' ', '')
    return 'PID.' + str(ds.PatientID) + '.PNAME.' + _patient_name.replace('_', '')
#------------------------------------------------------------------------------
#
def generate_dcm_index_for_pid_pname(dcm_root_0, dcm_root_1):
    """
    :param dcm_root:
    :return:
    """
    dcmtags = {'PIDPNAME': [], 'COPIED': [], 'SUBROOT': []}
    pnames = os.listdir(dcm_root_0)
    pidnames = os.listdir(dcm_root_1)
    for pname in pnames:
        pid = pname.split('_')[-1]
        _pname = pname.replace(pid, '')
        _pname = _pname.replace('_', '').upper()
        _pidname = 'PID.'+pid+'.PNAME.'+_pname
        dcmtags['PIDPNAME'].append(_pidname)
        if _pidname in pidnames: dcmtags['COPIED'].append(True)
        else: dcmtags['COPIED'].append(False)
        dcmtags['SUBROOT'].append(pname)
    return pd.DataFrame(dcmtags)

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
            if not _is_dcm_ext(dcm_file): continue
            if not is_dicom(dcm_file): continue
            ds = pydicom.read_file(dcm_file, stop_before_pixels=True, force=True)
            if ds.SeriesInstanceUID in dcmtags['SeriesInstanceUID']: continue
            try:
                suid = ds.SeriesInstanceUID
                sdesp = ds.SeriesDescription
                pname = ds.PatientName
                pid = ds.PatientID
                modality = ds.Modality
                institution = ds.InstitutionName
                studydatetime = ds.StudyDate + ds.StudyTime
                dcmtags['SeriesInstanceUID'].append(suid)
                dcmtags['SeriesDescription'].append(sdesp)
                dcmtags['PatientName'].append(pname)
                dcmtags['PatientID'].append(pid)
                dcmtags['StudyDateTime'].append(studydatetime)
                dcmtags['Modality'].append(modality)
                dcmtags['InstitutionName'].append(institution)
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
    for sub_root, _, files in os.walk(src_dcm_root):
        if len(files) <= 0: continue
        print('working on %s ...' % (sub_root))

        # copy each dcm file
        for file in files:
            dcm_file = os.path.join(sub_root, file)
            if not _is_dcm_ext(dcm_file): continue
            if not is_dicom(dcm_file): continue
            ds = pydicom.read_file(dcm_file, stop_before_pixels=True, force=True)
            # series uid
            series_uid = str(ds.SeriesInstanceUID)
            # study uid
            if ds.get('StudyDate') is None or ds.get('StudyTime') is None: study_uid = str(ds.StudyInstanceUID)
            else: study_uid = str(ds.StudyDate + ds.StudyTime)[:14]
            # patient uid
            patient_uid = _create_pid_pname(ds)
            # sorting files into patient_uid/study_uid/series_uid structure
            filename = str(ds.SOPInstanceUID) + '.dcm'
            file_root = os.path.join(target_dcm_root, patient_uid, study_uid, series_uid)
            os.makedirs(file_root, exist_ok=True)
            dcm_file_cp = os.path.join(file_root, filename)
            if os.path.exists(dcm_file_cp): continue
            shutil.copyfile(dcm_file, dcm_file_cp)
    return

#------------------------------------------------------------------------------
#
def organize_by_csv(csv_file, dcm_root_0, dcm_root_1):
    """
    :param csv_file:
    :param dcm_root_0:
    :param dcm_root_1:
    :return:
    """
    df = pd.read_csv(csv_file)
    subroots = df['SUBROOT'].values
    copieds = df['COPIED'].values
    pidpnames = df['PIDPNAME'].values

    for subroot, copied, pidpname in zip(subroots, copieds, pidpnames):
        if copied:
            print('%s is already copied to %s.'%(subroot, pidpname))
        else:
            try:
                organize_dcm_byuid(os.path.join(dcm_root_0, subroot), dcm_root_1)
            except:
                print('failed to copy %s - %s.'%(subroot, pidpname))
    return
#------------------------------------------------------------------------------
#
def copy_folder_info(dcm_root_0, dcm_root_1):
    """
    :param dcm_root_0:
    :param dcm_root_1:
    :return:
    """
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
    dcmroot = 'E:\\test'
    dcmroot_2 = 'D:\\ISLES\\RAPID_HX\\001_DCM'

    csv_file = os.path.join(dcmroot_2, 'convert_working.csv')
    df_0 = generate_dcm_index_for_pid_pname(os.path.join(dcmroot, 'RAPID_Result_0'), dcmroot_2)
    df_1 = generate_dcm_index_for_pid_pname(os.path.join(dcmroot, 'RAPID_Result_1'), dcmroot_2)
    df = pd.concat([df_0, df_1], axis=0)
    df.to_csv(csv_file)

    # organize_by_csv(csv_file, os.path.join(dcmroot, 'RAPID_Result_0'), dcmroot_2)
    organize_by_csv(csv_file, os.path.join(dcmroot, 'RAPID_Result_1'), dcmroot_2)

    #organize_dcm_byuid(dcmroot, dcmroot_2)

    #df = generate_dcm_index(dcmroot_2)
    #df.to_excel(os.path.join(dcmroot_2, 'dcm_index.xlsx'))

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