'''Condenses a mappings file to only include finished mappings (for diffing)'''

import os

import Importer.MappingsEncoder as MappingsEncoder

def get_line(input_line:str) -> str:
    '''Strips a line into the wanted content'''
    return input_line.lstrip().split(" ")[-1]

def fetch_condensed_mappings(version:str, side:str, store:bool=True) -> str:
    if side not in ("client", "server"): raise ValueError("%s is an invalid side!" % side)
    mappings = MappingsEncoder.get_mappings(version, side)
    output = ""
    for line in mappings.split("\n"):
        is_variable =  line.startswith("\t")
        leading_characters = "\t" if is_variable else ""
        output += leading_characters + get_line(line) + "\n"
    if store:
        with open("./_versions/%s/%s_mappings_compressed.txt" % (version, side), "wt") as f:
            f.write(output)
    return output

def get_condensed_mappings(version:str, side:str) -> str:
    if os.path.exists("./_versions/%s/%s_mappings_compressed.txt"):
        with open("./_versions/%s/%s_mappings_compressed.txt", "rt") as f:
            return f.read()
    else: return fetch_condensed_mappings(version, side, store=True)

def main() -> None:
    possible_versions = os.listdir("./_versions")
    possible_versions.remove("version_manifest.json")
    chosen_version = None
    while True:
        chosen_version = input("Choose from the following versions:\n%s\n" % "\n".join(possible_versions))
        if chosen_version in possible_versions: break
    fetch_condensed_mappings(chosen_version, "client")
    print("Success!")

if __name__ == "__main__":
    main()
