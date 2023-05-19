import os
import json

import DataMiners.DataMiner as DataMiner
import Importer.JarImporter as JarImporter

class LanguageNew(DataMiner.DataMiner):
    def activate(self, version:str, store:bool=True) -> dict[str,str]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        JarImporter.get_unzipped_client(version)
        file_name = "assets/minecraft/lang/en_us.json"
        if not os.path.exists("./_versions/%s/client_unzipped/%s" % (version, file_name)):
            raise FileNotFoundError("Lang file for %s cannot be found!" % version)
        with open("./_versions/%s/client_unzipped/%s" % (version, file_name), "rt", encoding="utf8") as f:
            file_data = f.read()
        file_data = json.loads(file_data)
        file_data = LanguageNew.sort_dict(file_data)
        if store: self.store(version, file_data, "language.json")
        return file_data