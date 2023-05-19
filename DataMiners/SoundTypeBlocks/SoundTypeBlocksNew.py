import json
import os

import DataMiners.DataMiner as DataMiner
import DataMiners.Blocks.Blocks as Blocks
import DataMiners.SoundType.SoundType as SoundType

class SoundTypeBlocksNew(DataMiner.DataMiner):
    def import_file(self, version:str, file_name:str, dataminer_list:list[DataMiner.DataMiner]) -> any:
        path = "./_versions/%s/data/%s" % (version, file_name)
        if not os.path.exists(path):
            dataminer = DataMiner.get_dataminer(version, dataminer_list)
            data = dataminer.activate(version)
        else:
            with open(path, "rt") as f:
                data = json.loads(f.read())
        return data

    def activate(self, version:str, store:bool=True) -> dict[str,list[str]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_data:dict[str,dict[str,any]] = self.import_file(version, "blocks.json", Blocks.dataminers)
        sound_type_data:dict[str,dict[str,float|str]] = self.import_file(version, "sound_type.json", SoundType.dataminers)
        output:dict[str,list[str]] = {}
        for sound_type in list(sound_type_data.keys()):
            output[sound_type] = []
        for block, block_data in list(blocks_data.items()):
            sound_types = block_data["sound_type"]
            if isinstance(sound_types, str): sound_types = [sound_types]
            for sound_type in sound_types:
                output[sound_type].append(block)
        output = SoundTypeBlocksNew.sort_dict(output)
        if store: self.store(version, output, "sound_type_blocks.json")
        return output