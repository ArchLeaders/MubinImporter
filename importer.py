import bpy
import math
from pathlib import Path
from .io.cache import Cache
from .io.oead import OpenOead

cache = Cache.cache
data_dir = Cache.data_dir
exported = Cache.exported

def actor(actor: dict, mod_folder: str):
    """Imports a mubin actor entry using the cached models and relative sbfres files."""

    name = actor['UnitConfigName']
    dae_file = ''

    # Vanilla actor
    if name in exported:
        dae_file = f'{data_dir}\\exported\\{exported[name]["BfresName"]}\\{exported[name]["ModelName"]}.dae'

    # Custom actor already cached
    elif name in cache:
        dae_file = f'{data_dir}\\bin\\{cache[name]["BfresName"]}\\{cache[name]["ModelName"]}.dae'

    # Custom actor
    elif Path(f'{mod_folder}\\content\\Actor\\Pack\\{name}.sbactorpack').is_file():
        Cache.add_actor(Path(f'{mod_folder}\\content\\Actor\\Pack\\{name}.sbactorpack'))
        dae_file = f'{data_dir}\\bin\\{cache[name]["BfresName"]}\\{cache[name]["ModelName"]}.dae'

    # Actor not found
    else:
        print(f'A model for {name}: {actor["HashID"]} could not be found.')
        return

    # Import DAE
    bpy.ops.wm.collada_import(
        filename=dae_file
    )

    # Set the transform
    armature = bpy.data.objects["Armature"]
    location = [ 0, 0, 0 ]
    rotate = [ 0, 0, 0 ]
    scale = [ 1, 1, 1 ]

    # Get translate
    if 'Translate' in actor:
        location = [
            actor['Translate'][0],
            actor['Translate'][2],
            actor['Translate'][1],
        ]

    # Get rotation
    if 'Rotate' in actor:
        try:
            rotate = [
                math.cos(math.degrees(actor['Rotate'][0])),
                math.cos(math.degrees(actor['Rotate'][2])),
                math.cos(math.degrees(actor['Rotate'][1])),
            ]
        except:
            angle = math.cos(math.degrees(actor['Rotate']))
            rotate = [
                angle,
                angle,
                angle,
            ]

    # Get scale
    if 'Scale' in actor:
        try:
            scale = [
                actor['Scale'][0],
                actor['Scale'][2],
                actor['Scale'][1],
            ]
        except:
            scale = [
                actor['Scale'],
                actor['Scale'],
                actor['Scale'],
            ]

    # Set transforms
    if armature.type == 'ARMATURE':
        bone = armature.pose.bones['Root']
        bone.rotation_mode = 'XYZ'
        if bone is not None: 
            bone.location = location
            bone.scale = scale
            bone.rotation_euler = rotate
    else:
        print('Imported armature could not be found!')
        return

    # Rename armature (Could result in issues)
    armature.name = f"{actor['UnitConfigName']} ({actor['HashID']})"