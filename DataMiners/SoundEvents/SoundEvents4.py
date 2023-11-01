import DataMiners.DataMiner as DataMiner
import DataMiners.LiteralStrings.LiteralStrings as LiteralStrings
import DataMiners.Notes.Notes as Notes
import DataMiners.Records.Records as Records
import DataMiners.SoundType.SoundType as SoundType
import Importer.AssetsIndex as AssetsIndex
import Utilities.LanguageKeyGenerator as LanguageKeyGenerator

class SoundEvents4(DataMiner.DataMiner):
    def init(self, **kwargs) -> None:
        self.records = "records.ogg"
        self.sound_type_keys = ["dig", "step", "dig2"]
        self.grab_assets = True
        self.manual_additions:list[str] = []
        if "records" in kwargs:
            self.records = kwargs["records"]
        if "sound_type_keys" in kwargs:
            self.sound_type_keys = kwargs["sound_type_keys"]
        if "grab_assets" in kwargs:
            self.grab_assets = kwargs["grab_assets"]
        if "manual_additions" in kwargs:
            self.manual_additions = kwargs["manual_additions"]

    def ensure_no_duplicates(self, string_list:list[str], version:str) -> None:
        if len(set(string_list)) != len(string_list):
            already:set[str] = set()
            duplicates:list[str] = []
            for item in string_list:
                if item in already: duplicates.append(item)
                already.add(item)
            raise ValueError("SoundEvents has duplicate entries in %s: %s" % (version, ", ".join(duplicates)))

    def replace_minecraft_colon(self, string_list:list[str]) -> list[str]:
        output:list[str] = []
        for item in string_list:
            if item.startswith("minecraft:"):
                output.append(item.replace("minecraft:", "", 1))
            else: output.append(item)
        return output

    def filter_illegal_characters(self, string_list:list[str]) -> list[str]:
        ILLEGAL_CHARACTERS = set(" !@#$%^&*()-+=[]{}\\|;:\"\',<>/?`~")
        output:list[str] = []
        for item in string_list:
            if item == "": continue
            string_is_bad = False
            for illegal_character in ILLEGAL_CHARACTERS:
                if illegal_character in item: string_is_bad = True; break
            if string_is_bad: continue
            else: output.append(item)
        return output

    def filter_duplicates(self, string_list:list[str]) -> list[str]:
        return list(set(string_list))

    def filter_no_periods(self, string_list:list[str]) -> list[str]:
        output:list[str] = []
        for item in string_list:
            if item.count(".") > 0: output.append(item)
        return output

    def filter_strange_underscores(self, string_list:list[str]) -> list[str]:
        output:list[str] = []
        for item in string_list:
            split_items = item.split(".")
            is_bad = False
            for split_item in split_items:
                if split_item.endswith("_") or split_item.startswith("_"): is_bad = True; break
            if not is_bad: output.append(item)
        return output

    def filter_language_keys(self, string_list:list[str], language:set[str]) -> list[str]:
        if language is None: return string_list
        output:list[str] = []
        for item in string_list:
            if item not in language: output.append(item)
        return output

    def filter_wonky_periods(self, string_list:list[str]) -> list[str]:
        output:list[str] = []
        for item in string_list:
            if not (item.startswith(".") or item.endswith(".") or ".." in item): output.append(item)
        return output

    def filter_illegal_endings(self, string_list:list[str]) -> list[str]:
        ILLEGAL_ENDINGS = [".png", ".desktop", ".txt", ".dat", ".dat_old", ".old", ".tmp", ".dat_new", ".dat_mcr", ".dnscontextfactory", ".main", ".bone", ".nose", ".skin", ".box", ".nostril", ".ear1", ".ear2", ".upperlip", ".scale", ".log", ".body", ".properties", ".jaw", ".upperhead", ".mcmeta", ".json", ".lang"]
        output:list[str] = []
        for item in string_list:
            is_bad = False
            for illegal_ending in ILLEGAL_ENDINGS:
                if item.lower().endswith(illegal_ending.lower()): is_bad = True; break
            if not is_bad: output.append(item)
        return output

    def filter_illegal_beginnings(self, string_list:list[str]) -> list[str]:
        ILLEGAL_BEGINNINGS = ["generic.", "java.", "util.", "rcon.", "commands.", "net.", "query.", "com.", "os.", "sun.", "chat.", "horse.", "stat.", "mco.", "org.", "alg.", "algorithm", "certpath", "certstore.", "cipher.", "keystore.", "mac.", "secretkeyfactory.", "x509", "javax.", "options.", "language.", "achievement.", "gui.", "potion.", "performance."]
        output:list[str] = []
        for item in string_list:
            is_bad = False
            for illegal_beginning in ILLEGAL_BEGINNINGS:
                if item.lower().startswith(illegal_beginning.lower()): is_bad = True; break
            if not is_bad: output.append(item)
        return output

    def filter_numbery_items(self, string_list:list[str]) -> list[str]:
        output:list[str] = []
        for item in string_list:
            split_items = item.split(".")
            is_bad = True
            for split_item in split_items:
                if not split_item.isdigit(): is_bad = False; break
            if not is_bad: output.append(item)
        return output

    def filter_illegal_items(self, string_list:list[str]) -> list[str]:
        ILLEGAL_ITEMS = ["session.lock", "container.beacon", "item.charcoal", "item.coal", "zombie.spawnReinforcements", "potion.healthBoost", "Style.ROOT", "supported.n", "explosion.player", "death.fell.accident", "user.home", "line.separator", "selectServer.editButton", "deathScreen.leaveServer", "disconnect.spam", "file.separator", "www.minecraft.net", "menu.playdemo"]
        output:set[str] = set(string_list)
        for illegal_item in ILLEGAL_ITEMS:
            if illegal_item in output: output.remove(illegal_item)
        return list(output)

    def add_sound_type_events(self, string_list:list[str], sound_types:dict[str,dict[str,int|str]]) -> list[str]:
        if sound_types is None: return string_list
        SOUND_TYPE_KEYS = self.sound_type_keys
        output = set(string_list)
        for sound_type in list(sound_types.values()):
            for sound_type_key in SOUND_TYPE_KEYS:
                output.add(sound_type[sound_type_key])
        return list(output)

    def add_records(self, string_list:list[str], version:str, records:list[str]) -> list[str]:
        if records is None: return string_list
        if "records.far" in string_list: return string_list # some versions have records already in them
        output = string_list
        for record in records:
            output.append("records." + record)
        return output

    def add_notes(self, string_list:list[str], notes:list[str]) -> list[str]:
        if notes is None: return string_list
        for note in notes:
            string_list.append("note." + note)
        return string_list

    def add_manual_additions(self, string_list:list[str], manual_additions:list[str]) -> list[str]:
        for addition in manual_additions:
            if addition not in string_list: string_list.append(addition)
        return string_list

    def analyze(self, string_list:list[str], version:str, language:set[str], sound_type_data:dict[str,dict[str,int|str]], notes_data:list[str], records:list[str]) -> list[str]:
        output = self.filter_duplicates(string_list)
        output = self.replace_minecraft_colon(output)
        output = self.filter_illegal_characters(output)
        output = self.filter_no_periods(output)
        output = self.filter_strange_underscores(output)
        output = self.filter_language_keys(output, language)
        output = self.filter_wonky_periods(output)
        output = self.filter_illegal_endings(output)
        output = self.filter_illegal_beginnings(output)
        output = self.filter_numbery_items(output)
        output = self.filter_illegal_items(output)
        output = self.add_sound_type_events(output, sound_type_data)
        output = self.add_records(output, version, records)
        output = self.add_notes(output, notes_data)
        output = self.add_manual_additions(output, self.manual_additions)
        self.ensure_no_duplicates(output, version)
        return sorted(output)

    def activate(self, version:str, store:bool=True) -> dict[str,str]|list[str]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        literal_string_list = LiteralStrings.LiteralStrings.get_data_file(version)
        # so many extra data files
        language_data = LanguageKeyGenerator.get_all_language_keys()
        sound_type_data = SoundType.SoundType.get_data_file(version)
        notes_data = Notes.Notes.get_data_file(version)
        records:list[str] = Records.Records.get_data_file(version)
        # end extra data files
        sound_events = self.analyze(literal_string_list, version, language_data, sound_type_data, notes_data, records)
        if store: self.store(version, sound_events, "sound_events.json")
        return sound_events
