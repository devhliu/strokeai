# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import re
import zipfile
import pydicom
import shutil

from glob import glob
from pydicom.misc import is_dicom

#------------------------------------------------------------------------------
#
def create_pid_pname_from_dcm(ds):
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
            _patient_name = _patient_name.replace('^', '')
    return 'PID.' + str(ds.PatientID) + '.PNAME.' + _patient_name.replace('_', '')
#------------------------------------------------------------------------------
#
def create_pid_pname_from_path(patient_dcm_root):
    """
    :param patient_dcm_root:
    :return:    PID.xxxx.PNAME....
    """
    patient_strs = patient_dcm_root.split('_ZS')
    pid = 'ZS' + patient_strs[1]
    patient_name = patient_strs[0].upper().replace('_', '')

    return 'PID.' + pid + '.PNAME.' + patient_name.replace('_', '')

#------------------------------------------------------------------------------
#
def calc_subroot_size(subroot):
    """
    :param subroot:
    :return:
    """
    subroot_size = 0
    try:
        for _subroot, _, files in os.walk(subroot):
            for file in files:
                fp = os.path.join(_subroot, file)
                subroot_size += os.path.getsize(fp)
    except: print('failed to get %s size'%(subroot))
    return subroot_size
#------------------------------------------------------------------------------
#
def compress_subroot(subroot, zip_file):
    """
    :param subroot:
    :param zip_file:
    :return:
    """
    print('zipping %s to %s'%(subroot, zip_file))
    ziping_file = zipfile.ZipFile(zip_file, 'w')
    with ziping_file:
        for _subroot, _, files in os.walk(subroot):
            for filename in files:
                file_path = os.path.join(_subroot, filename)
                ziping_file.write(file_path)
    return
#------------------------------------------------------------------------------
#
def compress_dcmroot(dcmroot, zip_file):
    """
    :param dcmroot:
    :param zip_file:
    :return:
    """
    print('zipping %s to %s'%(dcmroot, zip_file))
    ziping_file = zipfile.ZipFile(zip_file, 'w')
    with ziping_file:
        for _subroot, _, files in os.walk(dcmroot):
            for filename in files:
                file_path = os.path.join(_subroot, filename)
                if is_dicom(file_path): ziping_file.write(file_path)
    return
#----------------------------------------------------------------------------------------------
#
def compress_patient_dcmroot_ziproot(patient_dcmroot, zip_root):
    """
    :param patient_dcmroot:     assume that there is only one patient dcm data in this dcmroot
    :param patient_dcmzip_file:
    :return:
    organized by pid-pname/studydate-study_uid/series_uid
    """
    # find the first dcm
    dcm_file = ''
    for subroot, _, files in os.walk(patient_dcmroot):
        if len(files) == 0: continue
        for file in files:
            if is_dicom(os.path.join(subroot, file)):
                dcm_file = os.path.join(subroot, file)
                break
    if not os.path.exists(dcm_file):
        print('there is no valid dcm in %s.'%(patient_dcmroot))
        return

    # read the first dcm
    ds = pydicom.read_file(dcm_file, stop_before_pixels=True)
    patient_uid = create_pid_pname_from_dcm(ds)

    zip_file = os.path.join(zip_root, patient_uid + '.zip')
    if os.path.exists(zip_file): return

    # zipping the dcm files on the single patient level
    print('zipping %s into %s'%(patient_dcmroot, zip_file))
    ziping_file = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_BZIP2)
    with ziping_file:
        for _subroot, _, files in os.walk(patient_dcmroot):
            for filename in files:
                _dcmfile = os.path.join(_subroot, filename)
                if not is_dicom(_dcmfile): continue
                _ds = pydicom.read_file(_dcmfile, stop_before_pixels=True)
                _studydate = str(_ds.get('StudyDate'))
                _seriesuid = str(_ds.get('SeriesInstanceUID'))
                #if _ds.get('InstanceNumber') is not None:
                #    _instancenb = int(_ds.get('InstanceNumber'))
                #    _filename = '{:08d}.dcm'.format(_instancenb)
                #else: _filename = filename
                ziping_file.write(_dcmfile,
                                  os.path.join(patient_uid, _studydate, _seriesuid, filename),
                                  compresslevel=9)
    return

#----------------------------------------------------------------------------------------------
#
# Test Purpose
#
#----------------------------------------------------------------------------------------------
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dcm_root = 'D:\\stroke\\MR_Liver_Cancer\\raw_data'
    zip_dcm_root = 'D:\\MR_Liver_Cancer\\001_DCM'
    zip_niix_root = 'D:\\MR_Liver_Cancer\\002_NIIX_SEG'

    dirnames = os.listdir(dcm_root)
    for dirname in dirnames:
        dcm_sub_root = os.path.join(dcm_root, dirname)
        compress_patient_dcmroot_ziproot(dcm_sub_root, zip_dcm_root)
        """
        # copy to niix_seg
        patient_niix_root = os.path.join(zip_niix_root, create_pid_pname_from_path(dirname))
        print('copying to %s'%(patient_niix_root))
        os.makedirs(patient_niix_root, exist_ok=True)
        nii_files = glob(os.path.join(dcm_sub_root, '*.nii.gz'))
        for nii_file in nii_files:
            shutil.copyfile(nii_file, os.path.join(patient_niix_root, os.path.basename(nii_file)))
        """