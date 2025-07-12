''' gsrs.py  The purpose of this program is to fetch a GSRS molecule image.
    Copyright (C) 2024  github.com/brandongrahamcobb

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
from py_vyrtuous.utils.handlers.image_manager import adjust_hue_and_saturation, add_watermark
from py_vyrtuous.utils.inc.helpers import *
from py_vyrtuous.utils.inc.setup_logging import logger
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pyPept.sequence import Sequence, correct_pdb_atoms
from pyPept.molecule import Molecule
from pyPept.converter import Converter
from rdkit import Chem
from rdkit.Chem import rdFMCS, AllChem, DataStructs, Draw, rdMolAlign, rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D, SimilarityMaps
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Geometry import Point3D
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import math
import numpy as np
import os
import pubchempy as pcp
import re
import requests
import shlex
import os

residue_fragments = {
    "A": "[*:1]NC(=O)[C@@H](C)[*:2]",
    "R": "[*:1]NC(=O)[C@@H](CCCNC(=N)N)[*:2]",
    "N": "[*:1]NC(=O)[C@@H](CC(=O)N)[*:2]",
    "D": "[*:1]NC(=O)[C@@H](CC(=O)O)[*:2]",
    "C": "[*:1]NC(=O)[C@@H](CSH)[*:2]",
    "Q": "[*:1]NC(=O)[C@@H](CCC(=O)N)[*:2]",
    "E": "[*:1]NC(=O)[C@@H](CCC(=O)O)[*:2]",
    "G": "[*:1]NCC(=O)[*:2]",
    "H": "[*:1]NC(=O)[C@@H](Cc1cnc[nH]1)[*:2]",
    "I": "[*:1]NC(=O)[C@@H](C(C)CC)[*:2]",
    "L": "[*:1]NC(=O)[C@@H](CC(C)C)[*:2]",
    "K": "[*:1]NC(=O)[C@@H](CCCCN)[*:2]",
    "M": "[*:1]NC(=O)[C@@H](CCSC)[*:2]",
    "F": "[*:1]NC(=O)[C@@H](Cc1ccccc1)[*:2]",
    "P": "[*:1]NC(=O)[C@@H](C1CCCN1)[*:2]",
    "S": "[*:1]NC(=O)[C@@H](CO)[*:2]",
    "T": "[*:1]NC(=O)[C@@H]([C@H](O)C)[*:2]",
    "W": "[*:1]NC(=O)[C@@H](Cc1c[nH]c2ccccc12)[*:2]",
    "Y": "[*:1]NC(=O)[C@@H](Cc1ccc(O)cc1)[*:2]",
    "V": "[*:1]NC(=O)[C@@H](C(C)C)[*:2]"
}

def build_peptide_from_residues(res_list, cyclic=False):
    if not res_list:
        raise ValueError("Residue list is empty.")
    mol_list = []
    for r in res_list:
        frag = residue_fragments.get(r)
        if frag is None:
            raise ValueError(f"Residue '{r}' is not defined in residue_fragments.")
        mol = Chem.MolFromSmiles(frag)
        if mol is None:
            raise ValueError(f"Failed to parse SMILES for residue '{r}'.")
        mol_list.append(mol)
    current = mol_list[0]
    for i in range(1, len(mol_list)):
        current = join_two_molecules(current, mol_list[i])
    final_mol = remove_dummy_atoms(current)
    return final_mol

def construct_helm(sequence, reverse=False):
    if reverse:
        sequence = reverse_peptide_sequence(sequence)
    fasta_str = three_to_fasta(sequence)
    if not fasta_str:
        logger.error(f"Failed to convert peptide sequence '{sequence}' to FASTA.")
        return None
    helm = construct_linear_helm(fasta_str)
    logger.info(f"Constructed HELM: {helm}")
    return helm

def construct_helm_from_peptide(seq):
    fasta = three_to_fasta(seq)
    if not fasta:
        return None
    helm = construct_linear_helm(fasta)
    return helm

def construct_linear_helm(fasta_str):
    polymer = "PEPTIDE1{" + ".".join(list(fasta_str)) + "}"
    sections = [polymer, "", "", "", "V2.0"]
    helm = "$".join(sections)
    return helm

def draw_fingerprint(pair, rdkit_bool=True, rotation=0) -> BytesIO:
    rdDepictor.SetPreferCoordGen(rdkit_bool)
    d2d = rdMolDraw2D.MolDraw2DCairo(1024, 1024)
    d2d.prepareMolsBeforeDrawing = False
    Options = d2d.drawOptions()
    Options.prepareMolsBeforeDrawing = False
    Options.includeMetadata = False
    Options.bondLineWidth = 4.0
    d2d.SetDrawOptions(Options)
    mol1, mol2 = pair[0], pair[1]
    mol1, mol2 = standardize_molecule(mol1), standardize_molecule(mol2)
    mol1 = rotate_molecule(mol1, rotation)
    mol2 = rotate_molecule(mol2, rotation)
    fig, maxweight = SimilarityMaps.GetSimilarityMapForFingerprint(
        mol1, mol2,
        lambda m, i: SimilarityMaps.GetMorganFingerprint(m, i, radius=2, fpType='bv', nBits=8192),
        draw2d=d2d, drawingOptions=Options, forceCoords=True
    )
    name = get_molecule_name(mol2)
    d2d.FinishDrawing()
    drawing = d2d.GetDrawingText()
    output = BytesIO(drawing)
    output.seek(0)
    img = Image.open(output).convert('RGBA')
    inverted_img = Image.eval(img, lambda x: 255 - x)
    adjusted_output = adjust_hue_and_saturation(inverted_img, hue_shift=-180, saturation_shift=160)
    adjusted_output.seek(0)
    if rotation == 0:
        return adjusted_output
    else:
        watermarked_image_buffer = add_watermark(adjusted_output, name, False)
        return watermarked_image_buffer

def draw_watermarked_molecule(molecule, rotation=0, rdkit_bool=True) -> BytesIO:
    rdDepictor.SetPreferCoordGen(rdkit_bool)
    try:
        resolved_name = get_molecule_name(molecule)
        d2d = rdMolDraw2D.MolDraw2DCairo(1024, 1024)
        Options = d2d.drawOptions()
        Options.prepareMolsBeforeDrawing = False
        Options.includeMetadata = False
        Options.bondLineWidth = 4.0
        d2d.SetDrawOptions(Options)
        rdMolDraw2D.SetDarkMode(Options)
        mol = rdMolDraw2D.PrepareMolForDrawing(molecule, kekulize=True)
        mol = rotate_molecule(mol, rotation)
        mol.UpdatePropertyCache(False)
        d2d.DrawMolecule(mol)
        d2d.FinishDrawing()
        drawing = d2d.GetDrawingText()
        output = add_watermark(BytesIO(drawing), resolved_name, False)
        return output
    except Exception as e:
        logger.error(f'An error occurred while drawing the watermarked molecule: {e}')
        raise

def get_linear_peptide_mol(sequence, reverse=False):
    helm = construct_helm(sequence, reverse=reverse)
    if helm is None:
        return None
    try:
        conv = Converter(helm=helm)
        biln_seq = conv.get_biln()
        seq_obj = Sequence(biln_seq)
        seq_obj = correct_pdb_atoms(seq_obj)
        mol_obj = Molecule(seq_obj)
        rdkit_mol = mol_obj.get_molecule(fmt="ROMol")
        return rdkit_mol
    except Exception as e:
        logger.error(f"Error converting linear peptide: {e}")
        return None

def get_mol(arg, reverse=False):
    try:
        mol = Chem.MolFromSmiles(arg)
        if mol:
            return mol
    except Exception as e:
        logger.warning(f"Direct SMILES conversion failed for '{arg}': {e}")
    try:
        compounds = pcp.get_compounds(arg, 'name')
        if compounds:
            smiles = compounds[0].to_dict(properties=['isomeric_smiles']).get('isomeric_smiles')
            if smiles:
                mol = Chem.MolFromSmiles(smiles)
                if mol:
                    return mol
    except Exception as e:
        logger.warning(f"PubChem lookup failed for '{arg}': {e}")
    if any(x in arg for x in ["Ala", "Arg", "His", "Lys", "Pro", "Gly", "Cys"]):
        try:
            return get_linear_peptide_mol(arg, reverse=reverse)
        except Exception as e:
            logger.error(f"Peptide conversion error: {e}")
            return None
    return None

def get_molecule_name(molecule) -> str:
    try:
        smiles = Chem.MolToSmiles(molecule)
        if not smiles:
            return 'Unknown'
        compounds = pcp.get_compounds(smiles, 'smiles')
        if not compounds:
            raise ValueError('No compound found for the given SMILES string')
        compound_data = compounds[0].to_dict(properties=['synonyms'])
        if 'synonyms' in compound_data and compound_data['synonyms']:
            molecule_name = compound_data['synonyms'][0]
            return molecule_name
        else:
            return 'Unknown'
    except Exception as e:
        logger.error(f"An error occurred while retrieving the molecule name: {e}")
        return 'Unknown'

def get_proximity(default, input) -> float:
    try:
        default_fp = AllChem.GetMorganFingerprintAsBitVect(default, 2)
        if default_fp is None:
            raise ValueError('Invalid default molecule.')
        input_fp = AllChem.GetMorganFingerprintAsBitVect(input, 2)
        if input_fp is None:
            raise ValueError('Invalid input molecule.')
        similarity = DataStructs.FingerprintSimilarity(default_fp, input_fp)
        return similarity
    except Exception as e:
        logger.error(f'An error occurred during proximity calculation: {e}')
        raise

def gsrs(arg):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run headless Chrome (no UI)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    executable_path = os.path.join(DIR_HOME, 'Py_vyrtuous', 'chromedriver')
    driver = webdriver.Chrome(service=Service(executable_path=executable_path), options=chrome_options)
    try:
        search_url = f'https://gsrs.ncats.nih.gov/ginas/app/beta/browse-substance?search={arg}'
        driver.get(search_url)
        driver.implicitly_wait(10)  # Adjust the wait time as needed
        img_element = driver.find_element(By.CSS_SELECTOR, 'body > app-root > app-base > app-substances-browse > div > div.substance-cards > app-substance-summary-card > mat-card > mat-card-title > a')
        if img_element:
            img_src = img_element.get_attribute('href')
            if img_src:
                stripped = img_src.split('/', -1)[-1:]
                link = f'https://gsrs.ncats.nih.gov/api/v1/substances/render({stripped[0]})?format=png&size=512&stereo=true'
                response = requests.get(link)
                response.raise_for_status()
                image_bytes = response.content
                image = Image.open(BytesIO(image_bytes)).convert('RGBA')
                draw = ImageDraw.Draw(image)
                width, height = image.size
                diagonal = math.sqrt(width**2 + height**2)
                font_size = int(diagonal / 15)
                try:
                    font = ImageFont.truetype(PATH_FONT, font_size)
                except IOError:
                    font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), arg, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = (width - text_width) / 2
                text_y = (height - text_height) / 2
                watermark_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
                watermark_draw = ImageDraw.Draw(watermark_image)
                watermark_draw.text((text_x, text_y), arg, font=font, fill=(255, 255, 255, 64))
                mask = watermark_image.split()[3]
                image.paste(watermark_image, (0, 0), mask)
                return image
            else:
                return 'No src attribute found in the <img> element'
        else:
            return 'No <img> element found with the specified CSS path'
    except Exception as e:
        logger.error(f'An error occurred during the GSRS process: {e}')
        raise
    finally:
        driver.quit()
        logger.info('WebDriver session closed.')

def helm_to_smiles_manual(helm_str):
    m = re.search(r'PEPTIDE1\{([^}]+)\}', helm_str)
    if not m:
        raise ValueError("Could not parse HELM polymer definition.")
    residue_str = m.group(1)
    residues = residue_str.split('.')
    mol = build_peptide_from_residues(list(residues), cyclic=False)
    smiles = Chem.MolToSmiles(mol, canonical=False)
    return smiles

def join_two_molecules(mol1, mol2):
    dummy1 = next((atom for atom in mol1.GetAtoms() if atom.GetAtomMapNum() == 2), None)
    if dummy1 is None:
        raise ValueError("No dummy atom with map number 2 found in first molecule.")
    dummy2 = next((atom for atom in mol2.GetAtoms() if atom.GetAtomMapNum() == 1), None)
    if dummy2 is None:
        raise ValueError("No dummy atom with map number 1 found in second molecule.")
    combined = Chem.CombineMols(mol1, mol2)
    n1 = mol1.GetNumAtoms()
    idx1 = dummy1.GetIdx()
    idx2 = n1 + dummy2.GetIdx()
    emol = Chem.EditableMol(combined)
    emol.AddBond(idx1, idx2, Chem.BondType.SINGLE)
    new_mol = emol.GetMol()
    return new_mol

def manual_helm_to_smiles(helm_str):
    try:
        residues = parse_helm_for_residues(helm_str)
    except Exception as e:
        logger.error(f"Error parsing HELM: {e}")
        return None
    frag_dict = {
        "A": "NCC",   # Placeholder for Ala
        "R": "NC(CCCNC(=N)N)",  # Placeholder for Arg
        "N": "NC(CC(=O)N)",     # Placeholder for Asn
        "D": "NC(CC(=O)O)",     # Asp
        "C": "NC(CS)",          # Cys
        "Q": "NC(CCC(=O)N)",     # Gln
        "E": "NC(CCC(=O)O)",     # Glu
        "G": "NC",              # Gly
        "H": "NC(CC1=CN=CN1)",   # His
        "I": "NC(C(C)CC)",       # Ile
        "L": "NC(CC(C)C)",       # Leu
        "K": "NC(CCCCN)",        # Lys
        "M": "NC(CCSC)",         # Met
        "F": "NC(CC1=CC=CC=C1)",  # Phe
        "P": "NC(C1CCCN1)",       # Pro
        "S": "NC(CO)",           # Ser
        "T": "NC(C(C)O)",        # Thr
        "W": "NC(CC1=CNC2=CC=CC=C12)",  # Trp
        "Y": "NC(CC1=CC=C(O)C=C1)",      # Tyr
        "V": "NC(C(C)C)"         # Val
    }
    connector = "NC(=O)"
    smiles_parts = []
    for r in residues:
        frag = frag_dict.get(r)
        if not frag:
            logger.error(f"Residue {r} not defined in frag_dict.")
            return None
        smiles_parts.append(frag)
    manual_smiles = connector.join(smiles_parts)
    return manual_smiles

def parse_helm_for_residues(helm_str):
    m = re.search(r'PEPTIDE1\{([^}]+)\}', helm_str)
    if not m:
        raise ValueError("Could not parse HELM polymer definition.")
    residue_str = m.group(1)
    residues = residue_str.split('.')
    return residues

def clean_peptide_sequence(seq):
    seq = seq.replace("(", "").replace(")", "").replace(" ", "").strip()
    if len(seq) % 3 != 0:
        return None
    allowed = {"Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly",
               "His", "Ile", "Leu", "Lys", "Met", "Phe", "Pro", "Ser",
               "Thr", "Trp", "Tyr", "Val"}
    tokens = [seq[i:i+3] for i in range(0, len(seq), 3)]
    for token in tokens:
        if token not in allowed:
            logger.error(f"Unknown residue: '{token}' in sequence '{seq}'")
            return None
    return "".join(tokens)

def remove_dummy_atoms(mol):
    emol = Chem.RWMol(mol)
    dummy_idxs = [atom.GetIdx() for atom in emol.GetAtoms() if atom.GetAtomicNum() == 0]
    for idx in sorted(dummy_idxs, reverse=True):
        emol.RemoveAtom(idx)
    return emol.GetMol()

def reverse_peptide_sequence(seq):
    cleaned = seq.replace("(", "").replace(")", "").strip()
    tokens = [cleaned[i:i+3] for i in range(0, len(cleaned), 3)]
    reversed_tokens = list(reversed(tokens))
    return "".join(reversed_tokens)

def rotate_molecule(mol, angle):
    conf = mol.GetConformer()
    rad_angle = float(np.radians(angle))
    cos_theta = float(np.cos(rad_angle))
    sin_theta = float(np.sin(rad_angle))
    for i in range(mol.GetNumAtoms()):
        pos = conf.GetAtomPosition(i)
        x_new = float(cos_theta * pos.x - sin_theta * pos.y)
        y_new = float(sin_theta * pos.x + cos_theta * pos.y)
        z = float(pos.z)
        conf.SetAtomPosition(i, Point3D(x_new, y_new, z))
    return mol

def standardize_molecule(mol):
    mol = Chem.Mol(mol)
    Chem.rdDepictor.Compute2DCoords(mol)
    return mol

def standardize_smiles(smiles_str):
    try:
        std_smiles = rdMolStandardize.StandardizeSmiles(smiles_str)
        return std_smiles
    except Exception as e:
        logger.error(f"Error standardizing SMILES: {e}")
        return smiles_str

def three_to_fasta(three_letter_seq):
    cleaned = clean_peptide_sequence(three_letter_seq)
    if not cleaned:
        return None
    three_to_one = {
        "Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C",
        "Gln": "Q", "Glu": "E", "Gly": "G", "His": "H", "Ile": "I",
        "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P",
        "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V"
    }
    tokens = [cleaned[i:i+3] for i in range(0, len(cleaned), 3)]
    fasta = ''.join(three_to_one.get(token, '?') for token in tokens)
    if '?' in fasta:
        return None
    return fasta

