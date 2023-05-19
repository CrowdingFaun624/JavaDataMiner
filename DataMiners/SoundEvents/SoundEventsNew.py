import DataMiners.DataMiner as DataMiner
import Utilities.Searcher as Searcher

class SoundEventsNew(DataMiner.DataMiner):
    '''Returns a list of sound events in the provided version.'''
    def search(self, version:str) -> str:
        '''Returns the file path of the desired file.'''
        sound_events_file:list[str] = Searcher.search(version, "client", ["only:file:SoundEvents.java"])
        if len(sound_events_file) > 1:
            print("\n".join(sound_events_file))
            raise FileExistsError("Too many files SoundEvents files found for %s" % version)
        elif len(sound_events_file) == 0:
            raise FileNotFoundError("No SoundEvents file found for %s" % version)
        else: sound_events_file:str = sound_events_file[0]
        return sound_events_file

    def starts_withs(string:str, input_list:list[str]) -> bool:
        '''Returns if the string starts with any of the provided strings.'''
        for input_string in input_list:
            if string.startswith(input_string): return True
        else: return False

    def analyze(self, file_contents:list[str]) -> dict[str,str]:
        '''Takes in the lines of SoundEvents.java, and returns its sound events'''
        START_SOUND_EVENTS = "public class SoundEvents {"
        END_SOUND_EVENTS = ""
        MULTI_EVENT_LENGTH = "    public static final int "
        MULTI_EVENT_DECLARER = "    public static final ImmutableList<Holder.Reference<SoundEvent>> "
        VALID_EVENT_STARTS = ["    public static final SoundEvent ", "    public static final Holder.Reference<SoundEvent> "]
        VALID_ALTERNATE_STARTS = [MULTI_EVENT_LENGTH, MULTI_EVENT_DECLARER]
        FUNCTION_START = "    private "

        multi_length = None
        record_sound_events = False # if it is within the line range that stores sound event ids
        record_alternates = False
        sound_events:dict[str,str] = {}
        alternates:dict[str,tuple[int,str]] = {} # {function name, (length, code name)}
        for line in file_contents:
            line = line.replace("\n", "")
            if line == START_SOUND_EVENTS:
                if record_sound_events: raise ValueError("Multiple start sound events lines detected!")
                record_sound_events = True
                continue # do not record this line as a sound event
            if line == END_SOUND_EVENTS and record_sound_events: # SWITCH SECTIONS
                record_sound_events = False
                record_alternates = True
                function_name = None # Repurposed
                completed_alternates:list[str] = []
            if record_sound_events: # RECORD SOUND EVENTS
                is_event = SoundEventsNew.starts_withs(line, VALID_EVENT_STARTS)
                is_alternate = SoundEventsNew.starts_withs(line, VALID_ALTERNATE_STARTS)
                if not(is_event or is_alternate): raise ValueError("Invalid sound event line:\n%s" % line)
                if is_event: # NORMAL SOUND EVENT
                    code_name = line.lstrip().split(" ")[4]
                    external_name = line.split("\"")[-2]
                    sound_events[code_name] = external_name
                elif is_alternate: # MULTI SOUND EVENT
                    if line.startswith(MULTI_EVENT_LENGTH):
                        multi_length = int(line.split(" ")[-1].replace(";", ""))
                        multi_length_name = line.split(" ")[-3].replace("_VARIANT_COUNT", "")
                    elif line.startswith(MULTI_EVENT_DECLARER):
                        if multi_length is None: raise ValueError("Out of order multi-events declaration and length declaration!")
                        function_name = line.split(".")[-1].replace("();", "")
                        category_name = line.split(" ")[-3].replace("_SOUND_VARIANTS", "")
                        if multi_length_name != category_name:
                            raise ValueError("Multi-events have different names: \"%s\" (length) and \"%s\" (declarer)" % (multi_length_name, category_name))
                        alternates[function_name] = (multi_length, category_name)
                        multi_length, multi_length_name, function_name, category_name = None, None, None, None # reset so errors occur correctly.
            elif record_alternates: # RECORD OTHER FUNCTIONS AND STUFF AFTER MAIN
                if line.startswith(FUNCTION_START):
                    function_name = line.split(" ")[-2].replace("()", "")
                    continue
                if function_name in alternates and "SoundEvents" in line:
                    external_name_start = line.split("\"")[-2]
                    multi_length = alternates[function_name][0]
                    code_name = alternates[function_name][1]
                    code_names = [code_name + "_SOUND_VARIANTS" + ".get(%s)" % index for index in range(multi_length)]
                    external_names = [external_name_start + str(index) for index in range(multi_length)]
                    alternates_dict = dict(zip(code_names, external_names))
                    sound_events.update(alternates_dict)
                    completed_alternates.append(function_name)
        if set(completed_alternates) != set(list(alternates.keys())):
            raise ValueError("Unable to match some alternate functions! (%s vs %s)" % (set(completed_alternates), set(list(alternates.keys()))))
        return SoundEventsNew.sort_dict(sound_events)

    def activate(self, version:str, store:bool=True) -> dict[str,str]:
        if not self.is_valid_version(version):
            raise ValueError("Version %s is not within %s and %s!" % (version, self.start_version, self.end_version))
        sound_events_file = self.search(version)
        with open("./_search"+sound_events_file, "rt") as f:
            sound_events_file_contents = f.readlines()
        sound_events = self.analyze(sound_events_file_contents)
        if store: self.store(version, sound_events, "sound_events.json")
        return sound_events

