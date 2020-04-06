"""Test for PubChemPy"""

from chemistry_tools.lookup import get_compounds
from decimal import Decimal

comp = get_compounds("diphenylamine", 'name')[0]

import pprint
pprint.pprint(comp._physical_properties)

print(f"CID:							{'Passed!' if comp.cid == 11487 else 'Failed!'}")
print(f"CAS Number:						{'Passed!' if comp.CAS == '122-39-4' else 'Failed!'}")
print(f"Formula:						{'Passed!' if comp.molecular_formula == 'C12H11N' else 'Failed!'}")
print(f"IUPAC:							{'Passed!' if comp.IUPAC['String'] == 'N-phenylaniline' else 'Failed!'}")
print(f"InChI:							{'Passed!' if comp.inchi == 'InChI=1S/C12H11N/c1-3-7-11(8-4-1)13-12-9-5-2-6-10-12/h1-10,13H' else 'Failed!'}")
print(f"InChIKey:						{'Passed!' if comp.inchikey == 'DMBHHRLKUKUOEG-UHFFFAOYSA-N' else 'Failed!'}")
print(f"Canonical SMILES:				{'Passed!' if comp.canonical_smiles == 'C1=CC=C(C=C1)NC2=CC=CC=C2' else 'Failed!'}")
print(f"Isomeric SMILES:				{'Passed!' if True == False else 'Failed!'}") # TODO
print(f"SMILES:							{'Passed!' if comp.smiles == 'C1=CC=C(C=C1)NC2=CC=CC=C2' else 'Failed!'}")
print(f"Physical Description:			{'Passed!' if comp.physical_description['String'] == 'DIPHENYLAMINE is a light tan to brown solid with a pleasant odor. Sinks in water. (USCG, 1999)' else 'Failed!'}")
print(f"Ontology:						{'Passed!' if comp.ontology['String'] == 'An aromatic amine containing two phenyl substituents. It has been used as a fungicide for the treatment of superficial scald in apples and pears, but is no longer approved for this purpose within the European Union.' else 'Failed!'}")
print(f"Metabolites:					{'Passed!' if comp.metabolite['String'] == 'Diphenylamine is found in coriander. Diphenylamine is used for control of superficial scald in stored apples Diphenylamine is the organic compound with the formula (C6H5)2NH. It is a colourless solid, but samples are often yellow due to oxidized impurities. It is a weak base, with a KB of 10 14. With strong acids, it forms the water soluble salt' else 'Failed!'}")
print(f"Molecular Mass:					{'Passed!' if comp.molecular_mass == Decimal('169.227') else 'Failed!'}")
print(f"Molecular Weight:				{'Passed!' if comp.molecular_weight == Decimal('169.227') else 'Failed!'}")
print(f"XLogP:							{'Passed!' if comp.xlogp == Decimal('3.5')  else 'Failed!'}")
print(f"Hydrogen Bond Donor Count:		{'Passed!' if comp.h_bond_donor_count == Decimal('1') else 'Failed!'}")
print(f"Hydrogen Bond Acceptor Count:	{'Passed!' if comp.h_bond_acceptor_count == Decimal('1') else 'Failed!'}")
print(f"Rotatable Bond Count:			{'Passed!' if comp.rotatable_bond_count == Decimal('2') else 'Failed!'}")
print(f"Exact Mass:						{'Passed!' if comp.exact_mass == Decimal('169.089') else 'Failed!'}")
print(f"Monoisotopic Mass:				{'Passed!' if comp.monoisotopic_mass == Decimal('169.089') else 'Failed!'}")
print(f"Topological Polar Surface Area:	{'Passed!' if comp.tpsa == Decimal('12') else 'Failed!'}")
print(f"Heavy Atom Count:				{'Passed!' if comp.heavy_atom_count == Decimal('13') else 'Failed!'}")
print(f"Charge:							{'Passed!' if comp.charge == Decimal('0') else 'Failed!'}")
print(f"Complexity:						{'Passed!' if comp.complexity == Decimal('116') else 'Failed!'}")
print(f"Isotope Atom Count:				{'Passed!' if comp.isotope_atom_count == Decimal('0') else 'Failed!'}")
print(f"Defined Atom Stereo Count:		{'Passed!' if comp.defined_atom_stereo_count == Decimal('0') else 'Failed!'}")
print(f"Undefined Atom Stereo Count:	{'Passed!' if comp.undefined_atom_stereo_count == Decimal('0') else 'Failed!'}")
print(f"Defined Bond Stereo Count:		{'Passed!' if comp.defined_bond_stereo_count == Decimal('0') else 'Failed!'}")
print(f"Undefined Bond Stereo Count:	{'Passed!' if comp.undefined_bond_stereo_count == Decimal('0') else 'Failed!'}")
print(f"Covalent Unit Count:			{'Passed!' if comp.covalent_unit_count == Decimal('1') else 'Failed!'}")
print(f"Compound is Canonicalized:		{'Passed!' if comp.compound_is_canonicalized == True else 'Failed!'}")
print(f"Atom stereocenter count:		{'Passed!' if True == False else 'Failed!'}")
print(f"Bond stereocenter count:		{'Passed!' if True == False else 'Failed!'}")
print(f"boiling_point:					{'Passed!' if comp.boiling_point == Decimal('302') else 'Failed!'}")
print(f"melting_point:					{'Passed!' if comp.melting_point == '53-54' else 'Failed!'}")
print(f"Density:						{'Passed!' if comp.density == Decimal('1.16') else 'Failed!'}")
print(f"Vapor Density:					{'Passed!' if comp.vapor_density == Decimal('5.82') else 'Failed!'}")
print(f"Vapor Pressure:					{'Passed!' if comp.vapor_pressure == Decimal('1') else 'Failed!'}")
print(f"Heat of Combustion:				{'Passed!' if comp.heat_combustion == '-16.300 BTU/LB = -9.060 CAL/G = -379×10<sup>+5</sup> J/KG' else 'Failed!'}")




#print(f"IUPAC:					{'Passed!' if comp. ==  else 'Failed!'}")
#print(f"IUPAC:					{'Passed!' if comp. ==  else 'Failed!'}")
#print(f"IUPAC:					{'Passed!' if comp. ==  else 'Failed!'}")
#print(f"IUPAC:					{'Passed!' if comp. ==  else 'Failed!'}")
#print(f"IUPAC:					{'Passed!' if comp. ==  else 'Failed!'}")
#print(f"IUPAC:					{'Passed!' if comp. ==  else 'Failed!'}")
#print(f"IUPAC:					{'Passed!' if comp. ==  else 'Failed!'}")
#print(f"IUPAC:					{'Passed!' if comp. ==  else 'Failed!'}")
#Decimal('')