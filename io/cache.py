import json
import subprocess
from .oead import OpenOead
from pathlib import Path

class CachedActor:
    """Meta data for cached actors"""

    name = ''
    """Name of the actor"""

    display_name = ''
    """In game name of the actor"""

    dae_file = ''
    """Full path to the actors collada file"""

    folder = ''
    """Model folder name, aka bfres name"""

    unit = ''
    """Model unit name, commonly shares the actor name"""

class Cache:
    """Cached actors"""

    data_dir = json.loads(Path(f'.\\config.json').read_text())['data_dir']
    """Path to the storage directory"""

    exported: dict = {}
    """Dictionary of exported actors"""

    cache: dict = {}
    """Dictionary of cached actors"""

    def register():
        """Sets the current export and cache data to the ExportList and CacheList class."""

        sets = [ 'exported', 'cache' ]

        for file in sets:
            file_data = json.loads(Path(f'{Cache.data_dir}\\{file}.json').read_text())
            data: dict = {}

            for key, value in file_data:
                data[key] = {
                    CachedActor(
                        name=key,
                        display_name=value['DisplayName'],
                        folder=value['BfresName'],
                        unit=value['ModelName'],
                        dae_file=f"{Cache.data_dir}\\{file}\\{value['BfresName']}\\{value['ModelName']}.dae"
                    )
                }

            if file == 'exported':
                exported = data
            elif file == 'cache':
                cache = data

    def add_actor(actorname, mod_dir) -> CachedActor:
        """Caches an actor from an actorpack file"""

        cache_data = json.loads(Path(f'{Cache.data_dir}\\cache.json').read_text())

        # Check for existing entry
        if actorname.name in cache_data:
            return

        # Look for actorpack
        actorpack = Path(f'{mod_dir}\\Actor\\Pack\\{actorname}.sbactorpack')
        if not actorpack.is_file():
            print(f'No binary actor pack (bactorpack) for {actorname} could be found.')
            return

        # Parse SARC file
        data = OpenOead.from_path(actorpack)
        if data['type'] == 'SARC':
            for SARCFile in data['content']:
                if str(SARCFile).endswith('.bmodellist'):
                    modellist = OpenOead.from_bytes(SARCFile.data)
                    model_data = modellist.lists["ModelData"].lists["ModelData_0"]
                    unit_name = model_data.lists["Unit"].objects["Unit_0"].params["UnitName"]
                    folder_name = model_data.objects["Base"].params["Folder"]
                    cache_data[actorname] = {
                        "DisplayName": actorname.name,
                        "BfresName": folder_name,
                        "ModelName": unit_name,
                    }

        # Check and extract sbfres
        if not Path(f'{mod_dir}\\content\\Model\\{folder_name}.sbfres').is_file():
            print(f'No binary cafe resource (bfres) file for {actorname} could be found.')
            return

        subprocess.run(
            args=[
                f'"{Cache.data_dir}\\lib\\SbfresExtracter.exe"',
                f'"{mod_dir}\\content\\Model\\{folder_name}.sbfres"',
                f'"{mod_dir}\\content\\Model\\{folder_name}Tex1.sbfres"',
                f'"{folder_name}"'
            ],
            capture_output=True
        )

        Path(f'{Cache.data_dir}\\cache.json').write_text(json.dumps(cache_data, indent=4))