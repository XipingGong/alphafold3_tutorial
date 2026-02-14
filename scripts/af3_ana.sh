#!/usr/bin/env bash

# Usage:
# bash af3_ana.sh ref.pdb "af3_*"

ref_pdb="$1"
pattern="$2"

wdir="/home/xg69107/program/alphafold3/alphafold3_tutorial/scripts"
python="/home/xg69107/program/anaconda/anaconda3/bin/python"

if [ -z "$ref_pdb" ] || [ -z "$pattern" ]; then
    echo "Usage: bash af3_ana.sh ref.pdb \"folder_pattern\""
    exit 1
fi

# Expand folder pattern
for folder in $pattern; do
    [ -d "$folder" ] || continue

    echo "# Testing >> $folder"
    echo "#===================="

    mkdir -p "$folder/best_pose"

    cp "$folder"/*model.cif "$folder/best_pose/model.cif" 

    echo "$ $python $wdir/cif2pdb.py "$folder/*/*model.cif""
            $python $wdir/cif2pdb.py "$folder/*/*model.cif"
    echo ""

    echo "$ $python $wdir/align_pdb.py --ref $ref_pdb "$folder/*/*model.pdb""
            $python $wdir/align_pdb.py --ref $ref_pdb "$folder/*/*model.pdb"
    echo ""
done

