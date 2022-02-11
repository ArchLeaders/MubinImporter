import bpy
import sys
import os
import subprocess
import shutil
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from pathlib import Path
from .importer import import_mubin
from .io.system import Data

class IMPORT_MUBIN_SCENE_OT_smubin(bpy.types.Operator, ImportHelper):
    """Imports a map unit (mubin) file."""
    bl_idname = 'mubin_importer.scene'
    bl_label = 'Import Mubin'

    filter_glob: StringProperty( default='*.mubin;*smubin', options={'HIDDEN'} )
    import_shader: BoolProperty('Import objects with the BotW Shader by Moonling')

    def execute(self, context):
        if Path(self.filepath).is_file() and Path(self.filepath).suffix == '.mubin' or '.smubin':
            import_mubin(Path(self.filepath), context, self.import_shader)

        return {'FINISHED'}

class IMPORT_MUBIN_DEPS_OT_install(bpy.types.Operator):
    """Installs the Mubin Importer dependicies."""
    bl_idname = 'mubin_importer.deps'
    bl_label = 'Install Dependencies'

    def execute(self, context):
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        subprocess.call([python_exe, "-m", "pip", "install", "oead"])

        subprocess.run(f'{Data.data_dir}\\lib\\ModelExtracter.exe')
        shutil.move(f'.\\export', f'{Data.data_dir}\\exported')

        return {'FINISHED'}

class PANEL_smth:
    ...