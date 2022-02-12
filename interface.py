import bpy
import json
import os
import sys
import subprocess
import shutil
import requests
import zipfile
from bpy_extras.io_utils import ImportHelper, ExportHelper
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
        # Show console window
        bpy.ops.wm.console_toggle()

        if Path(self.filepath).is_file() and Path(self.filepath).suffix == '.mubin' or '.smubin':
            if not Path(f'{Data.data_dir}\\shader.blend').is_file():
                self.import_shader = False

            import_mubin(Path(self.filepath), context, self.import_shader)

        bpy.ops.wm.console_toggle()

        return {'FINISHED'}

class IMPORT_MUBIN_DEPS_OT_install(bpy.types.Operator, ExportHelper):
    """Installs the Mubin Importer dependencies."""
    bl_idname = 'mubin_importer.deps'
    bl_label = 'Install Dependencies'

    filename_only = 0
    filename_ext = '.ini'
    filter_glob: StringProperty(default='*.ini', options={'HIDDEN'}, subtype= 'DIR_PATH')

    def execute(self, context):
        # Show console
        bpy.ops.wm.console_toggle()

        # Set app data information
        print('Setting up configuration...')
        if not Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_importer').is_dir():
            Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_importer').mkdir()
        Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_importer\\config.json').write_text(json.dumps({ 'data_dir': self.filepath }, indent=4))
        Data.data_dir = Path(self.filepath).parent

        # Install oead
        print('Installing oead...')
        python_exe = Path(sys.prefix, 'bin', 'python.exe')
        subprocess.call([python_exe, "-m", "pip", "install", "oead"])

        # Download lib
        print('Downloading C# binaries...')
        file_bytes = requests.get('https://github.com/ArchLeaders/MubinImporter/raw/master/dist/lib.zip')
        Path(f'{Data.data_dir}\\lib.zip').write_bytes(file_bytes.content)

        print('Extracting C# binaries...')
        if not Path(f'{Data.data_dir}\\lib').is_dir():
            Path(f'{Data.data_dir}\\lib').mkdir
        with zipfile.ZipFile(f'{Data.data_dir}\\lib.zip', 'r') as zip_ref:
            zip_ref.extractall(f'{Data.data_dir}\\lib')
        Path(f'{Data.data_dir}\\lib.zip').unlink()

        # Download json data
        print('Downloading json data...')
        file_bytes = requests.get('https://raw.githubusercontent.com/ArchLeaders/MubinImporter/master/dist/exported.bin')
        Path(f'{Data.data_dir}\\exported.json').write_bytes(file_bytes.content)

        # Export sbfres files
        print('Extracting sbfres data... (this will take a while)')
        subprocess.run(f'cmd.exe /c "{Data.data_dir}\\lib\\ModelExtracter.exe"', cwd=f'{Data.data_dir}')
        shutil.move(f'{Data.data_dir}\\export', f'{Data.data_dir}\\exported')

        # Write cache file
        if not Path(f'{Data.data_dir}\\cache').is_dir():
            Path(f'{Data.data_dir}\\cache').mkdir()
        Path(f'{Data.data_dir}\\cache.json').write_text(json.dumps({}))

        print('Install Complete! Please restart Blender before continuing.')
        bpy.ops.wm.console_toggle()

        return {'FINISHED'}

class TOOL_PT_MubinImporter(bpy.types.Panel):
    bl_idname = "TOOL_PT_MubinImporter"
    bl_category = "Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_label = "Mubin Importer"

    data_dir: StringProperty(f'{os.environ["LOCALAPPDATA"]}\\mubin_importer')

    def draw(self, context):
        self.layout.operator('mubin_importer.scene')

        try:
            Data.init()
        except:
            self.layout.operator('mubin_importer.deps')