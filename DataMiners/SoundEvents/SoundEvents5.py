import os

import DataMiners.DataMiner as DataMiner
import DataMiners.Language.Language as Language
import DataMiners.Notes.Notes as Notes
import DataMiners.Records.Records as Records
import DataMiners.SoundType.SoundType as SoundType
import Importer.AssetsIndex as AssetsIndex

class SoundEvents5(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.records = "records.ogg"
        self.sound_type_keys = ["dig", "step", "dig2"]
        self.grab_assets = True
        if "records" in kwargs:
            self.records = kwargs["records"]
        if "sound_type_keys" in kwargs:
            self.sound_type_keys = kwargs["sound_type_keys"]
        if "grab_assets" in kwargs:
            self.grab_assets = kwargs["grab_assets"]
    
    def search(self, version:str, subfolder:str="") -> list[str]:
        output:list[str] = []
        file_list = os.listdir("./_versions/%s/client_decompiled%s" % (version, subfolder))
        for file in file_list:
            full_path = os.path.join("./_versions/%s/client_decompiled%s" % (version, subfolder), file)
            if os.path.isdir(full_path):
                output.extend(self.search(version, subfolder + "/" + file))
            else:
                with open(full_path, "rt") as f:
                    file_content = f.read()
                output.extend(self.get_strings(file_content, file, version))
        return output
    
    def get_strings(self, file_contents:str, file_name:str, version:str) -> list[str]:
        def is_significant_quote(char:str) -> bool:
            if char not in ("\"", "\'"): return False
            elif not in_quote: return True
            else: return quote_type == char
        output:list[str] = []
        in_quote = False
        quote_type = None
        is_escaped = False
        is_in_comment = False
        skip_to_next_line = False
        for index, char in enumerate(file_contents):
            next_char = file_contents[index + 1] if index < len(file_contents) - 1 else ""
            if char + next_char == "/*" and not in_quote: is_in_comment = True
            if char + next_char == "*/" and not in_quote: is_in_comment = False
            if char + next_char == "//" and not in_quote: skip_to_next_line = True
            if char == "\n" and skip_to_next_line: skip_to_next_line = False
            if is_in_comment or skip_to_next_line: continue
            if is_escaped:
                if in_quote: current_quote += char
                is_escaped = False
                continue
            if char == "\\": is_escaped = True; continue
            if is_significant_quote(char):
                if in_quote:
                    in_quote = False
                    if quote_type == "\"": output.append(current_quote) # only " quotes since ' quotes mean single character apparently
                    quote_type = None
                    current_quote = ""
                    continue
                else:
                    in_quote = True
                    quote_type = char
                    current_quote = ""
                    continue
            if in_quote:
                if char == "\n":
                    print(current_quote) # intended print line
                    raise ValueError("newline in file %s in SoundEvents in %s: \"%s\"" % (file_name, version))
                current_quote += char
        return output

    def ensure_no_duplicates(self, string_list:list[str], version:str) -> None:
        if len(set(string_list)) != len(string_list):
            already:set[str] = set()
            duplicates:list[str] = []
            for item in string_list:
                if item in already: duplicates.append(item)
                already.add(item)
            raise ValueError("SoundEvents has duplicate entries in %s: %s" % (version, ", ".join(duplicates)))

    def filter_duplicates(self, string_list:list[str]) -> list[str]:
        return list(set(string_list))

    def analyze(self, string_list:list[str], version:str) -> list[str]:
        output = self.filter_duplicates(string_list)
        # output = self.replace_minecraft_colon(output)
        # output = self.filter_illegal_characters(output)
        # output = self.filter_no_periods(output)
        # output = self.filter_strange_underscores(output)
        # output = self.filter_language_keys(output, language)
        # output = self.filter_wonky_periods(output)
        # output = self.filter_illegal_endings(output)
        # output = self.filter_illegal_beginnings(output)
        # output = self.filter_numbery_items(output)
        # output = self.filter_illegal_items(output)
        # output = self.add_sound_type_events(output, sound_type_data)
        # output = self.add_records(output, version, records)
        # output = self.add_notes(output, notes_data)
        # self.ensure_no_duplicates(output, version)
        return sorted(output)

    def activate(self, version:str, store:bool=True) -> dict[str,str]|list[str]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        literal_string_list = self.search(version)
        sound_events = self.analyze(literal_string_list, version)
        if store: self.store(version, sound_events, "sound_events.json")
        return literal_string_list
