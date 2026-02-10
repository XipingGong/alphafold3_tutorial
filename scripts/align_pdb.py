#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mdtraj as md
import argparse
import numpy as np
import sys
import os
import glob


def identify_pocket_atoms(ref_traj, cutoff=1.0):
    """Identify protein backbone pocket atoms within a given distance of the ligand.
    If ligand is not present, use all protein backbone heavy atoms."""
    protein_atoms = ref_traj.topology.select("protein and backbone and not element H")
    ligand_atoms = ref_traj.topology.select("not protein and not element H")

    if len(protein_atoms) == 0:
        print("❌ Error: No protein backbone atoms found in the reference PDB.")
        sys.exit(1)

    if len(ligand_atoms) == 0:
        print("⚠ Warning: No ligand found. Using protein backbone heavy atoms as pocket.")
        return protein_atoms, False

    pairs = np.array([[p, l] for p in protein_atoms for l in ligand_atoms])
    distances = md.compute_distances(ref_traj, pairs).reshape(len(protein_atoms), len(ligand_atoms))

    pocket_mask = np.any(distances < cutoff, axis=1)
    pocket_atoms = protein_atoms[pocket_mask]

    if len(pocket_atoms) == 0:
        print("⚠ Warning: No pocket residues found in reference. Using full backbone instead.")
        return protein_atoms, True

    return pocket_atoms, True


def get_matched_pocket_atoms(ref_traj, target_traj, ref_pocket_atoms):
    target_lookup = {}
    for atom in target_traj.topology.atoms:
        key = (atom.name, atom.residue.name, atom.residue.index, atom.residue.chain.index)
        if key not in target_lookup:
            target_lookup[key] = atom.index

    matched_target_atoms = []
    for idx in ref_pocket_atoms:
        ref_atom = ref_traj.topology.atom(idx)
        key = (ref_atom.name, ref_atom.residue.name, ref_atom.residue.index, ref_atom.residue.chain.index)
        if key in target_lookup:
            matched_target_atoms.append(target_lookup[key])

    return matched_target_atoms


def make_output_names(pdb_files, suffix):
    """For each input file, write output in same directory with <stem><suffix>.pdb"""
    outputs = []
    for pdb in pdb_files:
        d = os.path.dirname(pdb)
        stem = os.path.splitext(os.path.basename(pdb))[0]
        outputs.append(os.path.join(d, f"{stem}{suffix}.pdb"))
    return outputs


