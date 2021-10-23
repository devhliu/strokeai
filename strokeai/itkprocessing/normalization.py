"""
    Program: strokeai/itkprocessing

    A python wrapped medical imaging processing tools for stroke

    file name: normalization.py
    date of creation: 2020-07-30
    date of modification: 2020-08-01
    Author: Liu Hui (huiliu.liu@gmail.com)
    purpose:

"""

import numpy as np
import nibabel as nib
import SimpleITK as sitk

#-------------------------------------------------------------------------------
#
def normalize_ct_to_unit(sitkImage, lower_threshold, upper_threshold):
    sitkImage = sitk.Cast(sitkImage, sitk.sitkFloat64)
    _shift = 0.5 * (lower_threshold + upper_threshold)
    _scale = 1.0 / (upper_threshold - lower_threshold)
    normalized_sitkImage = sitk.ShiftScale(sitkImage, shift=_shift, scale=_scale)
    img_array = sitk.GetArrayFromImage(normalized_sitkImage) + 0.5
    img_array[img_array < 0.0] = 0.0
    img_array[img_array > 1.0] = 1.0
    sitkImage = sitk.GetImageFromArray(img_array)
    sitkImage.SetOrigin(normalized_sitkImage.GetOrigin())
    sitkImage.SetSpacing(normalized_sitkImage.GetSpacing())
    sitkImage.SetDirection(normalized_sitkImage.GetDirection())
    return sitkImage
#------------------------------------------------------------------------------
#
# test purpose
#
#------------------------------------------------------------------------------

if __name__ == '__main__':
    import os
    root = 'E:\\hIBIZ\\Projects\\2020\\2020_07_30_Stroke\\001_references\\TOF_MRA_Altas_nii'

    nii_file = os.path.join(root, 'tofAverage.nii.gz')
    sitk_img = sitk.ReadImage(nii_file)
    sitk_img_n1 = normalize_ct_to_unit(sitk_img, lower_threshold=0, upper_threshold=500)
    sitk.WriteImage(sitk_img_n1, nii_file.replace('.nii.gz', '_n1.nii.gz'))