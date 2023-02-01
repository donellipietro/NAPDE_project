FROM pietrodonelli/ubuntu_mardal:latest

WORKDIR /project
COPY copy.sh .

# Directories

## Scripts
ENV SCRIPTS=scripts
RUN mkdir -p $SCRIPTS
COPY scripts $SCRIPTS

## Data
ENV DIR_DATA=data
RUN mkdir -p $DIR_DATA

### Origin
ENV ORIGIN=data/origin
ENV ORIGIN_MRI="${ORIGIN}/mri"
ENV ORIGIN_DTI="${ORIGIN}/dti"
ENV ORIGIN_PET="${ORIGIN}/pet"
RUN mkdir -p $ORIGIN
RUN mkdir -p $ORIGIN_MRI
RUN mkdir -p $ORIGIN_DTI
RUN mkdir -p $ORIGIN_PET
# COPY origin/mri_orig $ORIGIN_MRI
# COPY origin/dti_orig $ORIGIN_DTI
# COPY origin/pet_orig $ORIGIN_PET

### Surface
ENV SURFACE=data/surface
ENV SURFACE_ORIGIN=$SURFACE/origin
ENV SURFACE_REMESH=$SURFACE/remesh
ENV SURFACE_SMOOTH=$SURFACE/smooth
ENV SURFACE_REPAIR=$SURFACE/repair
RUN mkdir -p $SURFACE
RUN mkdir -p $SURFACE_ORIGIN
RUN mkdir -p $SURFACE_REMESH
RUN mkdir -p $SURFACE_SMOOTH
RUN mkdir -p $SURFACE_REPAIR
COPY origin/surfaces $SURFACE_ORIGIN

### MRI
ENV MRI=data/mri
RUN mkdir -p $MRI
COPY origin/mri $MRI

### DTI
ENV DTI=data/dti
RUN mkdir -p $DTI
COPY origin/dti $DTI

### PET
ENV PET=data/pet
RUN mkdir -p $PET
COPY origin/pet $PET

### Mesh
ENV MESH=data/mesh
RUN mkdir -p $MESH


# Variables

## Files name
ENV PIAL=pial
ENV WHITE=white
ENV VENTRICLES=ventricles

## Extensions
ENV SURFACE_EXT=.stl
ENV MESH_EXT=.mesh
ENV MESH_FENICS_EXT=.h5
ENV MESH_PARAVIEW_EXT=.xdmf
ENV MESH_TAG_EXT=.vtu


# Meshing

## Remeshing
## -> remesh_surface(stl_input, output, L, n, do_not_move_boundary_edges=False)

ENV L=1.0
ENV n=3

### Pial
ENV FILE_NAME=$PIAL
ENV stl_input=$SURFACE_ORIGIN/$FILE_NAME$SURFACE_EXT
ENV output=$SURFACE_REMESH/$FILE_NAME.remesh$SURFACE_EXT
RUN python3 $SCRIPTS/remesh_surface.py --stl_input $stl_input --output $output --L $L --n $n

### White
ENV FILE_NAME=$WHITE
ENV stl_input=$SURFACE_ORIGIN/$FILE_NAME$SURFACE_EXT
ENV output=$SURFACE_REMESH/$FILE_NAME.remesh$SURFACE_EXT
RUN python3 $SCRIPTS/remesh_surface.py --stl_input $stl_input --output $output --L $L --n $n

### Ventricles
ENV FILE_NAME=$VENTRICLES
ENV stl_input=$SURFACE_ORIGIN/$FILE_NAME$SURFACE_EXT
ENV output=$SURFACE_REMESH/$FILE_NAME.remesh$SURFACE_EXT
RUN python3 $SCRIPTS/remesh_surface.py --stl_input $stl_input --output $output --L $L --n $n

## Smoothing
## -> smoothen_surface(stl_input, output, n=1, eps=1.0, preserve_volume=True)

ENV n=3
ENV eps=1.5

### Pial
ENV FILE_NAME=$PIAL
ENV stl_input=$SURFACE_REMESH/$FILE_NAME.remesh$SURFACE_EXT
ENV output=$SURFACE_SMOOTH/$FILE_NAME.smooth$SURFACE_EXT
RUN python3 $SCRIPTS/smoothen_surface.py --stl_input $stl_input --output $output --n $n --eps $eps

### White
ENV FILE_NAME=$WHITE
ENV stl_input=$SURFACE_REMESH/$FILE_NAME.remesh$SURFACE_EXT
ENV output=$SURFACE_SMOOTH/$FILE_NAME.smooth$SURFACE_EXT
RUN python3 $SCRIPTS/smoothen_surface.py --stl_input $stl_input --output $output --n $n --eps $eps

