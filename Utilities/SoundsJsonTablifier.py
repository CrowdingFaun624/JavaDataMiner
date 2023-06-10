import json
import os
import random

import Comparison.Comparer as Comparer
import Comparison.Difference as D
import DataMiners.DataMiner as DataMiner
import DataMiners.Subtitles.Subtitles as Subtitles
import Importer.AssetImporter as AssetImporter
import Importer.Manifest as Manifest
import Importer.VersionJson as VersionJson

UPCOMING = "<wbr>{{Upcoming|<NEWRELEASE>}}"
UNTIL = "<wbr>{{Until|<NEWRELEASE>}}"
CHANGE = "%s" + UNTIL + " " + "%s" + UPCOMING
CHANGE_BR = "%s" + UNTIL + "<br>" + "%s" + UPCOMING
ADD = "%s" + UPCOMING
REMOVE = "%s" + UNTIL


def get_files(old_version:str, new_version:str) -> list[dict]:
    '''Returns a list of one or two sounds.json dictionaries (order: old, new)'''
    old_index_id, new_index_id = VersionJson.get_asset_index(old_version), VersionJson.get_asset_index(new_version)
    old_file = AssetImporter.fetch_asset(old_index_id, "minecraft/sounds.json", "j", old_version)
    new_file = AssetImporter.fetch_asset(new_index_id, "minecraft/sounds.json", "j", new_version)
    if new_file == old_file: return [new_file]
    else: return [old_file, new_file]

'''Internal sounds.json format:
{
    "sound.key.something": {
        "sounds": {
            "path/path": {
                "volume": 0.4
            },
            "path/path2": {
                
            }
        }
    }
}'''

def reformat(soundsjson:dict) -> dict:
    def reformat_sounds(sound_list:list[str|dict[str,int|float|bool]], sound_event_name:str="Unknown") -> dict[str,dict[str,int|float|bool]]:
        output = {}
        index = 0
        for sound in sound_list:
            if isinstance(sound, str):
                output[sound] = {}
            elif isinstance(sound, dict):
                sound_name = sound["name"]
                vars = sound.copy()
                del vars["name"]
                output[sound_name + "|" + str(index)] = vars
            else: raise KeyError("Invalid sound type (\"%s\")(not str or dict) in sound event \"%s\"!" % (type(sound), sound_event_name))
            index += 1
        return output
    output = {}
    for sound_event_name, sound_event_content in list(soundsjson.items()):
        sound_event_name:str; sound_event_content:dict
        new_sound_event = sound_event_content.copy()
        new_sounds = reformat_sounds(new_sound_event["sounds"], sound_event_name)
        new_sound_event["sounds"] = new_sounds
        output[sound_event_name] = new_sound_event
    return output

def get_table(comparison:dict, subtitles_comparison:dict[str,str|D.Difference]) -> str:
    HEADER = "{| class=\"wikitable\" data-description=\"List of sound events\"\n! Sound Event !! Sound File Used !! Subtitle Data Value !! Subtitle Displayed\n"
    FOOTER = "|}\n\n<noinclude>[[Category:Data pages]]\n[[ja:Sounds.json/Java Editionの値]]\n[[ru:Sounds.json/Значения в Java Edition]]\n[[uk:Sounds.json/Значення в Java Edition]]\n[[zh:Sounds.json/Java版数据值]]\n</noinclude>"
    JOINER = "|-\n"
    rows:list[str] = []
    for sound_event_name, sound_event_content in list(comparison.items()):
        if isinstance(sound_event_content, D.Difference):
            if sound_event_content.is_change():
                raise ValueError("A sound event has a type of D.CHANGE, which should not happen!")
            elif sound_event_content.is_addition():
                rows.append(get_row(sound_event_name, sound_event_content.new, subtitles_comparison, event_append=UPCOMING))
            elif sound_event_content.is_removal():
                rows.append(get_row(sound_event_name, sound_event_content.old, subtitles_comparison, event_append=UNTIL))
        else:
            rows.append(get_row(sound_event_name, sound_event_content, subtitles_comparison))
    return HEADER + JOINER + JOINER.join(rows) + FOOTER

def get_row(sound_event_name:str, sound_event_content:dict[str,str|float|dict[str,str|bool|float|int]], subtitles_comparison:dict[str,str|D.Difference], event_append:str="") -> str:
    
    HEADER = "| "
    FOOTER = "\n"
    JOINER = " || "
    columns = []
    columns.append(sound_event_name + event_append)
    columns.append(get_sound_column(sound_event_content["sounds"]))
    columns.append(get_subtitle_key_column(sound_event_content))
    columns.append(get_subtitle_value_column(sound_event_content, subtitles_comparison))
    return (HEADER + JOINER.join(columns) + FOOTER).replace("|  |", "| |")

def get_subtitle_key_column(sound_event_content:dict[str,str]) -> str:
        if "subtitle" not in sound_event_content: return ""
        subtitle = sound_event_content["subtitle"]
        if isinstance(subtitle, D.Difference):
            if subtitle.is_change():
                return CHANGE_BR % (subtitle.old, subtitle.new)
            elif subtitle.is_addition():
                return ADD % subtitle.new
            elif subtitle.is_removal():
                return REMOVE % subtitle.old
        else: return subtitle

