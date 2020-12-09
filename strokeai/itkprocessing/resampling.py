"""
    Program: strokeai/itkprocessing

    A python wrapped medical imaging processing tools for stroke

    file name: resampling.py
    date of creation: 2020-07-30
    date of modification: 2020-08-01
    Author: Liu Hui (huiliu.liu@gmail.com)
    purpose:

"""

import numpy as np
import nibabel as nib
import SimpleITK as sitk
from glob import glob

#-------------------------------------------------------------------------------
# resample sitk_image to referenced sitk_image
def resample_sitk_image_by_reference(reference, sitk_image):
    """
    :param reference:
    :param sitk_image:
    :return:
    """
    resampler = sitk.ResampleImageFilter()
    resampler.SetInterpolator(sitk.sitkBSpline)
    resampler.SetReferenceImage(reference)
    return resampler.Execute(sitk_image)

#------------------------------------------------------------------------------
# resampling the sitk_image with new size and spacing by preserving the spatial range
# appliable for 2d, 3d
def resample_sitk_image_center_aligned(sitk_image, size, range, padding='min'):
    """
    :param sitk_image:
    :param size:    tuple
    :param range:   tuple
    :param padding: 'zero', 'min'
    :return:
    """
    # checks
    if padding not in ['zero', 'min']: raise ValueError('padding should be either zero or min.')

    # get properties
    dim = sitk_image.GetDimension()
    np_old_size = np.array(sitk_image.GetSize(), dtype=np.uint32)
    np_old_spacing = np.array(sitk_image.GetSpacing(), dtype=np.float)
    np_old_origin = np.array(sitk_image.GetOrigin(), dtype=np.float)

    # new spatial config
    if len(size) != len(range) != dim: raise ValueError('size or range is not matched with sitk_image.')
    np_range = np.array(range, dtype=np.float)
    np_size = np.array(size, dtype=np.float)
    np_spacing = np_range / np_size

    # faster performance : check whether to resample or not
    if np.equal(np_size, np_old_size).all() and np.equal(np_spacing, np_old_spacing).all(): return sitk_image

    new_size = tuple(np_size.astype(np.uint32).tolist())
    new_spacing = tuple(np_spacing.astype(np.float).tolist())

    # determine the new origin
    np_matrix_direction = np.array(sitk_image.GetDirection()).reshape(dim, dim)
    np_calibrated_shift = np.dot(np_matrix_direction, np_old_spacing * np_old_size / 2)
    np_center = np_old_origin + np_calibrated_shift
    np_calibrated_shift = np.dot(np_matrix_direction, np_spacing * np_size / 2)
    np_new_origin = np_center - np_calibrated_shift
    new_origin = tuple(np_new_origin.tolist())

    # determine the padding
    padding_value = 0.0
    if padding is 'min': padding_value = float(np.ndarray.min(sitk.GetArrayFromImage(sitk_image)))

    # resample sitk_image into new specs
    transform = sitk.Transform()
    return sitk.Resample(sitk_image, new_size, transform, sitk.sitkBSpline,
                         new_origin, new_spacing, sitk_image.GetDirection(),
                         padding_value, sitk_image.GetPixelID())

# ------------------------------------------------------------------------------
# resampling the sitk_image with new size and spacing by preserving the spatial range
# appliable for 2d, 3d
def resample_sitk_image_with_preserved_spatial_range(sitk_image,
                                                     size=None,
                                                     spacing=None,
                                                     padding='min'):
    """
    :param sitk_image:
    :param size:    tuple
    :param spacing: tuple
    :param padding: 'zero', 'min'
    :return:
    """
    # checks
    if sitk_image == None: raise ValueError('sitk_image should not be None.')
    checks = (size is not None, spacing is not None)
    if True not in checks: raise ValueError('either size or spacing should be specified.')
    if padding not in ['zero', 'min']: raise ValueError('padding should be either zero or min.')

    # get properties
    dim = sitk_image.GetDimension()
    np_old_size = np.array(sitk_image.GetSize(), dtype=np.uint32)
    np_old_spacing = np.array(sitk_image.GetSpacing(), dtype=np.float)
    np_old_origin = np.array(sitk_image.GetOrigin(), dtype=np.float)

    # perserved range
    np_range = np.multiply(np_old_size, np_old_spacing)

    # calculate new size and new spacing
    if checks == (True, False):
        np_size = np.array(size, dtype=np.uint32)
        np_spacing = np.divide(np_range, np_size)
    elif checks == (False, True):
        np_spacing = np.array(spacing, dtype=np.float)
        np_size = np.divide(np_range, np_spacing)
    else:
        np_size = np_old_size
        np_spacing = np_old_spacing

    # faster performance : check whether to resample or not
    if np.equal(np_size, np_old_size).all() and np.equal(np_spacing, np_old_spacing).all(): return sitk_image

    new_size = tuple(np_size.astype(np.uint32).tolist())
    new_spacing = tuple(np_spacing.astype(np.float).tolist())

    # determine the new origin
    np_matrix_direction = np.array(sitk_image.GetDirection()).reshape(dim, dim)
    np_calibrated_shift = np.dot(np_matrix_direction, np_old_spacing * np_old_size / 2)
    np_center = np_old_origin + np_calibrated_shift
    np_calibrated_shift = np.dot(np_matrix_direction, np_spacing * np_size / 2)
    np_new_origin = np_center - np_calibrated_shift
    new_origin = tuple(np_new_origin.tolist())

    # determine the padding
    padding_value = 0.0
    if padding is 'min': padding_value = float(np.ndarray.min(sitk.GetArrayFromImage(sitk_image)))

    # resample sitk_image into new specs
    transform = sitk.Transform()
    return sitk.Resample(sitk_image, new_size, transform, sitk.sitkBSpline,
                         new_origin, new_spacing, sitk_image.GetDirection(),
                         padding_value, sitk_image.GetPixelID())

