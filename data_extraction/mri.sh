export FREESURFER_HOME=/Applications/freesurfer
export SUBJECTS_DIR=origin_meshing/
source $FREESURFER_HOME/SetUpFreeSurfer.sh

export ORIGIN_EXTRACTION=origin_extraction/mri
export ORIGIN_MESH=origin_meshing/mri/mri

recon-all -s mri2 -i $ORIGIN_EXTRACTION/T1w.nii.gz -T2 $ORIGIN_EXTRACTION/T2w.nii.gz -all

mri_binarize --i $ORIGIN_MESH/wmparc.mgz --gm --dilate 2 --o $ORIGIN_MESH/mask.mgz