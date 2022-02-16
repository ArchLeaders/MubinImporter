# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import os
import subprocess
import sys

# install oead
python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
subprocess.call([python_exe, "-m", "pip", "install", "oead"])

from pathlib import Path
from .interface import IMPORT_MUBIN_DEPS_OT_install, IMPORT_MUBIN_SCENE_OT_smubin, TOOL_PT_MubinImporter

bl_info = {
    "name" : "Mubin Importer",
    "author" : "Marcus Smith",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

# Install deps
if not Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_importer').is_dir():
    Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_importer').mkdir()
if not Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_importer\\config.json').is_file():
    Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_importer\\config.json').write_text('{}')

classes = [
    IMPORT_MUBIN_DEPS_OT_install,
    IMPORT_MUBIN_SCENE_OT_smubin,
    TOOL_PT_MubinImporter,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)