import bpy
from pathlib import Path
from .importer import import_mubin

class IMPORT_SCENE_OT_mubin(bpy.types.Operator):
    """Imports a map unit (mubin) file."""
    bl_idname = 'import_scene.mubin'
    bl_label = 'Import Mubin'

    def execute(self, context):
        # import_mubin(Path("D:\\Botw\\Cemu\\mlc01\\usr\\title\\0005000c\\101c9500\\content\\0010\\Map\\MainField\\E-6\\E-6_Static.smubin"))
        import_mubin(Path('D:\\A-1_Static.mubin'), context)
        return {'FINISHED'}