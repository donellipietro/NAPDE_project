import argparse
from pickle import FALSE
import numpy
import nibabel # importing nibabel after dolfin will cause error
from nibabel.affines import apply_affine
from dolfin import *

def adjusting_mean_diffusivity(Dtensor, subdomains_array, tags_with_limits) :
    # Computes the mean diffusivity for each degree of freedom
    MD = (Dvector[:,0]+Dvector[:,4]+Dvector[:,8])/3.

    # Reads the tag and the minimum and maximum mean diffusivity limit
    # for that tag subdomain.
    for tag,mn,mx in tags_with_limits:
        # If the minimum or maximum mean diffusivity limit is set to zero,
        # then the limit is considered void.
        usr_max = float(mx) if mx!=0 else numpy.inf
        usr_min = float(mn) if mn!=0 else -numpy.inf

        # creates a mask for all degrees of freesom that are within the
        # subdomain with the tag and is above the maximum limit or
        # below the minimum limit.
        max_mask = (subdomains.array()==tag)*(MD>usr_max)
        min_mask = (subdomains.array()==tag)*(MD<usr_min)

        # Sets values that are either above or below limits to the closest limit.
        Dvector[max_mask]=usr_max*numpy.divide(Dvector[max_mask],MD[max_mask,numpy.newaxis])
        Dvector[min_mask]=usr_min*numpy.divide(Dvector[min_mask],MD[min_mask,numpy.newaxis])

def dti_data_to_mesh(meshfile, dtifile, maskfile, outfile_n, outfile_D, label=None):

	# Read the mesh from file. The mesh coordinates define the Surface RAS space.
	mesh = Mesh ()
	hdf = HDF5File(mesh.mpi_comm(), meshfile , "r")
	hdf.read(mesh, "/mesh", False)
	mesh.scale(1e3)

	# Read subdomains and boundary markers to write output
	d = mesh.topology().dim()
	#subdomains = MeshFunction("size_t", mesh, d)
	#hdf.read(subdomains, "/subdomains")
	#boundaries = MeshFunction("size_t", mesh, d-1)
	#hdf.read(boundaries, "/boundaries")
	hdf.close()

	# Read in DTI data in T1 voxel space (see previous function, e.g. ernie-dti-clean.mgz)
	dti_image = nibabel.load(dtifile)
	dti_data = dti_image.get_fdata()

	# Transformation to voxel space from mesh coordinates
	image = nibabel.load(maskfile)
	vox2ras = image.header.get_vox2ras()
	ras2vox = numpy.linalg.inv(vox2ras)

	# Create a FEniCS tensor field:
	DG09 = TensorFunctionSpace(mesh, "DG", 0)
	DG03 = VectorFunctionSpace(mesh, "DG", 0)
	D = Function(DG09)
	n_vec = Function(DG03)

	# Get the coordinates xyz of each degree of freedom
	DG0 = FunctionSpace(mesh, "DG", 0)
	imap = DG0.dofmap().index_map()
	num_dofs_local = (imap.local_range()[1] - imap.local_range()[0])
	xyz = DG0.tabulate_dof_coordinates()
	xyz = xyz.reshape((num_dofs_local, -1))

	# Convert to voxel space and round off to find voxel indices
	ijk = apply_affine(ras2vox, xyz).T
	i, j, k = numpy.rint(ijk).astype('int')

	# Create a matrix from the DTI representation
	D1 = dti_data[i, j, k]
	n1 = dti_data[i, j, k]
	n1 = n1[:,0:3]
	print(n1.shape)
	for ii in range(0,D1.shape[0]):
		Dapp = D1[ii,:]
		Dapp = Dapp.reshape(3,3)
		l, v = numpy.linalg.eig(Dapp)
		n = v[:,l.argmax()]
		n1[ii,:] = n
		Dapp = numpy.tensordot(n,n,axes = 0)
		D1[ii,:] = Dapp.reshape(-1)

	print(n1.shape)
	print(n1.reshape(-1).shape)

	n_vec.vector()[:] = n1.reshape(-1)
	D.vector()[:] = D1.reshape(-1)
	# Compute other functions

	# Rescale mm -> m
	mesh.scale(1e-3)

	# Save h5 file for N
	hdf = HDF5File(mesh.mpi_comm(), outfile_n, 'w')
	hdf.write(mesh, "/mesh")
	hdf.write(n_vec, "/N")
	hdf.close()

	# Store subdomains in XDMF for easy visualization
	xdmfname = ".".join(outfile_n.split(".")[0:-1]) + "-visualization.xdmf"
	xdmf = XDMFFile(mesh.mpi_comm(), xdmfname)
	xdmf.write(n_vec)
	xdmf.close()

	# Save h5 file for N
	hdf = HDF5File(mesh.mpi_comm(), outfile_D, 'w')
	hdf.write(mesh, "/mesh")
	hdf.write(D, "/axonal_diffusion")
	hdf.close()

	# Store subdomains in XDMF for easy visualization
	xdmfname = ".".join(outfile_D.split(".")[0:-1]) + "-visualization.xdmf"
	xdmf = XDMFFile(mesh.mpi_comm(), xdmfname)
	xdmf.write(D)
	xdmf.close()

	

if __name__ =='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-h5","--h5file", type=str)      
	parser.add_argument("-df","--dtifile", type=str)
	parser.add_argument("-mf","--maskfile", type=str) 
	parser.add_argument("-o_n","--output_n", type=str)
	parser.add_argument("-o_D","--output_D", type=str)
	parser.add_argument("-l","--label", type=bool, default=False) 
	Z = parser.parse_args() 

	dti_data_to_mesh(Z.h5file, Z.dtifile, Z.maskfile, Z.output_n, Z.output_D, Z.label)
