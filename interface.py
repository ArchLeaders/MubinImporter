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

class IMPORT_SCENE_OT_mubin(bpy.types.Operator, ImportError):
    """Imports a map unit (mubin) file."""
    bl_idname = 'import_scene.mubin'
    bl_label = 'Import Mubin'

    filter_glob: StringProperty( default='*.mubin;*smubin', options={'HIDDEN'} )
    import_shader: BoolProperty('Import objects with the BotW Shader by Moonling')

    def execute(self, context):
        if Path(self.filepath).is_file() and Path(self.filepath).suffix == '.mubin' or '.smubin':
            import_mubin(Path(self.filepath), context, self.import_shader)

        return {'FINISHED'}

class OT_oead(bpy.types.Operator):
    """Installs oead inside Blenders python install."""
    bl_idname = 'mubin_importer.install.deps'
    bl_label = 'Install Dependencies'

    def execute(self, context):
        subprocess.run(f'{Data.data_dir}\\lib\\ModelExtracter.exe')
        shutil.move(f'{Data.data_dir}\\lib\\export',f'{Data.data_dir}\\exported')

        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        subprocess.call([python_exe, "-m", "pip", "install", "oead"])

        return {'FINISHED'}