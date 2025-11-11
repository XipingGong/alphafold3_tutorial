#!/usr/bin/env python3
"""
Extract specific atoms or residues from a PDB file using MDTraj.

Usage:
    python extract_pdb.py --selection "protein or resname '8PF' or resname 'MYR'" --ref 7AAI.pdb --output selected.pdb

Examples:
    python extract_pdb.py --selection "protein" --ref 7AAI.pdb
    python extract_pdb.py --selection "protein or resname '8PF' or resname 'MYR'" --ref complex.pdb --output complex_filtered.pdb

Output:
    By default: input_extracted.pdb (if --output is not specified)
"""

import os
import sys
import argparse
import mdtraj as md


def extract_selection(selection, pdb_path, output_pdb=None):
    """Extract the specified selection from the PDB file."""
    print(f"📂 Loading PDB: {pdb_path}")
    traj = md.load(pdb_path)

    print(f"🔍 Applying selection: {selection}")
    try:
        selected_atoms = traj.top.select(selection)
    except Exception as e:
        print(f"❌ Invalid selection string: {selection}")
        print(f"   Error details: {e}")
        sys.exit(1)

    if len(selected_atoms) == 0:
        print(f"⚠️  No atoms matched the selection: '{selection}'")
        sys.exit(1)

    extracted_traj = traj.atom_slice(selected_atoms)

    # Define output path
    if output_pdb is None:
        base, ext = os.path.splitext(pdb_path)
        output_pdb = f"{base}_extracted.pdb"

    extracted_traj.save_pdb(output_pdb)

    print(f"✅ Saved extracted PDB: {output_pdb}")
    print(f"   Selection used: {selection}")
    print(f"   Total atoms included: {len(selected_atoms)}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract atoms or residues from a PDB file using MDTraj."
    )
    parser.add_argument(
        "--selection", "-s",
        required=True,
        help='MDTraj selection string (e.g. "protein or resname 8PF")'
    )
    parser.add_argument(
        "--ref", "-r",
        required=True,
        help="Path to the reference PDB file"
    )
    parser.add_argument(
        "--output", "-o",
        required=False,
        help="Output PDB file name (default: <input>_extracted.pdb)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.ref):
        print(f"❌ File not found: {args.ref}")
        sys.exit(1)

    extract_selection(args.selection, args.ref, args.output)


if __name__ == "__main__":
    main()

