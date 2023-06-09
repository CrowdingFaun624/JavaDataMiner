import os

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

class Records1(DataMiner.DataMiner):
    def search(self, version:str) -> str:
        '''Returns the file path of Items.java (e.g. dx.java)'''
        blocks_files = Searcher.search(version, "client", ["2000", "2001"], set(["and"]))
        if len(blocks_files) > 1:
            raise FileExistsError("Too many Records files found for %s:\n%s" % (version, "\n".join(blocks_files)))
        elif len(blocks_files) == 0:
            raise FileNotFoundError("No Records file found for %s" % version)
        else: blocks_file = blocks_files[0]
        return blocks_file

    def analyze(self, file_contents:list[str], version:str) -> list[str]:
        recording = False
        output:list[str] = []
        for line in file_contents:
            line = line.rstrip()
            if "2000" in line and "\"" in line: recording = True
            elif "\"" not in line and recording: recording = False; break
            if recording:
                record_name = line.split("\"")[1]
                if record_name not in ("13", "cat", "blocks", "chirp", "far", "mall", "mellohi", "stal", "strad", "ward", "11"):
                    raise ValueError("Record \"%s\" in line \"%s\" in Records in %s is not a recognized record name!" % (record_name, line, version))
                output.append(record_name)
        if len(output) == 0: raise ValueError("Did not find any records in %s!" % version)
        return output

    def activate(self, version:str, store:bool=True) -> dict[int,dict[str,any]]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        blocks_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", blocks_file), "rt") as f:
            items_file_contents = f.readlines()
        blocks = self.analyze(items_file_contents, version)
        if store: self.store(version, blocks, "records.json")
        return blocks
