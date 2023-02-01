import argparse
import numpy
import nibabel

from nibabel.processing import resample_from_to
numpy.seterr(divide='ignore', invalid='ignore')

def check_dti_data(dti_file, mask_file, order=0):
    # Load the DTI image data and mask:
    dti_image = nibabel.load(dti_file)
    dti_data = dti_image.get_fdata()

    mask_image = nibabel.load(mask_file)
    mask = mask_image.get_fdata().astype(bool)

    # Examine the differences in shape
    print(dti_data.shape)
    print(mask.shape)
    M1, M2, M3 = mask.shape

    # Create an empty image as a helper for mapping
    # from DTI voxel space to T1 voxel space:
    shape = numpy.zeros((M1, M2, M3, 9))
    vox2ras = mask_image.header.get_vox2ras()
    Nii = nibabel.nifti1.Nifti1Image
    helper = Nii(shape, vox2ras)

    # Resample the DTI data in the T1 voxel space:
    image = resample_from_to(dti_image, helper, order=order)
    D = image.get_fdata()
    print(D.shape)

    # Reshape D from M1 x M2 x M3 x 9 into a N x 3 x 3:
    D = D.reshape(-1, 3, 3)

    # Compute eigenvalues and eigenvectors
    lmbdas, v = numpy.linalg.eigh(D)

    # Compute fractional anisotropy (FA)
    FA = compute_FA(lmbdas)

    # Define valid entries as those where all eigenvalues are
    # positive and FA is between 0 and 1
    positives = (lmbdas[:,0]>0)*(lmbdas[:,1]>0)*(lmbdas[:,2]>0)
    valid = positives*(FA < 1.0)*(FA > 0.0)
    valid = valid.reshape((M1, M2, M3))

    # Find all voxels with invalid tensors within the mask
    ii, jj, kk = numpy.where((~valid)*mask)
    print("Number of invalid tensor voxels")
    print("in the mask ROI: ", len(ii))

    # Reshape D from N x 3 x 3 to M1 x M2 x M3 x 9
    D = D.reshape((M1,M2,M3,9))

    return valid, mask, D

def compute_FA(lmbdas):
    MD = (lmbdas[:,0] + lmbdas[:,1] + lmbdas[:,2])/3.
    FA2 = (3./2.)*((lmbdas[:, 0]-MD)**2+(lmbdas[:,1]-MD)**2
                  +(lmbdas[:,2]-MD)**2)/(lmbdas[:,0]**2 + lmbdas[:,1]**2 + lmbdas[:,2]**2)
    FA = numpy.sqrt(FA2)
    return FA

def find_valid_adjacent_tensor(data,i,j,k, max_iter):
    # Start at 1, since 0 is an invalid tensor
    for m in range(1, max_iter+1) :
        # Extract the adjacent data to voxel i, j, k
        # and compute the mean diffusivity.
        A = data[i-m:i+m+1, j-m:j+m+1, k-m:k+m+1,:]
        A = A.reshape(-1, 9)
        MD = (A[:, 0]+ A[:, 4] + A[:,8])/3.

        # If valid tensor is found:
        if MD.sum() > 0.0:
            # Find index of the median valid tensor, and return
            # corresponding tensor.
            index = (numpy.abs(MD - numpy.median(MD[MD>0]))).argmin ()
            return A[index]

    print("Failed to find valid tensor")
    return data[i, j, k]

def clean_dti_data(dti_file, mask_file, out_file, order=3, max_search=9):

    valid, mask, D = check_dti_data(dti_file, mask_file, order=order)

    # Zero out "invalid" tensor entries outside mask,
    # and extrapolate from valid neighbors
    D[~mask] = numpy.zeros(9)
    D[(~valid)*mask] = numpy.zeros(9)
    ii, jj, kk = numpy.where((~valid)*mask)
    for i, j, k in zip(ii, jj, kk):
        D[i, j, k, :] = \
        find_valid_adjacent_tensor(D, i, j, k, max_search)

    # Create and save clean DTI image in T1 voxel space:
    mask_image = nibabel.load(mask_file)
    M1, M2, M3 = mask.shape
    shape = numpy.zeros((M1, M2, M3, 9))
    vox2ras = mask_image.header.get_vox2ras()
    Nii = nibabel.nifti1.Nifti1Image
    dti_image = Nii(D, vox2ras)
    nibabel.save(dti_image , out_file)

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-df","--dtifile", type=str)      
    parser.add_argument("-mf","--maskfile", type=str) 
    parser.add_argument("-o","--output", type=str)
    parser.add_argument("-or","--order", type=int, default=3) 
    parser.add_argument("-ms","--max_search", type=int, default=9) 
    Z = parser.parse_args() 

    clean_dti_data(Z.dtifile, Z.maskfile, Z.output, Z.order, Z.max_search)
