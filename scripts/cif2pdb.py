#!/usr/bin/env python3
"""
Convert one or multiple CIF files into PDB format using MDTraj.

Usage:
    python cif2pdb.py "af3/*/model.cif"

Examples:
    python cif2pdb.py "af3/*/model.cif"

Options:
    --help      Show this help message.
"""

import sys
import glob
import os
import mdtraj as md

def print_help():
    """Show help text."""
    print(__doc__)
    sys.exit(0)

def cif_to_pdb(cif_path):
    """Convert one CIF file to PDB using MDTraj."""
    pdb_path = os.path.join(os.path.dirname(cif_path),
                            os.path.splitext(os.path.basename(cif_path))[0] + ".pdb")

    if os.path.exists(pdb_path):
        print(f"⏩ Skipping {cif_path} (already converted)")
        return

    try:
        traj = md.load(cif_path)
        traj.save_pdb(pdb_path)
        print(f"✅ Converted: {cif_path} → {pdb_path}")
    except Exception as e:
        print(f"❌ Failed to convert {cif_path}: {e}")

def main():
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        print_help()

    pattern = sys.argv[1]
    cif_files = glob.glob(pattern, recursive=True)

    if not cif_files:
        print(f"⚠️ No CIF files found matching pattern: {pattern}")
        sys.exit(0)

    print(f"🔍 Found {len(cif_files)} CIF file(s) to convert.\n")
    for cif_path in cif_files:
        cif_to_pdb(cif_path)

if __name__ == "__main__":
    main()

