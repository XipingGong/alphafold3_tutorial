# AlphaFold 3 for Predicting Biomolecular Structures and Interactions

**Author:** Xiping Gong  
Department of Crop and Soil Sciences, College of Agricultural and Environmental Sciences, University of Georgia, Griffin, GA, USA  
📧 xipinggong@uga.edu  
🗓️ First Draft: 11/11/2025  

---

## 📘 Overview

This Jupyter Notebook (`alphafold3.ipynb`) serves as a **hands-on tutorial** for *MIBO 8110* students to learn how to use **AlphaFold 3 (AF3)** for predicting **biomolecular structures and interactions**.

It provides a step-by-step workflow showing how AlphaFold 3 integrates protein and small-molecule components into a unified structure prediction system. Students will gain practical experience in using computational structure prediction tools, performing post-analysis, and interpreting results.

---

## 🧩 Learning Objectives

By working through this notebook, students will learn how to:
- Predict **protein 3D structures** from amino acid sequences using AlphaFold 3.  
- Predict **protein–ligand complexes** and explore binding interactions.  
- Analyze and visualize predicted structures using **MDTraj** and **VMD**.  
- Calculate **RMSD** values to assess prediction accuracy.  
- Perform post-processing (alignment, file conversion, and interaction mapping).

---

## ⚙️ Prerequisites and Setup

- **AlphaFold 3** must be installed.  
  Official GitHub: [https://github.com/google-deepmind/alphafold3](https://github.com/google-deepmind/alphafold3)

- **Environment:**  
  AF3 is already installed on the *GACRC teaching node*.  
  Log in using your UGA MyID:  
```bash
$ ssh <MyID>@teach.gacrc.uga.edu
```

- **Dependencies:**  
Some useful Python packages like `mdtraj`, `openmm`, and `biopython` are preinstalled.  
For additional setup help, see: [https://xipinggong.com/files/tutorials/setup.html](https://xipinggong.com/files/tutorials/setup.html)

---

## 🧪 Sections Overview

### 1. Protein Structure Prediction
Students learn how to:
1. **Download** a PDB structure (e.g., human serum albumin 7AAI).  
2. **Extract** the protein chain (`extract_pdb.py`).  
3. **Prepare input JSON** for AF3 (`get_json_for_af3.py`).  
4. **Run AF3** via SLURM (`sbatch af3.sh 7AAI_protein.json`).  
5. **Convert and align** output CIF → PDB → aligned structure (`cif2pdb.py`, `align_pdb.py`).  
6. **Visualize** using VMD.

---

### 2. Protein–Ligand Interaction Prediction
- Extend the workflow to include **ligands** (e.g., `8PF` and `MYR` in the 7AAI system).  
- Create a **multi-component JSON** input specifying both protein and ligands.  
- Run AF3 again and align the predicted complexes.  
- Discuss accuracy and limitations (e.g., training set overlap).

---

### 3. Structural Interaction Analysis
- Use the provided scripts to identify **binding residues**
- Calculate the RMSD values
- Example systems: PFOA–human serum albumin (PDB: 7AAI) & MYR–human serum albumin interactions

