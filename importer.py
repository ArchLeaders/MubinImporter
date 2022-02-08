import bpy
import math
from pathlib import Path
from .io.system import Data
from .io.oead import OpenOead

cache = Data.cache
data_dir = Data.data_dir
exported = Data.exported

def import_actor(actor: dict, mod_folder: str):
    """Imports a mubin actor entry using the cached models and relative sbfres files."""

    name = actor['UnitConfigName']
    dae_file = ''

    try:
        print(f'{data_dir}\\exported\\{exported[name]["BfresName"]}\\{exported[name]["ModelName"]}.dae')
    except:
        print('N/A')

    # Vanilla actor
    if name in exported:
        dae_file = f'{data_dir}\\exported\\{exported[name]["BfresName"]}\\{exported[name]["ModelName"]}.dae'

    # Custom actor already cached
    elif name in cache:
        dae_file = f'{data_dir}\\cache\\{cache[name]["BfresName"]}\\{cache[name]["ModelName"]}.dae'

    # Custom actor
    elif Path(f'{mod_folder}\\content\\Actor\\Pack\\{name}.sbactorpack').is_file():
        Data.cache_actor(Path(f'{mod_folder}\\content\\Actor\\Pack\\{name}.sbactorpack'))
        dae_file = f'{data_dir}\\bin\\{cache[name]["BfresName"]}\\{cache[name]["ModelName"]}.dae'

    # Actor not found
    else:
        # print(f'A model for {name}: {actor["HashId"]} could not be found.')
        return

    # Import DAE
    bpy.ops.wm.collada_import(filepath=dae_file)
    armature = bpy.data.objects["Armature"]

    # Set the transform
    location = actor['Translate']
    rotate = [ 0, 0, 0 ]
    scale = [ 1, 1, 1 ]

    # Get rotation
    if 'Rotate' in actor:
        try:
            rotate = [
                actor['Rotate'][0],
                actor['Rotate'][1],
                actor['Rotate'][2],
            ]
        except:
            rotate = [
                0.0,
                actor['Rotate'],
                0.0,
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
        try:
            bone = armature.pose.bones['Root']
        except:
            bone = armature.pose.bones['Model']

        bone.rotation_mode = 'XYZ'
        if bone is not None: 
            bone.location = location
            bone.scale = scale
            bone.rotation_euler = rotate

            print(bone.rotation_euler)
            print(rotate)
    else:
        print('Imported armature could not be found!')
        return

    # Rename armature (Could result in issues)
    armature.name = f"{actor['UnitConfigName']} ({actor['HashId']})"

def import_mubin(mubin :Path):
    data = OpenOead.from_path(mubin)

    content = ''
    num = range(0)
    for i in num:
        if Path(f'{mubin}{".//" * (i + 1)}/content').is_dir():
            content = f'{mubin}{"..//" * (i + 1)}/content'
            break

        num = range(i + 1)

    if data.type == 'BYML' and data.sub_type == 'MUBIN':
        for actor in data.content['Objs']:
            try:
                import_actor(actor, f'{content}..\\')
            except:
                print(f'Could not import {actor["UnitConfigName"]}')