#------------------------------------------------------------------------------
# resampling the sitk_image with new size and spacing by preserving the spatial spacing
# applible for 2d, 3d
def resample_sitk_image_with_preserved_spatial_spacing(sitk_image,
                                                       size=None,
                                                       range=None,
                                                       padding='min'):
    """
    :param sitk_image:
    :param size:    tuple
    :param range:   tuple
    :param padding: 'zero', 'min'
    :return:
    """
    # checks
    if sitk_image == None: raise ValueError('sitk_image should not be None.')
    checks = (size is not None, range is not None)
    if True not in checks: raise ValueError('either size or spacing should be specified.')
    if padding not in ['zero', 'min']: raise ValueError('padding should be either zero or min.')

    # get properties
    dim = sitk_image.GetDimension()
    np_old_size = np.array(sitk_image.GetSize(), dtype=np.float)
    np_old_origin = np.array(sitk_image.GetOrigin(), dtype=np.float)

    # perserved spacing
    np_spacing = np.array(sitk_image.GetSpacing(), dtype=np.float)

    # calculate new size and new range
    if checks == (True, False):
        np_size = np.array(size, dtype=np.float)
    elif checks == (False, True):
        np_range = np.array(range, dtype=np.float)
        np_size = np.divide(np_range, np_spacing)
    else:
        np_size = np_old_size

    # faster performance : check whether to resample or not
    if np.equal(np_size, np_old_size).all(): return sitk_image

    new_size = tuple(np_size.astype(np.uint32).tolist())
    new_spacing = tuple(np_spacing.astype(np.float32).tolist())

    # determine the new origin
    np_matrix_direction = np.array(sitk_image.GetDirection()).reshape(dim, dim)
    np_calibrated_shift = np.dot(np_matrix_direction, np_spacing * np_old_size / 2)
    np_center = np_old_origin + np_calibrated_shift
    np_calibrated_shift = np.dot(np_matrix_direction, np_spacing * np_size / 2)
    np_new_origin = np_center - np_calibrated_shift
    new_origin = tuple(np_new_origin.tolist())

    # determine the padding
    padding_value = 0.0
    if padding is 'min': padding_value = float(np.ndarray.min(sitk.GetArrayFromImage(sitk_image)))

    # resample sitk_image into new specs
    transform = sitk.Transform()
    return sitk.Resample(sitk_image, new_size, transform, sitk.sitkBSpline,
                         new_origin, new_spacing, sitk_image.GetDirection(),
                         padding_value, sitk_image.GetPixelID())

#------------------------------------------------------------------------------
#
# test purpose
#
#------------------------------------------------------------------------------

if __name__ == '__main__':
    """
    import os
    root = 'F:\\WuhanUnionLiver\\HSOS-MRI\\nii_seg\HBP_tmp'
    pns = ['FENG_XING_HE', 'HUANG_WEI_CHENG', 'LIANG_FA_YUAN', 'LIAO_ZHENG_QUAN']
    for pn in pns:
        nii_file = os.path.join(root, pn + '_img.nii.gz')
        sitk_img = sitk.ReadImage(nii_file)
        seg_file = os.path.join(root, pn + '_seg.nii.gz')
        sitk_seg = sitk.ReadImage(seg_file)
        sitk_seg_1 = resample_sitk_image_by_reference(sitk_img, sitk_seg)
        sitk.WriteImage(sitk_seg_1, os.path.join(root, pn + '_seg.nii.gz'))
        nib_img = nib.load(os.path.join(root, pn + '_seg.nii.gz'))
        nib_img_1 = nib.Nifti1Image(nib_img.get_fdata().astype(np.int8), affine=nib_img.affine)
        nib.save(nib_img_1, os.path.join(root, pn + '_seg.nii.gz'))
    """

    import os
    resample_root = 'D:\\DICOMDB\SYUCC\\nii_images'
    tar_root = 'D:\\DICOMDB\SYUCC\\niigz_images'
    patient_names = os.listdir(resample_root)
    for patient_name in patient_names:
        print('working on %s'%(patient_name))

        patient_root = os.path.join(resample_root, patient_name)
        tarp_root = os.path.join(tar_root, patient_name)
        os.makedirs(tarp_root)

        sitk_img_ref = sitk.ReadImage(os.path.join(patient_root, 'SUV_50-60min.nii'))
        names = ['patlak_Ki_20-60min', 'patlak_intercept_20-60min']

        for name in names:
            sitk_img = sitk.ReadImage(os.path.join(patient_root, name+'.nii'))
            sitk_img_1 = resample_sitk_image_by_reference(sitk_img_ref, sitk_img)
            np_img_1 = sitk.GetArrayFromImage(sitk_img_1)
            np_img_2 = np_img_1[::-1, :, :]
            sitk_img_2 = sitk.GetImageFromArray(np_img_2)
            sitk_img_2.SetOrigin(sitk_img_ref.GetOrigin())
            sitk_img_2.SetDirection(sitk_img_ref.GetDirection())
            sitk_img_2.SetSpacing(sitk_img_ref.GetSpacing())
            sitk.WriteImage(sitk_img_2, os.path.join(os.path.join(tarp_root, name+'.nii.gz')))

        sitk.WriteImage(sitk_img_ref, os.path.join(tarp_root, 'SUV_50-60min.nii.gz'))