### Ventricles
ENV FILE_NAME=$VENTRICLES
ENV stl_input=$SURFACE_REMESH/$FILE_NAME.remesh$SURFACE_EXT
ENV output=$SURFACE_SMOOTH/$FILE_NAME.smooth$SURFACE_EXT
RUN python3 $SCRIPTS/smoothen_surface.py --stl_input $stl_input --output $output --n $n --eps $eps


## Preventing intersections and missing facets
## -> repaired_surface(stl_input, output)

### Pial
ENV FILE_NAME=$PIAL
ENV stl_input=$SURFACE_SMOOTH/$FILE_NAME.smooth$SURFACE_EXT
ENV output=$SURFACE_REPAIR/$FILE_NAME.repair$SURFACE_EXT
RUN python3 $SCRIPTS/repaired_surface.py --stl_input $stl_input --output $output

### White
ENV FILE_NAME=$WHITE
ENV stl_input=$SURFACE_SMOOTH/$FILE_NAME.smooth$SURFACE_EXT
ENV output=$SURFACE_REPAIR/$FILE_NAME.repair$SURFACE_EXT
RUN python3 $SCRIPTS/repaired_surface.py --stl_input $stl_input --output $output

### Ventricles
ENV FILE_NAME=$VENTRICLES
ENV stl_input=$SURFACE_SMOOTH/$FILE_NAME.smooth$SURFACE_EXT
ENV output=$SURFACE_REPAIR/$FILE_NAME.repair$SURFACE_EXT
RUN python3 $SCRIPTS/repaired_surface.py --stl_input $stl_input --output $output


## Mesh creation: single regions of the brain
## -> create_volume_mesh(stlfile, output, resolution=8)

ENV resolution=8

### Pial
ENV FILE_NAME=$PIAL
ENV stl_input=$SURFACE_REPAIR/$FILE_NAME.repair$SURFACE_EXT
ENV output=$MESH/$FILE_NAME$MESH_EXT
RUN python3 $SCRIPTS/create_volume_mesh.py --stl_input $stl_input --output $output --resolution $resolution

### White
ENV FILE_NAME=$WHITE
ENV stl_input=$SURFACE_REPAIR/$FILE_NAME.repair$SURFACE_EXT
ENV output=$MESH/$FILE_NAME$MESH_EXT
RUN python3 $SCRIPTS/create_volume_mesh.py --stl_input $stl_input --output $output --resolution $resolution

### Ventricles
ENV FILE_NAME=$VENTRICLES
ENV stl_input=$SURFACE_REPAIR/$FILE_NAME.repair$SURFACE_EXT
ENV output=$MESH/$FILE_NAME$MESH_EXT
RUN python3 $SCRIPTS/create_volume_mesh.py --stl_input $stl_input --output $output --resolution $resolution


## Tagged meshes

# ENV MESH_NAMES "gray_white" "gray_ventricles" "white_ventricles" "gray_white_ventricles"

## Mesh creation: whole brain tagged by cuples of regions
## -> create_two_domain_tagged_mesh(ext_stl, inn_stl, output, resolution=8)

ENV resolution=8 

### gw
ENV FILE_NAME_ext=$PIAL
ENV FILE_NAME_inn=$WHITE
ENV stl_input_ext=$SURFACE_REPAIR/$FILE_NAME_ext.repair$SURFACE_EXT
ENV stl_input_inn=$SURFACE_REPAIR/$FILE_NAME_inn.repair$SURFACE_EXT
# ENV FILE_NAME_out=$MESH_NAMES[1]
ENV FILE_NAME_out=gray_white
ENV output=$MESH/$FILE_NAME_out$MESH_EXT
# RUN python3 $SCRIPTS/create_two_domain_tagged_mesh.py --stl_input_ext $stl_input_ext --stl_input_inn $stl_input_inn --output $output --resolution $resolution

### gv
ENV FILE_NAME_ext=$PIAL
ENV FILE_NAME_inn=$VENTRICLES
ENV stl_input_ext=$SURFACE_REPAIR/$FILE_NAME_ext.repair$SURFACE_EXT
ENV stl_input_inn=$SURFACE_REPAIR/$FILE_NAME_inn.repair$SURFACE_EXT
# ENV FILE_NAME_out=$MESH_NAMES[2]
ENV FILE_NAME_out=gray_ventricles
ENV output=$MESH/$FILE_NAME_out$MESH_EXT
RUN python3 $SCRIPTS/create_two_domain_tagged_mesh.py --stl_input_ext $stl_input_ext --stl_input_inn $stl_input_inn --output $output --resolution $resolution --remove_inn True