def get_subtitle_value_column(sound_event_content:dict[str,str], subtitles_comparison) -> str:
        def get_subtitle(key:str, version:str="both") -> str:
            '''Gets the subtitle value from key. Set `version` to "old", "new", or "both"'''
            if key in subtitles_comparison:
                if version == "both": return subtitles_comparison[key]
                else:
                    value = subtitles_comparison[key]
                    if isinstance(value, D.Difference):
                        if version == "old": return value.old
                        elif version == "new": return value.new
                        else: raise ValueError
                    else: return value
            else: return "''None''"
        if "subtitle" not in sound_event_content:return ""
        subtitle_key = sound_event_content["subtitle"]
        if isinstance(subtitle_key, D.Difference):
            subtitle_key_old = subtitle_key.old
            subtitle_key_new = subtitle_key.new
            subtitle_value_old = get_subtitle(subtitle_key_old, "old")
            subtitle_value_new = get_subtitle(subtitle_key_new, "new")
            if subtitle_key.is_change():
                return CHANGE_BR % (subtitle_value_old, subtitle_value_new)
            elif subtitle_key.is_addition():
                return ADD % subtitle_value_new
            elif subtitle_key.is_removal():
                return REMOVE % subtitle_value_old
        else:
            subtitle_value = get_subtitle(subtitle_key)
            if isinstance(subtitle_value, D.Difference):
                if subtitle_value.is_change():
                    return CHANGE_BR % (subtitle_value.old, subtitle_value.new)
                elif subtitle_value.is_addition():
                    return ADD % subtitle_value.new
                elif subtitle_value.is_removal():
                    return REMOVE % subtitle_value.old
            else: return subtitle_value

def get_sound_column(sounds:dict[str,dict[str,str|bool|float|int]]) -> str:
    JOINER = "<br>"
    sounds_strings = []
    for sound_name, sound_content in list(sounds.items()):
        if isinstance(sound_content, D.Difference):
            if sound_content.is_change():
                raise ValueError("A sound has a type of D.CHANGE, which should not happen!")
            elif sound_content.is_addition():
                sounds_strings.append(get_sound_vars(sound_name, sound_content.new, sound_append=UPCOMING))
            elif sound_content.is_removal():
                sounds_strings.append(get_sound_vars(sound_name, sound_content.old, sound_append=UNTIL))
        else:
            sounds_strings.append(get_sound_vars(sound_name, sound_content))
    return JOINER.join(sounds_strings)

def get_sound_vars(sound_name:str, sound_content:dict[str,str|bool|float|int], sound_append:str="") -> str:
    def format_simple(data:str|int|float|bool) -> str:
        if isinstance(data, str): return data
        elif isinstance(data, bool): return json.dumps(data)
        else: return str(data)
    JOINER = ", "
    EQUALS = " = "
    true_sound_name = sound_name.split("|")[0]
    variables = [true_sound_name + sound_append]
    for var_name, var_value in list(sound_content.items()):
        if isinstance(var_value, D.Difference):
            if var_value.is_change():
                value = CHANGE % (var_value.old, var_value.new)
            elif var_value.is_addition():
                value = ADD % var_value.new
            elif var_value.is_removal():
                value = REMOVE % var_value.old
        else:
            value = var_value
        variables.append(var_name + EQUALS + format_simple(value))
    return JOINER.join(variables)

def write_file(table:str, version:str) -> None:
    if not os.path.exists("./_versions/%s/data" % version):
        os.mkdir("./_versions/%s/data" % version)
    with open("./_versions/%s/data/sounds.json_table.txt" % version, "wt", encoding="UTF8") as f:
        f.write(table)

def sort_dict(input_dict:dict) -> dict:
    output = list(input_dict.items())
    output = sorted(output)
    output = dict(output)
    return output

def main() -> None:
    OLD_VERSION, NEW_VERSION = Manifest.get_latest()
    files = get_files(OLD_VERSION, NEW_VERSION)
    new_files = []
    for file in files:
        new_files.append(reformat(file))
    if len(new_files) == 2:
        comparison = sort_dict(Comparer.compare(*new_files))
    elif len(new_files) == 1:
        comparison = new_files[0]
    else: raise ValueError("Invalid number of sounds.json files in SoundsJsonTablifier: %s" % len(new_files))
    old_subtitles = DataMiner.get_dataminer(OLD_VERSION, Subtitles.dataminers).activate(OLD_VERSION)
    new_subtitles = DataMiner.get_dataminer(NEW_VERSION, Subtitles.dataminers).activate(NEW_VERSION)
    subtitles_comparison = Comparer.compare(old_subtitles, new_subtitles)
    # print(Comparer.stringify_data(comparison))
    table = get_table(comparison, subtitles_comparison)
    new_release = input("What is the latest snapshot for? ")
    table = table.replace("<NEWRELEASE>", "JE " + new_release)
    write_file(table, NEW_VERSION)

if __name__ == "__main__":
    main()
