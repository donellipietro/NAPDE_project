export FREESURFER_HOME=/Applications/freesurfer
export SUBJECTS_DIR=origin_meshing/
source $FREESURFER_HOME/SetUpFreeSurfer.sh

export ORIGIN_EXTRACTION=origin_extraction/dti

mri_convert $ORIGIN_EXTRACTION/dwi.nii.gz $ORIGIN_EXTRACTION/dwi.mgz 

dt_recon --i $ORIGIN_EXTRACTION/dwi.mgz --b $ORIGIN_EXTRACTION/dwi.bval $ORIGIN_EXTRACTION/dwi.bvec --s mri --o $SUBJECTS_DIR/dti