### wv
ENV FILE_NAME_ext=$WHITE
ENV FILE_NAME_inn=$VENTRICLES
ENV stl_input_ext=$SURFACE_REPAIR/$FILE_NAME_ext.repair$SURFACE_EXT
ENV stl_input_inn=$SURFACE_REPAIR/$FILE_NAME_inn.repair$SURFACE_EXT
# ENV FILE_NAME_out=$MESH_NAMES[3]
ENV FILE_NAME_out=white_ventricles
ENV output=$MESH/$FILE_NAME_out$MESH_EXT
# RUN python3 $SCRIPTS/create_two_domain_tagged_mesh.py --stl_input_ext $stl_input_ext --stl_input_inn $stl_input_inn --output $output --resolution $resolution


## Mesh creation: whole brain tagged by gwv
## -> create_three_domain_tagged_mesh(pial_stl, white_stl, ventricles_stl, output, resolution=8, remove_ventricles=False)

ENV resolution=8 
# ENV remove_ventricles=True -> -rv $remove_ventricles

ENV stl_input_p=$SURFACE_REPAIR/$PIAL.repair$SURFACE_EXT
ENV stl_input_w=$SURFACE_REPAIR/$WHITE.repair$SURFACE_EXT
ENV stl_input_v=$SURFACE_REPAIR/$VENTRICLES.repair$SURFACE_EXT
# ENV FILE_NAME_out=$MESH_NAMES[4]
ENV FILE_NAME_out=gray_white_ventricles
ENV output=$MESH/$FILE_NAME_out$MESH_EXT
# RUN python3 $SCRIPTS/create_three_domain_tagged_mesh.py -sip $stl_input_p -siw $stl_input_w -siv $stl_input_v -o $output -r $resolution


## Converting meshes and mesh data between different formats
## -> write_mesh_to_xdmf(meshfile, xdmfdir)
## -> write_xdmf_to_h5(xdmfdir, hdf5file)
## -> meshio-convert meshfile xdmffile or meshio-convert meshfile vtufile

# "gray_white" "gray_ventricles" "white_ventricles" "gray_white_ventricles"

### tmp directory creation
ENV xdmfdir=$MESH/tmp
RUN mkdir $xdmfdir

RUN apt update
RUN apt install -y meshio-tools

### g
ENV FILE_NAME=$PIAL
ENV meshfile=$MESH/$FILE_NAME$MESH_EXT
ENV xdmffile=$MESH/$FILE_NAME$MESH_PARAVIEW_EXT
ENV hdf5file=$MESH/$FILE_NAME.fenics$MESH_FENICS_EXT
RUN meshio-convert $meshfile $xdmffile
RUN python3 $SCRIPTS/convert_to_dolfin_mesh.py --meshfile $meshfile --hdf5file $hdf5file --xdmfdir $xdmfdir

### w
ENV FILE_NAME=$WHITE
ENV meshfile=$MESH/$FILE_NAME$MESH_EXT
ENV xdmffile=$MESH/$FILE_NAME$MESH_PARAVIEW_EXT
ENV hdf5file=$MESH/$FILE_NAME.fenics$MESH_FENICS_EXT
RUN meshio-convert $meshfile $xdmffile 
RUN python3 $SCRIPTS/convert_to_dolfin_mesh.py --meshfile $meshfile --hdf5file $hdf5file --xdmfdir $xdmfdir

### v
ENV FILE_NAME=$VENTRICLES
ENV meshfile=$MESH/$FILE_NAME$MESH_EXT
ENV xdmffile=$MESH/$FILE_NAME$MESH_PARAVIEW_EXT
ENV hdf5file=$MESH/$FILE_NAME.fenics$MESH_FENICS_EXT
RUN meshio-convert $meshfile $xdmffile 
RUN python3 $SCRIPTS/convert_to_dolfin_mesh.py --meshfile $meshfile --hdf5file $hdf5file --xdmfdir $xdmfdir

### gw
# ENV FILE_NAME=$MESH_NAMES[1]
ENV FILE_NAME=gray_white
ENV meshfile=$MESH/$FILE_NAME$MESH_EXT
ENV vtufile=$MESH/$FILE_NAME$MESH_TAG_EXT
ENV hdf5file=$MESH/$FILE_NAME.fenics$MESH_FENICS_EXT
# RUN meshio-convert $meshfile $vtufile 
# RUN python3 $SCRIPTS/convert_to_dolfin_mesh.py --meshfile $meshfile --hdf5file $hdf5file --xdmfdir $xdmfdir

### gv
# ENV FILE_NAME=$MESH_NAMES[2]
ENV FILE_NAME=gray_ventricles
ENV meshfile=$MESH/$FILE_NAME$MESH_EXT
ENV vtufile=$MESH/$FILE_NAME$MESH_TAG_EXT
ENV hdf5file=$MESH/$FILE_NAME.fenics$MESH_FENICS_EXT
RUN meshio-convert $meshfile $vtufile 
RUN python3 $SCRIPTS/convert_to_dolfin_mesh.py --meshfile $meshfile --hdf5file $hdf5file --xdmfdir $xdmfdir

