import DataMiners.DataMiner as DataMiner
import Importer.Manifest as Manifest

import DataMiners.Blocks.Blocks as Blocks
import DataMiners.Language.Language as Language
import DataMiners.SoundEvents.SoundEvents as SoundEvents
import DataMiners.SoundType.SoundType as SoundType
import DataMiners.SoundTypeBlocks.SoundTypeBlocks as SoundTypeBlocks
import DataMiners.Subtitles.Subtitles as Subtitles

all_dataminers = {
    "blocks": Blocks.dataminers,
    "language": Language.dataminers,
    "sound_events": SoundEvents.dataminers,
    "sound_type": SoundType.dataminers,
    "sound_type_blocks": SoundTypeBlocks.dataminers,
    "subtitles": Subtitles.dataminers
}

def run_all(version:str) -> None:
    for name, dataminers in list(all_dataminers.items()):
        dataminer = DataMiner.get_dataminer(version, dataminers)
        if dataminer is None: continue
        dataminer.activate(version)

def main() -> None:
    selected_dataminer = None
    while selected_dataminer not in all_dataminers and selected_dataminer != "all":
        selected_dataminer = input("Select a dataminer from [%s, all]: " % ", ".join(all_dataminers))
    all_versions = Manifest.get_version_list()
    selected_version = None
    while selected_version not in all_versions:
        selected_version = input("Select a valid version: ")
    if selected_dataminer == "all":
        run_all(selected_version)
    else:
        selected_dataminer = all_dataminers[selected_dataminer] # turns the key into the dataminer object
        dataminer = DataMiner.get_dataminer(selected_version, selected_dataminer)
        if dataminer is not None: dataminer.activate(selected_version)
        else: raise ValueError("dataminer does not exist for version %s!" % selected_version)
