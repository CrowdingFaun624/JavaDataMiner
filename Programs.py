import Comparison.Comparers as Comparers
import Comparison.CompareAllVersions as CompareAllVersions
import DataMiners.DataMiners as DataMiners
import Importer.Decompiler as Decompiler
import Importer.JarImporter as JarImporter
import Utilities.AssetsStorage as AssetsStorage
import Utilities.DataRedoer as DataRedoer
import Utilities.DecompileZipper as DecompileZipper
import Utilities.MappingCondenser as MappingCondenser
import Utilities.PlaylistAssembler as PlaylistAssembler
import Utilities.Searcher as Searcher
import Utilities.SoundsJsonTablifier as SoundsJsonTablifier

if __name__ == "__main__":
    functions = {
        "AssetsStorage": AssetsStorage.main,
        "CompareAllVersions": CompareAllVersions.main,
        "Comparers": Comparers.main,
        "DataMiners": DataMiners.main,
        "DataRedoer": DataRedoer.main,
        "Decompiler": Decompiler.main,
        "DecompileZipper": DecompileZipper.main,
        "JarImporter": JarImporter.main,
        "MappingCondenser": MappingCondenser.main,
        "PlaylistAssembler": PlaylistAssembler.main,
        "Searcher": Searcher.main,
        "SoundsJsonTablifier": SoundsJsonTablifier.main
        }
    available = list(functions.keys())
    chosen = None
    while True:
        chosen = input("Choose between [%s]: " % ", ".join(available))
        if chosen in available: break
    functions[chosen]()
