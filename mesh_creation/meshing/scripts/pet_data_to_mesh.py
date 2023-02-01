import argparse
from pickle import FALSE
import numpy
import nibabel # importing nibabel after dolfin will cause error
from nibabel.affines import apply_affine
from dolfin import *


def pet_data_to_mesh(meshfile, petfile, maskfile, outfile, label=None, order = 1):

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

	# Read in PET data in T1 voxel space
	pet_image = nibabel.load(petfile)
	pet_data = pet_image.get_fdata()

	# Transformation to voxel space from mesh coordinates
	image = nibabel.load(maskfile)
	vox2ras = image.header.get_vox2ras()
	ras2vox = numpy.linalg.inv(vox2ras)

	# Create a FEniCS tensor field:
	DG01 = FunctionSpace(mesh, "DG", order)
	PET = Function(DG01)

	# Get the coordinates xyz of each degree of freedom
	DG0 = FunctionSpace(mesh, "DG", order)
	imap = DG0.dofmap().index_map()
	num_dofs_local = (imap.local_range()[1] - imap.local_range()[0])
	xyz = DG0.tabulate_dof_coordinates()
	xyz = xyz.reshape((num_dofs_local, -1))

	# Convert to voxel space and round off to find voxel indices
	ijk = apply_affine(ras2vox, xyz).T
	i, j, k = numpy.rint(ijk).astype('int')

	# Create a matrix from the PET representation
	
	PET.vector()[:] = pet_data[i, j, k].reshape(-1)

	ones = numpy.ones(numpy.shape(PET.vector()[:]))

	PET.vector()[:] = (numpy.min(PET.vector()[:])+0.01)*ones + PET.vector()[:]
	PET.vector()[:] = PET.vector()[:]/numpy.max(PET.vector()[:])

	# Save h5 file
	mesh.scale(1e-3)
	hdf = HDF5File(mesh.mpi_comm(), outfile, 'w')
	hdf.write(mesh, "/mesh")
	hdf.write(PET, "/PET")
	hdf.close()

	# Store subdomains in XDMF for easy visualization
	xdmfname = ".".join(Z.output.split(".")[0:-1]) + "-visualization.xdmf"
	xdmf = XDMFFile(mesh.mpi_comm(), xdmfname)
	xdmf.write(PET)
	xdmf.close()

if __name__ =='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-h5","--h5file", type=str)      
	parser.add_argument("-pf","--petfile", type=str)
	parser.add_argument("-mf","--maskfile", type=str)
	parser.add_argument("-o","--output", type=str)
	parser.add_argument("-l","--label", type=bool, default=False)
	parser.add_argument("-ord","--order", type=int, default=1)
	Z = parser.parse_args() 

	pet_data_to_mesh(Z.h5file, Z.petfile, Z.maskfile, Z.output, Z.label, Z.order)
