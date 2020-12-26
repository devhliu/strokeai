
import os
import pydicom
import nibabel as nib
import pandas as pd
import numpy as np

from glob import glob
from datetime import datetime

#------------------------------------------------------------------------------------------------------
#
def diff_datetime_tag(datetime_tag_0, datetime_tag_1):
    """
    :param datetime_tag_0: '20190322143502'
    :param datetime_tag_1: '20190322143502'
    :return:
    """
    d_0 = datetime.strptime(datetime_tag_0, '%Y%m%d%H%M%S')
    d_1 = datetime.strptime(datetime_tag_1, '%Y%m%d%H%M%S')
    delta_time = d_1 - d_0
    return delta_time.seconds / 3600.0

#------------------------------------------------------------------------------
#
def reorganize_niix(niix_root_0, niix_root_1):
    """
    :param niix_root_0:
    :param niix_root_1:
    :return:
    """
    os.makedirs(niix_root_1, exist_ok=True)
    _patient_roots = glob(os.path.join(niix_root_0, '0*'))
    tags = {'PatientIDC': [],
            'PatientName_CT': [], 'PatientID_CT': [], 'SeriesDateTime_CT': [],
            'PatientName_DWI': [], 'PatientID_DWI': [], 'SeriesDateTime_DWI': [],
            'CT_to_DWI_Hours': [], 'SubRoot': []}
    for _patient_root in _patient_roots:
        _patient_idc = os.path.basename(_patient_root)
        tags['PatientIDC'].append(_patient_idc)
        print('working on %s'%(_patient_idc))

        _ct_nii_filename = _patient_idc + 'CTwpz.hdr'
        _dwi_nii_filename = _patient_idc + 'MRIwpz.hdr'
        _dwi_roi_nii_filename = _patient_idc + 'MRIwpzroi.hdr'
        _sub_root_ct = os.path.join(_patient_root, 'CT')
        _sub_root_dwi = os.path.join(_patient_root, 'MRI')

        # CT
        _ct_dcm_files = glob(os.path.join(_sub_root_ct, '*.dcm')) + \
                        glob(os.path.join(_sub_root_ct, '*.ima')) + \
                        glob(os.path.join(_sub_root_ct, '*.IMA')) + \
                        glob(os.path.join(_sub_root_ct, '*.DCM')) + \
                        glob(os.path.join(_sub_root_ct, '...*.dcm'))
        if len(_ct_dcm_files) > 0:
            ds = pydicom.read_file(_ct_dcm_files[0])
            tags['PatientName_CT'].append(ds['PatientName'].value)
            tags['PatientID_CT'].append(ds['PatientID'].value)
            tags['SeriesDateTime_CT'].append(ds['SeriesDate'].value + ds['SeriesTime'].value)
        else:
            tags['PatientName_CT'].append('')
            tags['PatientID_CT'].append('')
            tags['SeriesDateTime_CT'].append('')

        # DWI
        _dwi_dcm_files = glob(os.path.join(_sub_root_dwi, '*.dcm')) + \
                         glob(os.path.join(_sub_root_dwi, '*.ima')) + \
                         glob(os.path.join(_sub_root_dwi, '*.IMA')) + \
                         glob(os.path.join(_sub_root_dwi, '*.DCM'))
        if len(_dwi_dcm_files) > 0:
            ds = pydicom.read_file(_dwi_dcm_files[0])
            tags['PatientName_DWI'].append(ds['PatientName'].value)
            tags['PatientID_DWI'].append(ds['PatientID'].value)
            tags['SeriesDateTime_DWI'].append(ds['SeriesDate'].value + ds['SeriesTime'].value)
        else:
            tags['PatientName_DWI'].append('')
            tags['PatientID_DWI'].append('')
            tags['SeriesDateTime_DWI'].append('')

        tags['CT_to_DWI_Hours'].append(diff_datetime_tag(tags['SeriesDateTime_CT'][-1][:14],
                                                         tags['SeriesDateTime_DWI'][-1][:14]))

        pndwi = str(tags['PatientName_DWI'][-1])
        _patient_idc_1 = _patient_idc + '_' + 'DWI_' + pndwi.replace(' ', '')
        _patient_root_1 = os.path.join(niix_root_1, _patient_idc_1)
        os.makedirs(_patient_root_1, exist_ok=True)
        tags['SubRoot'].append(_patient_idc_1)
        _ct_nii_file = os.path.join(_patient_root_1, _patient_idc_1 + '_CT_img.nii.gz')
        _dwi_nii_file = os.path.join(_patient_root_1, _patient_idc_1 + '_DWI_img.nii.gz')
        _dwi_roi_nii_file = os.path.join(_patient_root_1, _patient_idc_1 + '_DWI_roi.nii.gz')

        try:
            # CT image
            if not os.path.exists(_ct_nii_file):
                _ct_file = os.path.join(_patient_root, _ct_nii_filename)
                if os.path.exists(_ct_file):
                    nib_ct_img = nib.load(os.path.join(_patient_root, _ct_nii_filename))
                    nib.save(nib_ct_img, _ct_nii_file)
            # DWI image
            if not os.path.exists(_dwi_nii_file) or not os.path.exists(_dwi_roi_nii_file):
                nib_dwi_img = nib.load(os.path.join(_patient_root, _dwi_nii_filename))
                nib.save(nib_dwi_img, _dwi_nii_file)
                #os.remove(_dwi_nii_file)

                # DWI roi
                _dwi_roi_file = os.path.join(_patient_root, _dwi_roi_nii_filename)
                if not os.path.exists(_dwi_roi_file.replace('.hdr', '.img')):
                    #print('%s is used.' %('l'+_dwi_roi_nii_filename))
                    _dwi_roi_file = os.path.join(_patient_root, 'l'+_dwi_roi_nii_filename)
                    #os.remove(_dwi_roi_nii_file)
                nib_dwi_roi_img = nib.load(_dwi_roi_file)
                np_img = nib_dwi_roi_img.get_fdata().copy()
                mask_img = np.zeros(np_img.shape, dtype=np.int)
                mask_img[np_img > 0.1] = 1
                nib.save(nib.Nifti1Image(mask_img, affine=nib_dwi_img.affine.copy()), _dwi_roi_nii_file)
                #os.remove(_dwi_roi_nii_file)

        except: print('failed to read %s'%(_patient_idc))

    df = pd.DataFrame(tags)
    df.to_excel(os.path.join(niix_root_1, 'niix_index.xlsx'))
    return
#------------------------------------------------------------------------------
#
# test purpose
#
#------------------------------------------------------------------------------

if __name__ == '__main__':
    project_root = 'D:\\UII\\nanjing_CT_DWI\\ROI1'
    niix_root_new = 'D:\\DICOMDB\\Shanghai_6th_Hospital\\001_Stroke_DWI\\002_niix_004'
    reorganize_niix(project_root, niix_root_new)