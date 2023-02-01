import argparse
import numpy
import nibabel

from nibabel.processing import resample_from_to
numpy.seterr(divide='ignore', invalid='ignore')

def remap_pet_data(pet_file, mask_file, out_file, order=3, max_search=9):

    # Load the PET image data and mask:
    pet_image = nibabel.load(pet_file)
    pet_data = pet_image.get_fdata()
    mask_image = nibabel.load(mask_file)
    mask = mask_image.get_fdata().astype(bool)

    # Examine the differences in shape
    print(pet_data.shape)
    print(mask.shape)
    M1, M2, M3 = mask.shape

    # Create an empty image as a helper for mapping
    # from PET voxel space to T1 voxel space:
    shape = numpy.zeros((M1, M2, M3))
    vox2ras = mask_image.header.get_vox2ras()
    Nii = nibabel.nifti1.Nifti1Image
    helper = Nii(shape, vox2ras)
    
    print(helper.shape)

    # Resample the PET data in the T1 voxel space:
    image = resample_from_to(pet_image, helper, order=order)
    PET = image.get_fdata()
    PET = PET.reshape(M1, M2, M3,1)
    
    # Examine the new shapes
    print(PET.shape)
    print(mask.shape)

    # Zero entries outside mask
    PET[~mask] = numpy.zeros(1)

    # Create and save clean PET image in T1 voxel space:
    pet_image = Nii(PET, vox2ras)
    nibabel.save(pet_image , out_file)
    

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-pf","--petfile", type=str)      
    parser.add_argument("-mf","--maskfile", type=str) 
    parser.add_argument("-o","--output", type=str)
    parser.add_argument("-or","--order", type=int, default=3) 
    parser.add_argument("-ms","--max_search", type=int, default=9) 
    Z = parser.parse_args() 

    remap_pet_data(Z.petfile, Z.maskfile, Z.output, Z.order, Z.max_search)
