from kicad import kicad_schlib

klib = kicad_schlib.ComponentLibManager()

def inventree_to_kicad(part_data: dict, library_path=None, template_path=None) -> bool:
	''' Create KiCad symbol from InvenTree part data '''
	return klib.add_component_to_library_from_inventree(	component_data=part_data,
															library_path=library_path,
															template_path=template_path )

def delete_part(part_number: str, category: str, library_path=None) -> bool:
	''' Delete KiCad symbol from library '''
	return klib.delete_component_from_lib(	part_number=part_number,
											category=category,
											library_path=library_path )
