import bpy
import traceback
import time
from pathlib import Path
from .io.system import Data
from .io.oead import OpenOead

Data.init()

data_dir = Data.data_dir
cache = Data.cache
exported = Data.exported

def import_actor(actor: dict, mod_folder: str, import_shader: bool = False):
    """Imports a mubin actor entry using the cached models and relative sbfres files."""

    name = actor['UnitConfigName']
    dae_file = ''

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
        print(f'A model for {name}: {actor["HashId"]} could not be found.')
        return

    # Import DAE
    bpy.ops.wm.collada_import(filepath=dae_file)
    armature = bpy.data.objects["Armature"]
    armature.hide_render = True
    armature.hide_viewport = True

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
    bone = None
    if armature.type == 'ARMATURE':
        for child_bone in armature.pose.bones:
            if child_bone.name == 'Root':
                bone = child_bone
                break
            elif child_bone.name == 'Model':
                bone = child_bone
                break
            else:
                bone = child_bone
                break


        bone.rotation_mode = 'XYZ'
        if bone is not None: 
            bone.location = location
            bone.scale = scale
            bone.rotation_euler = rotate
        else:
            print('Root bone could not be found!')
            return
    else:
        print('Imported armature could not be found!')
        return
        
    # Import Shader
    if import_shader:
        for child in armature.children:
            # Import material
            imported_mat = child.data.materials[0]

            # Break if no material exists
            if imported_mat is None:
                break

            # Get name
            name = imported_mat.name

            # Get base color
            base_color = None
            for node in imported_mat.node_tree.nodes:
                if node.label == 'Base Color':
                    base_color = node.image
                    break

            # Delete imported
            bpy.data.materials.remove(imported_mat)

            # Get material
            if base_color is not None:
                bpy.ops.wm.append(filename='MAT', directory=str(data_dir).replace("\\", "/") + '/shader.blend\\Material\\')
                mat = bpy.data.materials.get('MAT')
                mat.name = name
                for node in mat.node_tree.nodes:
                    if node.label == 'Base Color':
                        node.image = base_color
                        break
            else:
                bpy.ops.wm.append(filename='MAT_GRAY', directory=str(data_dir).replace("\\", "/") + '/shader.blend\\Material\\')
                mat = bpy.data.materials.get('MAT_GRAY')
                mat.name = name
            
            if child.data.materials:
                child.data.materials[0] = mat
            else:
                child.data.materials.append(mat)

    # Rename armature
    armature.name = f"{name} ({actor['HashId']})"

    # return complete
    print(f'Imported {name}: {actor["HashId"]} successfully.')
    return

def import_mubin(mubin :Path, context, import_shader: bool = False):
    data = OpenOead.from_path(mubin)

    content = ''
    num = range(0)
    for i in num:
        if Path(f'{mubin}{".//" * (i + 1)}/content').is_dir():
            content = f'{mubin}{"..//" * (i + 1)}/content'
            break

        num = range(i + 1)

    if data.type == 'BYML' and data.sub_type == 'MUBIN':
        start_time = time.time()
        for actor in data.content['Objs']:
            try:
                if str(actor["UnitConfigName"]).endswith('_Far'):
                    # Create Far LOD collection
                    if 'Far LOD' not in context.blend_data.collections:
                        collection = context.blend_data.collections.new("Far LOD")
                        context.scene.collection.children.link(collection)

                    # Set context
                    print(context.view_layer.layer_collection.children)
                    context.view_layer.active_layer_collection = context.view_layer.layer_collection.children["Far LOD"]

                    # Import actor
                    import_actor(actor, f'{content}..\\', import_shader=import_shader)
                else:
                    # Create Far LOD collection
                    if 'Actors' not in context.blend_data.collections:
                        collection = context.blend_data.collections.new("Actors")
                        context.scene.collection.children.link(collection)

                    # Set context
                    context.view_layer.active_layer_collection = context.view_layer.layer_collection.children["Actors"]

                    # Import actor
                    import_actor(actor, f'{content}..\\', import_shader=import_shader)
            except:
                print(f'Could not import {actor["UnitConfigName"]}\n{traceback.format_exc()}')

                error = ''
                if Path(f'{data_dir}\\error.txt').is_file():
                    error = Path(f'{data_dir}\\error.txt').read_text()

                Path(f'{data_dir}\\error.txt').write_text(f'{error}Could not import {actor["UnitConfigName"]}\n{traceback.format_exc()}{"- " * 30}\n')

                # if input() == 'exit':
                #     return

        end_time = time.time()
        sec = end_time - start_time
        print(f'\nCompleted in {sec} seconds.')