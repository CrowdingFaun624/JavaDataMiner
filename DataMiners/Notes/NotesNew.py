import os

import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

class NotesNew(DataMiner.DataMiner):
    def search(self, version:str) -> str:
        '''Returns the path of Notes.java (e.g. "aos.java")'''
        notes_files = Searcher.search(version, "client", ["\"note.\""], ["and"])
        if len(notes_files) > 1:
            raise FileExistsError("Too many files found for %s in Notes:\n%s" % (version, "\n".join(notes_files)))
        elif len(notes_files) == 0:
            raise FileNotFoundError("No file found for %s in Notes!" % version)
        else: notes_files = notes_files[0]
        return notes_files
    
    def analyze(self, file_contents:list[str], version:str) -> list[str]:
        DEFAULT_DECLARATION = "        String string = "
        NOTE_DECLARATION = "            string = "
        default_note = None
        other_notes:list[str] = []
        for line in file_contents:
            line = line.rstrip()
            if line.startswith(DEFAULT_DECLARATION):
                default_note = line.split("\"")[1]
            elif line.startswith(NOTE_DECLARATION):
                other_notes.append(line.split("\"")[1])
        if default_note is None:
            raise ValueError("Failed to find default note in Notes in %s!" % version)
        if other_notes == []:
            raise ValueError("Failed to find other notes in Notes in %s!" % version)
        output = [default_note]
        output.extend(other_notes)
        return output
    
    def activate(self, version:str, store:bool=True) -> list[str]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        notes_file = self.search(version)
        with open(os.path.join("./_versions", version, "client_decompiled", notes_file), "rt") as f:
            notes_file_contents = f.readlines()
        sound_types = self.analyze(notes_file_contents, version)
        if store: self.store(version, sound_types, "notes.json")
        return sound_types
