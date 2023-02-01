export FREESURFER_HOME=/Applications/freesurfer
export SUBJECTS_DIR=origin_meshing/
source $FREESURFER_HOME/SetUpFreeSurfer.sh

export ORIGIN_EXTRACTION=origin_extraction/pet
export ORIGIN_MESH=origin_meshing/pet

mri_concat $ORIGIN_EXTRACTION/pet_AV45.nii.gz --mean --o $ORIGIN_MESH/template_AV45.nii.gz
mri_coreg --s mri --mov $ORIGIN_MESH/template_AV45.nii.gz --reg $ORIGIN_MESH/template_AV45.reg.lta --threads 4
# tkregisterfv --mov $ORIGIN_MESH/template_AV54.nii.gz --reg $ORIGIN_MESH/template_AV45.reg.lta --surfs

mri_concat $ORIGIN_EXTRACTION/pet_PIB.nii.gz --mean --o $ORIGIN_MESH/template_PIB.nii.gz
mri_coreg --s mri --mov $ORIGIN_MESH/template_PIB.nii.gz --reg $ORIGIN_MESH/template_PIB.reg.lta --threads 4
# tkregisterfv --mov $ORIGIN_MESH/template_PIB.nii.gz --reg $ORIGIN_MESH/template_PIB.reg.lta --surfs
