import Comparison.Comparers as Comparers
import Comparison.CompareAllVersions as CompareAllVersions
import DataMiners.DataMiners as DataMiners
import Importer.Decompiler as Decompiler
import Importer.JarImporter as JarImporter
import Importer.JarRemapper as JarRemapper
import Utilities.AssetsStorage as AssetsStorage
import Utilities.DataRedoer as DataRedoer
import Utilities.DecompileZipper as DecompileZipper
import Utilities.LanguageKeyGenerator as LanguageKeyGenerator
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
        "LanguageKeyGenerator": LanguageKeyGenerator.main,
        "MappingCondenser": MappingCondenser.main,
        "PlaylistAssembler": PlaylistAssembler.main,
        "Remapper": JarRemapper.main,
        "Searcher": Searcher.main,
        "SearcherCompare": Searcher.search_compare_user,
        "SoundsJsonTablifier": SoundsJsonTablifier.main
        }
    available = list(functions.keys())
    chosen = None
    while True:
        chosen = input("Choose between [%s]:\n" % ", ".join(available))
        if chosen in available: break
    functions[chosen]()
