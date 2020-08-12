import os

import config.settings as settings
from common.tools import cprint
from config import config_interface
from schlib import SchLib


### KiCad Component Library Manager
class ComponentLibManager(object):
	def __init__(self):
		pass

	def is_component_in_library(self, library_instance, component_part_number):
		''' Check if component already exists in library '''
		for component in library_instance.components:
			cprint(f'[DBUG]\t{component.definition["name"]} ?= {component_part_number}', silent=settings.HIDE_DEBUG)
			if component.definition['name'] == component_part_number:
				cprint(f'[KCAD]\tWarning: Component {component_part_number} already in library', silent=settings.SILENT)
				return True

		return False

	def add_component_to_library_from_inventree(self, component_data, library_path=None, template_path=None):
		''' Create component (symbol) in KiCad library '''
		KICAD_SYMBOLS_PATH = config_interface.load_library_path(settings.CONFIG_KICAD, silent=True)
		part_in_lib = False
		new_part = False
		category = component_data['category'][0]
		subcategory = component_data['category'][1]

		# Load library and template paths
		if not library_path:
			# Automatically fetch library path
			try:
				symbol_library_name = component_data['parameters']['Symbol'].split(':')[0]
				# Reload paths (only in production)
				symbol_libraries_paths = config_interface.load_libraries_paths(settings.CONFIG_KICAD_CATEGORY_MAP, KICAD_SYMBOLS_PATH)
				library_path = symbol_libraries_paths[category][symbol_library_name]
			except:
				cprint(f'[KCAD]\tError: Failed to load library file for "{category}" category', silent=settings.SILENT)
				return part_in_lib, new_part

		cprint(f'[KCAD]\tlibrary_path: {library_path}', silent=settings.SILENT)

		if not template_path:
			# Automatically fetch template path
			try:
				template_path = settings.symbol_templates_paths[category][subcategory]
			except:
				template_path = settings.symbol_templates_paths[category]['Default']

		# Check files exist
		if not os.path.isfile(library_path):
			cprint(f'[KCAD]\tError loading library file ({library_path})', silent=settings.SILENT)
			return part_in_lib, new_part
		if not os.path.isfile(template_path):
			cprint(f'[KCAD]\tError loading template file ({template_path})', silent=settings.SILENT)
			return part_in_lib, new_part

		# Load library
		schlib = SchLib(library_path)
		library_name = library_path.split('/')[-1]
		cprint('[KCAD]\tNumber of parts in library ' + library_name + ': ' + str(schlib.getComponentCount()), silent=settings.SILENT)

		# Check if part already in library
		try:
			is_component_in_library = self.is_component_in_library(schlib, component_data['IPN'])
			part_in_lib = True
		except:
			is_component_in_library = False
		if is_component_in_library:
			return part_in_lib, new_part

		# Load template
		templatelib = SchLib(template_path)
		# Load new component
		if templatelib.getComponentCount() == 1:
			for component in templatelib.components:
				new_component = component
		else:
			cprint('[KCAD]\tError: Found more than 1 component template in template file, aborting', silent=settings.SILENT)
			return part_in_lib, new_part

		# Update comment, name and definition
		new_component.comments[1] = '# ' + component_data['IPN'] + '\n'
		new_component.name = component_data['IPN']
		new_component.definition['name'] = component_data['IPN']

		# Update documentation
		new_component.documentation['description'] = component_data['description']
		new_component.documentation['datasheet'] = component_data['inventree_url']
		new_component.documentation['keywords'] = component_data['keywords']
		#cprint(new_component.documentation, silent=SILENT)

		# Update fields
		manufacturer_name = ''
		for field_idx in range(len(new_component.fields)):
			if 'name' in new_component.fields[field_idx]:
				component_field = str(new_component.fields[field_idx]['name']).replace('"','')
				if component_field in component_data['parameters'].keys():
					new_component.fields[field_idx]['name'] = component_data['parameters'][component_field]
				elif component_field == 'Manufacturer':
					for manufacturer in component_data['manufacturer'].keys():
						manufacturer_name = manufacturer
						new_component.fields[field_idx]['name'] = manufacturer_name
						break
				elif component_field == 'MPN':
					new_component.fields[field_idx]['name'] = component_data['manufacturer'][manufacturer_name][0]
			
		schlib.addComponent(new_component)
		schlib.save()
		cprint(f'[KCAD]\tSuccess: Component added to library {library_name}', silent=settings.SILENT)
		part_in_lib = True
		new_part = True

		return part_in_lib, new_part

	def delete_component_from_lib(self, part_number, category=None, library_path=None):
		''' Remove component (symbol) from KiCad library '''
		if category and library_path:
			cprint('[KCAD]\tWarning: Too many argument, specifify only category or library_path (delete_component_from_lib)', silent=settings.SILENT)
			return False
		# Load Library and Template paths
		elif category and not library_path:
			library_path = settings.symbol_libraries_paths[category]
			# Check librart file exists
			if not os.path.isfile(library_path):
				cprint(f'[KCAD]\tError loading library file ({library_path})', silent=settings.SILENT)
				cprint('[KCAD]\tCheck library file path and name', silent=settings.SILENT)
				return False
		elif library_path and not category:
			if not os.path.isfile(library_path):
				cprint(f'[KCAD]\tError loading library file ({library_path})', silent=settings.SILENT)
				cprint('[KCAD]\tCheck library file path and name', silent=settings.SILENT)
				return False
		else:
			cprint('[KCAD]\tError: Specify either category or library_path (delete_component_from_lib)', silent=settings.SILENT)
			return False

		schlib = SchLib(library_path)
		library_name = library_path.split('/')[-1]
		cprint('[KCAD]\tNumber of parts in library ' + library_name + ': ' + str(schlib.getComponentCount()), silent=settings.SILENT)

		try:
			schlib.removeComponent(part_number)
			schlib.save()
			cprint(f'[KCAD]\tSuccess: Component {part_number} was removed from library', silent=settings.SILENT)
			return True
		except:
			cprint(f'[KCAD]\tError: Component {part_number} was not found in library {library_name} (no delete)', silent=settings.SILENT)
			return False
