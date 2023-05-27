import DataMiners.DataMiner as DataMiner
import DataMiners.Blocks.Blocks as Blocks
import DataMiners.SoundType.SoundType as SoundType

class SoundTypeBlocksNew(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.blocks_sound_type_variable = "sound_type"
        if "blocks_sound_type_variable" in kwargs:
            self.blocks_sound_type_variable = kwargs["blocks_sound_type_variable"]

    def activate(self, version:str, store:bool=True) -> dict[str,list[str]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_data:dict[str,dict[str,any]] = Blocks.get_data_file(version)
        sound_type_data:dict[str,dict[str,float|str]] = SoundType.get_data_file(version)
        output:dict[str,list[str]] = {}
        for sound_type in list(sound_type_data.keys()):
            output[sound_type] = []
        for block, block_data in list(blocks_data.items()):
            sound_types = block_data[self.blocks_sound_type_variable]
            if isinstance(sound_types, str): sound_types = [sound_types]
            for sound_type in sound_types:
                output[sound_type].append(block)
        output = SoundTypeBlocksNew.sort_dict(output)
        if store: self.store(version, output, "sound_type_blocks.json")
        return output
