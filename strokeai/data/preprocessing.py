

import os
import nibabel as nib
import pandas as pd
import numpy as np


#------------------------------------------------------------------------------
#
def read_mask(subject_id, root):
    """
    :param subject_id:
    :param root:
    :return:
    """
    group_subroot_0 = subject_id[:5]
    group_subroot_1 = subject_id
    nii_filename = subject_id + '_LesionSmooth_stx.nii.gz'
    nii_file = os.path.join(root, group_subroot_0, group_subroot_1, nii_filename)
    if not os.path.exists(nii_file): return None
    nib_img = nib.load(nii_file)
    return nib_img.get_fdata()
#-----------------------------------------------------------------------------
#




#------------------------------------------------------------------------------
#
# test purpose
#
#------------------------------------------------------------------------------

if __name__ == '__main__':
    project_root = 'D:\\ATLAS_v33\\ATLAS_R_1p2'
    nii_root = os.path.join(project_root, 'standard_MNI')
    nib_mni = nib.load(os.path.join(nii_root, 'standard_mni152.nii.gz'))
    np_mni = nib_mni.get_fdata()
    np_init = np.zeros(np_mni.shape, dtype=np.float)
    df = pd.read_excel(os.path.join(project_root, '20171106_ATLAS_Meta-Data_Release_1.1_Updated-v1.xlsx'))
    subids = df['Subject ID'].values
    vascularts = df['Vascular territory'].values
    vkey = 'SCA'
    i = 0
    for sub_id, vasculart in zip(subids, vascularts):
        if vasculart == vkey:
            np_tmp = read_mask(sub_id, nii_root)
            if np_tmp is None: continue
            np_init += np_tmp
            i += 1
    nib_init = nib.Nifti1Image(np_init/i, affine=nib_mni.affine)
    nib.save(nib_init, os.path.join(nii_root, vkey + '.nii.gz'))