### wv
# ENV FILE_NAME=$MESH_NAMES[3]
ENV FILE_NAME=white_ventricles
ENV meshfile=$MESH/$FILE_NAME$MESH_EXT
ENV vtufile=$MESH/$FILE_NAME$MESH_TAG_EXT
ENV hdf5file=$MESH/$FILE_NAME.fenics$MESH_FENICS_EXT
# RUN meshio-convert $meshfile $vtufile 
# RUN python3 $SCRIPTS/convert_to_dolfin_mesh.py --meshfile $meshfile --hdf5file $hdf5file --xdmfdir $xdmfdir

### gwv
# ENV FILE_NAME=$MESH_NAMES[4]
ENV FILE_NAME=gray_white_ventricles
ENV meshfile=$MESH/$FILE_NAME$MESH_EXT
ENV vtufile=$MESH/$FILE_NAME$MESH_TAG_EXT
ENV hdf5file=$MESH/$FILE_NAME.fenics$MESH_FENICS_EXT
# RUN meshio-convert $meshfile $vtufile 
# RUN python3 $SCRIPTS/convert_to_dolfin_mesh.py --meshfile $meshfile --hdf5file $hdf5file --xdmfdir $xdmfdir

### remove tmp directory
RUN rm $xdmfdir -r


## Add parcellations
## -> add_parcellations(parcfile, h5file, output, add=none)

ENV parcfile=$MRI/mri/wmparc.mgz
#ENV add="17 53 1028 2028 1035 2035 3028 4028 3035 4035" ->  --add $add

# 17 Left-Hippocampus
# 53 Right-Hippocampus
# 1028 ctx-lh-superiorfrontal
# 2028 ctx-rh-superiorfrontal
# 1035 ctx-lh-insula
# 2035 ctx-rh-insula
# 3028 wm-lh-superiorfrontal
# 4028 wm-rh-superiorfrontal
# 3035 wm-lh-insula
# 4035 wm-rh-insula

# Pial
ENV FILE_NAME=$PIAL
ENV h5file=$MESH/$FILE_NAME".fenics"$MESH_FENICS_EXT
ENV output=$MESH/$FILE_NAME".parc"$MESH_FENICS_EXT
# RUN python3 $SCRIPTS/add_parcellations.py --h5file $h5file --parcfile $parcfile --output $output

# White
ENV FILE_NAME=$WHITE
ENV h5file=$MESH/$FILE_NAME".fenics"$MESH_FENICS_EXT
ENV output=$MESH/$FILE_NAME".parc"$MESH_FENICS_EXT
# RUN python3 $SCRIPTS/add_parcellations.py --h5file $h5file --parcfile $parcfile --output $output

# Ventricles
ENV FILE_NAME=$VENTRICLES
ENV h5file=$MESH/$FILE_NAME".fenics"$MESH_FENICS_EXT
ENV output=$MESH/$FILE_NAME".parc"$MESH_FENICS_EXT
# RUN python3 $SCRIPTS/add_parcellations.py --h5file $h5file --parcfile $parcfile --output $output

# DTI projection

## Clean DTI data
ENV dtifile=$DTI/tensor.nii.gz
ENV maskfile=$MRI/mri/mask.mgz
ENV output=$DTI/tensor-clean.nii
RUN python3 $SCRIPTS/clean_dti_data.py --dtifile $dtifile --maskfile $maskfile --output $output

## DTI data to DTI normal
ENV h5file=$MESH/gray_ventricles.fenics.h5
ENV dtifile=$DTI/tensor-clean.nii
ENV maskfile=$MRI/mri/mask.mgz
ENV output_n=$MESH/N.h5
ENV output_D=$MESH/axonal_diffusion.h5
RUN python3 $SCRIPTS/dti_data_to_normal.py -h5 $h5file -df $dtifile -mf $maskfile -o_n $output_n -o_D $output_D

# PET projection

ENV petfile=$PET/template_AV45.nii.gz
ENV maskfile=$MRI/mri/mask.mgz
ENV output=$PET/template_AV45-remapped.nii
RUN python3 $SCRIPTS/remap_pet_data.py --petfile $petfile --maskfile $maskfile --output $output

ENV h5file=$MESH/gray_ventricles.fenics.h5
ENV petfile=$PET/template_AV45-remapped.nii
ENV maskfile=$MRI/mri/mask.mgz
ENV output=$MESH/PET_AV45.h5
ENV order=1
RUN python3 $SCRIPTS/pet_data_to_mesh.py -h5 $h5file -pf $petfile -mf $maskfile -o $output -ord $order