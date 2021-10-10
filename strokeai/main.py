# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import subprocess
from glob import glob


#----------------------------------------------------------------------------------------------
#
def convert2dki(dcm_root, niix_root):
    """
    :param dcm_root:
    :param niix_root:
    :return:
    """
    patient_names = os.listdir(dcm_root)
    for patient_name in patient_names:
        #print(patient_name)
        new_patient_name = patient_name.replace('__', '_')
        dki_roots = glob(os.path.join(dcm_root, patient_name, '*', '*DKI_NODDI_0*'))
        dki_roots += glob(os.path.join(dcm_root, patient_name, '*', '*DTI_0*'))
        dki_roots += glob(os.path.join(dcm_root, patient_name, '*', '*DTI_2*'))
        if len(dki_roots) == 0:
            print('failed ... ' + patient_name)
            continue
        output_root = os.path.join(niix_root, new_patient_name)
        if os.path.exists(os.path.join(output_root, new_patient_name + '.nii.gz')): continue
        os.makedirs(output_root, exist_ok=True)
        subprocess.call(['dcm2niix', '-f', 'dki', '-o', output_root, dki_roots[0]])
    return

#----------------------------------------------------------------------------------------------
#
def calc_dki_metrics(sub_root):
    """
    :param sub_root:
    :return:
    """
    patient_name = os.path.basename(sub_root)
    print('working on %s'%(patient_name))
    try:
        dki_file = os.path.join(sub_root, 'dki.nii.gz')
        dki_mask_file = os.path.join(sub_root, 'dki_mask.nii.gz')
        dki_denoised_file = os.path.join(sub_root, 'dki_denoised.nii.gz')
        dki_gibbs_file = os.path.join(sub_root, 'dki_denoised_gibbs.nii.gz')
        mk_file = os.path.join(sub_root, 'mk.nii.gz')
        bvals = os.path.join(sub_root, 'dki.bval')
        bvecs = os.path.join(sub_root, 'dki.bvec')
        #subprocess.call(['dwi2mask', '-fslgrad', bvecs, bvals, dki_file, dki_mask_file])
        subprocess.call(['dwidenoise', '-mask', dki_mask_file, dki_file, dki_denoised_file])
        """
        subprocess.call(['dipy_fit_dki',
                         '--out_dir', sub_root, '--out_fa', 'fa.nii.gz', '--out_ga', 'ga.nii.gz',
                         '--out_md', 'md.nii.gz', '--out_ad', 'ad.nii.gz', '--out_rd', 'rd.nii.gz',
                         '--out_mk', 'mk.nii.gz', '--out_ak', 'ak.nii.gz', '--out_rk', 'rk.nii.gz',
                         dki_denoised_file, bvals, bvecs, dki_mask_file])
        """
        """
        if not os.path.exists(dki_denoised_file):
            
            subprocess.call(['dipy_denoise_lpca.bat', '--pca_method', 'eig',
                             '--out_dir', sub_root, '--out_denoised', 'dki_denoised.nii.gz',
                             dki_file, bvals, bvecs])
            
            subprocess.call(['dipy_denoise_nlmeans.bat', '--rician',
                             '--out_dir', sub_root, '--out_denoised', 'dki_denoised.nii.gz',
                             dki_file])
        """
        if not os.path.exists(dki_gibbs_file):
            subprocess.call(['dipy_gibbs_ringing',
                             '--out_dir', sub_root, '--out_unring', 'dki_denoised_gibbs.nii.gz',
                             dki_denoised_file])
        if not os.path.exists(mk_file):
            subprocess.call(['dipy_fit_dki',
                             '--out_dir', sub_root, '--force',
                             dki_gibbs_file, bvals, bvecs, dki_mask_file])
    except:
        print('failed to calculate %s'%(patient_name))
    return 0
#----------------------------------------------------------------------------------------------
#
# Test Purpose
#
#----------------------------------------------------------------------------------------------
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #project_root = 'E:\\DicomDB\\MET_Proj'
    project_root = '/mnt/e/DicomDB/MET_proj'
    niix_root = os.path.join(project_root, 'niix')
    patient_subrootnames = os.listdir(niix_root)
    for patient_subrootname in patient_subrootnames:
        patient_root = os.path.join(niix_root, patient_subrootname)
        calc_dki_metrics(patient_root)