import bpy
import json
import os
import sys
import subprocess
import shutil
import requests
import zipfile
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from pathlib import Path
from .importer import import_mubin
from .io.system import Data

class IMPORT_MUBIN_SCENE_OT_smubin(bpy.types.Operator, ImportHelper):
    """Imports a map unit (mubin) file."""
    bl_idname = 'mubin_importer.scene'
    bl_label = 'Import Mubin'

    filter_glob: StringProperty( description='Browse for a MUBIN file to import.', default='*.mubin;*smubin', options={'HIDDEN'} )
    import_shader: BoolProperty('Import objects with the BotW Shader by Moonling')

    def execute(self, context):
        if Path(self.filepath).is_file() and Path(self.filepath).suffix == '.mubin' or '.smubin':
            if not Path(f'{Data.data_dir}\\shader.blend').is_file():
                self.import_shader = False

            import_mubin(Path(self.filepath), context, self.import_shader)

        return {'FINISHED'}

class IMPORT_MUBIN_DEPS_OT_install(bpy.types.Operator, ImportHelper):
    """Installs the Mubin Importer dependencies."""
    bl_idname = 'mubin_importer.deps'
    bl_label = 'Install Dependencies'

    filter_glob: StringProperty( description='Browse for the Mubin Importer data directory.', options={'HIDDEN'}, subtype='DIR_PATH' )

    def execute(self, context):
        # Show console
        bpy.ops.wm.console_toggle()

        # Set app data information
        print('Setting up configuration...')
        config = Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_importer\\config.json')
        config_data = { 'data_dir': self.filename }

        # Write config file
        config.write_text(json.dumps(config_data, indent=4))

        # Install oead
        print('Installing oead...')
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        subprocess.call([python_exe, "-m", "pip", "install", "oead"])

        # Download lib
        print('Downloading C# binaries...')
        file_bytes = requests.get('https://github.com/ArchLeaders/MubinImporter/raw/master/dist/lib.zip')
        Path(f'{Data.data_dir}\\lib.zip').write_bytes(file_bytes)

        print('Extracting C# binaries...')
        os.makedirs(f'{Data.data_dir}\\lib')
        with zipfile.ZipFile(f'{Data.data_dir}\\lib.zip', 'r') as zip_ref:
            zip_ref.extractall(f'{Data.data_dir}\\lib')

        # Download json data
        print('Downloading json data...')
        file_bytes = requests.get('https://github.com/ArchLeaders/MubinImporter/raw/master/dist/extracted.bin')
        Path(f'{Data.data_dir}\\extracted.json').write_bytes(file_bytes)

        # Export sbfres files
        print('Extracting sbfres data... (this will take a while)')
        subprocess.run(f'{Data.data_dir}\\lib\\ModelExtracter.exe')
        shutil.move(f'.\\export', f'{Data.data_dir}\\exported')

        # Write cache file
        os.makedirs(f'{Data.data_dir}\\cache')
        Path(f'{Data.data_dir}\\cache.json').write_bytes(json.dumps({}))

        # print initializing
        Data.init()

        return {'FINISHED'}

class TOOL_PT_MubinImporter(bpy.types.Panel):
    bl_idname = "TOOL_PT_MubinImporter"
    bl_category = "Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_label = "Mubin Importer"

    def draw(self, context):
        self.layout.operator('mubin_importer.scene')

        try:
            Data.init()
        except:
            self.layout.operator('mubin_importer.deps')