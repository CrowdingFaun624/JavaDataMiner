import os

import DataMiners.DataMiner as DataMiner
import Importer.Manifest as Manifest

import DataMiners.DataMinerType as DataMinerType
import DataMiners.Blocks.Blocks as Blocks
import DataMiners.Language.Language as Language
import DataMiners.Notes.Notes as Notes
import DataMiners.SoundEvents.SoundEvents as SoundEvents
import DataMiners.SoundType.SoundType as SoundType
import DataMiners.SoundTypeBlocks.SoundTypeBlocks as SoundTypeBlocks
import DataMiners.Subtitles.Subtitles as Subtitles

all_dataminers:dict[str,DataMinerType.DataMinerType] = {
    "blocks": Blocks.Blocks,
    "language": Language.Language,
    "notes": Notes.Notes,
    "sound_events": SoundEvents.SoundEvents,
    "sound_type": SoundType.SoundType,
    "sound_type_blocks": SoundTypeBlocks.SoundTypeBlocks,
    "subtitles": Subtitles.Subtitles,
}

def has_all_files(version:str) -> bool:
    for name, dataminer in list(all_dataminers.items()):
        if not os.path.exists(os.path.join("./_versions", version, "data", dataminer.file_name)):
            version_dataminer = DataMiner.get_dataminer(version, dataminer.dataminers)
            if version_dataminer is None: continue
            else: return False
    else: return True

def run(version:str, dataminer_name:str, error_on_none:bool=False, run_if_already_existing:bool=True) -> None:
    dataminer_type = all_dataminers[dataminer_name]
    if not run_if_already_existing and os.path.exists(os.path.join("./_versions", version, "data", dataminer_type.file_name)): return
    dataminer = DataMiner.get_dataminer(version, dataminer_type.dataminers)
    if dataminer is None:
        if error_on_none: raise KeyError("DataMiner %s for version %s does not exist!" % (dataminer_name, version))
        else: return None
    else:
        return dataminer.activate(version)

def run_all(version:str, error_on_none:bool=False, run_if_already_existing:bool=True) -> None:
    for name in list(all_dataminers.keys()):
        run(version, name, error_on_none, run_if_already_existing)

def main() -> None:
    selected_dataminer = None
    while selected_dataminer not in all_dataminers and selected_dataminer != "all":
        selected_dataminer = input("Select a dataminer from [%s, all]: " % ", ".join(all_dataminers))
    all_versions = Manifest.get_version_list()
    selected_version = None
    while selected_version not in all_versions:
        selected_version = input("Select a valid version: ")
    if selected_dataminer == "all": run_all(selected_version)
    else: run(selected_version, selected_dataminer, error_on_none=True)
