import argparse
from pickle import FALSE
import numpy
import nibabel # importing nibabel after dolfin will cause error
from dolfin import *

def write_mesh_to_xdmf(meshfile, xdmfdir):
    import meshio
    # Read the .mesh file into meshio 
    mesh = meshio.read(meshfile)

    # Extract subdomains and boundaries between regions
    # into appropriate containers
    points = mesh.points
    tetra  = {"tetra": mesh.cells_dict["tetra"]}
    triangles = {"triangle": mesh.cells_dict["triangle"]} 
    subdomains = {"subdomains": [mesh.cell_data_dict["medit:ref"]["tetra"]]}
    boundaries = {"boundaries": [mesh.cell_data_dict["medit:ref"]["triangle"]]}
    
    # Write the mesh to xdmfdir/mesh.xdmf 
    xdmf = meshio.Mesh(points, tetra) 
    meshio.write("%s/mesh.xdmf" % xdmfdir, xdmf)
    
    # Write the subdomains of the mesh 
    xdmf = meshio.Mesh(points, tetra, cell_data=subdomains)
    meshio.write("%s/subdomains.xdmf" % xdmfdir, xdmf)
    
    # Write the boundaries/interfaces of the mesh
    xdmf = meshio.Mesh(points, triangles,cell_data=boundaries)
    meshio.write("%s/boundaries.xdmf" % xdmfdir, xdmf)
    
def write_xdmf_to_h5(xdmfdir, hdf5file):

    # Read .xdmf mesh into a FEniCS Mesh
    mesh = Mesh()
    with XDMFFile("%s/mesh.xdmf" % xdmfdir) as infile:
        infile.read(mesh)
        
    # Read cell data to a MeshFunction (of dim n)
    n = mesh.topology().dim()
    subdomains = MeshFunction("size_t", mesh, n)
    with XDMFFile("%s/subdomains.xdmf" % xdmfdir) as infile:
        infile.read(subdomains, "subdomains")
        
    # Read facet data to a MeshFunction (of dim n-1)
    boundaries = MeshFunction("size_t", mesh, n-1, 0)
    with XDMFFile("%s/boundaries.xdmf" % xdmfdir) as infile:
        infile.read(boundaries, "boundaries")

    # Write all files into a single h5 file.
    mesh.scale(1e-3)
    hdf = HDF5File(mesh.mpi_comm(), hdf5file, "w")
    hdf.write(mesh, "/mesh")
    hdf.write(subdomains, "/subdomains")
    hdf.write(boundaries, "/boundaries") 
    hdf.close()

    # Store subdomains in XDMF for easy visualization
    xdmfname = ".".join(hdf5file.split(".")[0:-1]) + "-visualization.xdmf"
    xdmf = XDMFFile(mesh.mpi_comm(), xdmfname)
    xdmf.write(boundaries)
    xdmf.close()

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--meshfile', type=str)      
    parser.add_argument('--hdf5file', type=str) 
    parser.add_argument('--xdmfdir', type=str, default="tmp") 
    Z = parser.parse_args() 

    write_mesh_to_xdmf(Z.meshfile, Z.xdmfdir) 
    write_xdmf_to_h5(Z.xdmfdir, Z.hdf5file) 
