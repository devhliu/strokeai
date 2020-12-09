
import os
import pandas as pd
import SimpleITK as sitk

from strokeai.itkprocessing.resampling import resample_sitk_image_by_reference

#------------------------------------------------------------------------------
#
# test purpose
#
#------------------------------------------------------------------------------

if __name__ == '__main__':
    project_root = 'E:\\DicomDB\\MET_Proj'
    nii_root = os.path.join(project_root, 'niix')
    roi_root = os.path.join(project_root, 'roi')

    patient_names = os.listdir(nii_root)
    roi_patient_names = os.listdir(roi_root)
    roi_patient_names_b = [roi_patient_name.replace('_', '').replace(' ', '') for roi_patient_name in roi_patient_names]

    # generate radiomics csv
    data_dict = {'ID': [], 'Image': [], 'Mask': [], 'Type': []}

    for patient_name in patient_names:
        pb = patient_name.replace('_', '').replace(' ', '')
        roi_i = 0
        for i, roi_b in enumerate(roi_patient_names_b):
            if roi_b == pb: roi_i = i

        print('working on', pb, ' ', roi_patient_names_b[roi_i])

        mk_file = os.path.join(nii_root, patient_name, 'mk.nii.gz')
        if not os.path.exists(mk_file): continue

        roi_1_file = os.path.join(roi_root, roi_patient_names[roi_i], 'ROI_1.nii')
        roi_ref_file = os.path.join(roi_root, roi_patient_names[roi_i], 'ROI_ref.nii')

        sitk_img_roi1 = sitk.ReadImage(roi_1_file)

        # resample mk
        sitk_img_mk = sitk.ReadImage(mk_file)
        mk_r_file = os.path.join(nii_root, patient_name, 'mk_r.nii.gz')
        #if not os.path.exists(mk_r_file):
        sitk_img_mk_r = resample_sitk_image_by_reference(sitk_img_roi1, sitk_img_mk)
        sitk.WriteImage(sitk_img_mk_r, mk_r_file)


        # resample rk
        rk_file = os.path.join(nii_root, patient_name, 'rk.nii.gz')
        sitk_img_md = sitk.ReadImage(rk_file)
        rk_r_file = os.path.join(nii_root, patient_name, 'rk_r.nii.gz')
        if not os.path.exists(rk_r_file):
            sitk_img_rk_r = resample_sitk_image_by_reference(sitk_img_roi1, sitk_img_md)
            sitk.WriteImage(sitk_img_rk_r, rk_r_file)


        data_dict['ID'].append(patient_name)
        data_dict['Image'].append(mk_r_file)
        data_dict['Mask'].append(roi_1_file)
        data_dict['Type'].append('mk_roi_1')

        data_dict['ID'].append(patient_name)
        data_dict['Image'].append(mk_r_file)
        data_dict['Mask'].append(roi_ref_file)
        data_dict['Type'].append('mk_roi_ref')


        data_dict['ID'].append(patient_name)
        data_dict['Image'].append(rk_r_file)
        data_dict['Mask'].append(roi_1_file)
        data_dict['Type'].append('rk_roi_1')

        data_dict['ID'].append(patient_name)
        data_dict['Image'].append(rk_r_file)
        data_dict['Mask'].append(roi_ref_file)
        data_dict['Type'].append('rk_roi_ref')


    df = pd.DataFrame(data_dict)
    df.to_csv(os.path.join(project_root, 'radiomics.csv'))
    df.to_csv(os.path.join(project_root, 'radiomics.txt'))