def main():
    parser = argparse.ArgumentParser(
        description="Align PDB file(s) to a reference using protein backbone pocket residues (MDTraj)."
    )
    parser.add_argument("target", help="Target PDB file(s) to be aligned (supports glob).")
    parser.add_argument("--ref", default="model.pdb", help="Reference PDB file (default: model.pdb)")
    parser.add_argument("--cutoff", type=float, default=1.0, help="Pocket cutoff distance in nm (default: 1.0)")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Aligned model filename. Default: <input>_aligned.pdb (same directory as each input). "
             "If multiple targets and a single -o is given, a multi-model PDB is written."
    )
    parser.add_argument(
        "--oligand",
        default=None,
        help="Aligned ligand filename. Default: <input>_ligand_aligned.pdb (same directory as each input). "
             "If multiple targets and a single --oligand is given, a multi-model PDB is written."
    )
    args = parser.parse_args()

    # --- Load reference ---
    print(f"📂 Loading reference: {args.ref}")
    ref_matches = glob.glob(os.path.expanduser(args.ref))
    if not ref_matches:
        print(f"❌ Error: Reference not found: {args.ref}")
        sys.exit(1)
    ref_pdb_file = os.path.abspath(ref_matches[0])
    print(f"  - {ref_pdb_file}")
    ref_traj = md.load(ref_pdb_file)
    print(ref_traj)

    # --- Load targets ---
    print(f"📂 Loading target(s): {args.target}")
    target_matches = glob.glob(os.path.expanduser(args.target), recursive=True)
    if not target_matches:
        print(f"❌ Error: No target files matched: {args.target}")
        sys.exit(1)

    target_pdb_files = [os.path.abspath(f) for f in target_matches]
    target_pdb_files.sort(key=lambda x: (not os.path.basename(os.path.dirname(x)).startswith("best_pose"), x))
    print("\n".join(f"  - {f}" for f in target_pdb_files))

    target_traj = md.load(target_pdb_files)
    print(target_traj)

    n_targets = len(target_pdb_files)

    # --- Output filenames ---
    # If user did NOT specify -o, we save one aligned file per input.
    per_input_model_output = (args.output is None)

    if per_input_model_output:
        output_files = make_output_names(target_pdb_files, "_aligned")
       #for inp, out in zip(target_pdb_files, output_files):
       #    print(f"🧬 {os.path.basename(inp)} → {os.path.basename(out)}")
    else:
        output_single = os.path.abspath(os.path.expanduser(args.output))
       #print(f"🧬 Writing ALL aligned models to: {output_single}")

    # Ligand output: same policy
    per_input_ligand_output = (args.oligand is None)
    if per_input_ligand_output:
        oligand_files = make_output_names(target_pdb_files, "_ligand_aligned")
    else:
        oligand_single = os.path.abspath(os.path.expanduser(args.oligand))

    # --- Identify pocket atoms ---
    print("🔍 Identifying protein backbone pocket atoms from reference...")
    ref_pocket_atoms, has_ligand = identify_pocket_atoms(ref_traj, cutoff=args.cutoff)
    target_pocket_atoms = get_matched_pocket_atoms(ref_traj, target_traj, ref_pocket_atoms)

    if len(ref_pocket_atoms) != len(target_pocket_atoms):
        print(
            f"❌ Error: Atom mapping mismatch. ref pocket atoms={len(ref_pocket_atoms)}, "
            f"target matched atoms={len(target_pocket_atoms)}"
        )
        sys.exit(1)

    # --- Align ---
    print("📐 Aligning target to reference using protein backbone pocket atoms...")
    target_traj.superpose(ref_traj, atom_indices=target_pocket_atoms, ref_atom_indices=ref_pocket_atoms)

    # --- RMSD (protein backbone) ---
    idx_target = target_traj.topology.select("protein and backbone and not element H")
    idx_ref = ref_traj.topology.select("protein and backbone and not element H")
    target_protein_traj = target_traj.atom_slice(idx_target)
    ref_protein_traj = ref_traj.atom_slice(idx_ref)
    rmsd_values = md.rmsd(target_protein_traj, ref_protein_traj)
    print(f"📊 Pocket-Aligned Protein Backbone RMSD (MDTraj): {rmsd_values} nm")

    # --- RMSD (pocket) ---
    target_pocket_traj = target_traj.atom_slice(target_pocket_atoms)
    ref_pocket_traj = ref_traj.atom_slice(ref_pocket_atoms)
    rmsd_values = md.rmsd(target_pocket_traj, ref_pocket_traj)
    print(f"📊 Pocket-Aligned Protein Backbone Pocket RMSD (MDTraj): {rmsd_values} nm")

    # --- Save aligned models ---
    print("💾 Saving aligned model structures")
    if per_input_model_output:
        for i in range(len(target_traj)):
            print(f" - {output_files[i]}")
            target_traj[i].save(output_files[i])
    else:
        # IMPORTANT FIX: save ONCE to avoid overwriting; this produces multi-model PDB if multiple frames exist
        print(f" - {output_single} (contains {len(target_traj)} model(s))")
        target_traj.save(output_single)

    # --- Save aligned ligands (only if ligand exists in reference) ---
    if has_ligand:
        ligand_idx = target_traj.topology.select("not protein and not element H")
        if len(ligand_idx) == 0:
            print("ℹ️ Reference had ligand, but target has no ligand atoms — skipping ligand output.")
        else:
            target_ligand_traj = target_traj.atom_slice(ligand_idx)
            print("💾 Saving aligned ligand structures")
            if per_input_ligand_output:
                for i in range(len(target_ligand_traj)):
                    print(f" - {oligand_files[i]}")
                    target_ligand_traj[i].save(oligand_files[i])
            else:
                print(f" - {oligand_single} (contains {len(target_ligand_traj)} model(s))")
                target_ligand_traj.save(oligand_single)
    else:
        print("ℹ️ No ligand found in reference — skipping ligand output.")

    print("✅ Alignment complete.\n")


if __name__ == "__main__":
    main()

