import json
import subprocess
from .oead import OpenOead
from pathlib import Path

class Data:
    """Cached actors"""

    data_dir = json.loads(Path(f'.\\config.json').read_text())['data_dir']
    """Path to the storage directory"""

    exported: dict = json.loads(Path(f'{data_dir}\\exported.json').read_text())
    """Dictionary of exported actors"""

    cache: dict = json.loads(Path(f'{data_dir}\\cache.json').read_text())
    """Dictionary of cached actors"""

    def cache_actor(actorname, mod_dir) -> dict:
        """Caches an actor from an actorpack file"""

        # Check for existing entry
        if actorname.name in data.cache:
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
                    data.cache[actorname] = {
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
                f'"{data.data_dir}\\lib\\SbfresExtracter.exe"',
                f'"{mod_dir}\\content\\Model\\{folder_name}.sbfres"',
                f'"{mod_dir}\\content\\Model\\{folder_name}Tex1.sbfres"',
                f'"{folder_name}"'
            ],
            capture_output=True
        )

        Path(f'{data.data_dir}\\cache.json').write_text(json.dumps(data.cache, indent=4))