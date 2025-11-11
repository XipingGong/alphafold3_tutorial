#!/usr/bin/env python3
import argparse
import json
import mdtraj as md
import os
from collections import defaultdict

def extract_and_save_json(pdb_filename, output_filename):
    """
    Generate AlphaFold 3 (v4) input JSON containing proteins, ligands, and ions.
    Groups identical sequences or CCD codes and keeps all chain IDs as lists.
    """

    traj = md.load(pdb_filename)

    # --- Extract protein sequences ---
    fasta_sequences = traj.topology.to_fasta() if traj.topology.n_residues > 0 else []
    fasta_sequences = [seq for seq in fasta_sequences if seq.strip()]

    protein_chains = []
    for chain in traj.topology.chains:
        first_residue = next((res for res in chain.residues if res.is_protein), None)
        if first_residue:
            protein_chains.append(chain.chain_id)

    if fasta_sequences and len(fasta_sequences) != len(protein_chains):
        raise ValueError("Mismatch between protein sequences and chain IDs. Check the PDB file.")

    grouped_proteins = defaultdict(list)
    for chain_id, seq in zip(protein_chains, fasta_sequences):
        grouped_proteins[seq].append(chain_id)

    protein_sequences = [
        {
            "protein": {
                "id": sorted(ids),
                "sequence": seq
            }
        }
        for seq, ids in grouped_proteins.items()
    ]

    # --- Extract ligands & ions (non-protein residues) ---
    ligand_dict = defaultdict(set)
    for residue in traj.topology.residues:
        if not residue.is_protein:
            resname = residue.name.strip().upper()
            if resname in {"HOH", "WAT", "H2O"}:
                continue  # skip water
            chain_id = residue.chain.chain_id
            ligand_dict[chain_id].add(resname)

    grouped_ligands = defaultdict(list)
    for chain_id, ccd_codes in ligand_dict.items():
        key = tuple(sorted(ccd_codes))
        grouped_ligands[key].append(chain_id)

    ligand_entries = [
        {
            "ligand": {
                "id": sorted(ids),
                "ccdCodes": list(key)
                # Optional fields if you ever define custom CCDs:
                # "userCCD": "...",
                # "userCCDPath": "..."
            }
        }
        for key, ids in grouped_ligands.items()
    ]

    if not protein_sequences and not ligand_entries:
        raise ValueError("No valid protein, ligand, or ion found in the PDB file.")

    # --- Compose AF3 v4 JSON ---
    json_data = {
        "name": os.path.splitext(os.path.basename(output_filename))[0],
        "modelSeeds": [1],
        "sequences": protein_sequences + ligand_entries,
        "bondedAtomPairs": [],
        # userCCD and userCCDPath are mutually exclusive;
        # leave them empty unless you provide custom ligand definitions.
        "dialect": "alphafold3",
        "version": 2
    }

    with open(output_filename, "w") as json_file:
        json.dump(json_data, json_file, indent=2)

    print(f"✅ AlphaFold 3 JSON (v4) saved: {output_filename}")


def main():
    parser = argparse.ArgumentParser(description="Generate AlphaFold 3 (v4) JSON from a PDB with proteins, ligands, and ions.")
    parser.add_argument("input_pdb", help="Input PDB path.")
    parser.add_argument("-o", "--output", help="Output JSON path (default: <input_pdb>.json).")
    args = parser.parse_args()

    input_pdb = args.input_pdb
    output_json = args.output if args.output else input_pdb.replace(".pdb", ".json")

    try:
        extract_and_save_json(input_pdb, output_json)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

