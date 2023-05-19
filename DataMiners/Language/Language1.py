import os

import DataMiners.DataMiner as DataMiner
import Importer.JarImporter as JarImporter
import Importer.Manifest as Manifest

class Language1(DataMiner.DataMiner):
    def get_file_name(version:str) -> str:
        '''Returns the file path of the lang file based off of the version.'''
        manifest = Manifest.get_manifest()
        given_version_id = Manifest.get_version_id(version, manifest)
        if given_version_id >= Manifest.get_version_id("16w32a", manifest):
            return "assets/minecraft/lang/en_us.lang"
        elif given_version_id >= Manifest.get_version_id("13w26a", manifest):
            return "assets/minecraft/lang/en_US.lang"
        else:
            return "lang/en_US.lang"

    def activate(self, version:str, store:bool=True) -> dict[str,str]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        JarImporter.get_unzipped_client(version)
        file_name = Language1.get_file_name(version)
        if not os.path.exists("./_versions/%s/client_unzipped/%s" % (version, file_name)):
            raise FileNotFoundError("Lang file for %s cannot be found!" % version)
        with open("./_versions/%s/client_unzipped/%s" % (version, file_name), "rt", encoding="utf8") as f:
            file_lines = f.readlines()
        translations = {}
        for line in file_lines:
            if line == "\n": continue
            if line.endswith("\n"): line = line[:-1] # remove trailing newline
            key = line.split("=")[0]
            value = "=".join(line.split("=")[1:]) # exclude key but just in case "=" is in value
            translations[key] = value
        translations = Language1.sort_dict(translations)
        if store: self.store(version, translations, "language.json")
        return translations
