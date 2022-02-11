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
from .interface import IMPORT_MUBIN_DEPS_OT_install, IMPORT_MUBIN_SCENE_OT_smubin

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

def register():
    bpy.utils.register_class(IMPORT_MUBIN_DEPS_OT_install)
    bpy.utils.register_class(IMPORT_MUBIN_SCENE_OT_smubin)
    ...

def unregister():
    bpy.utils.unregister_class(IMPORT_MUBIN_DEPS_OT_install)
    bpy.utils.unregister_class(IMPORT_MUBIN_SCENE_OT_smubin)
    ...
