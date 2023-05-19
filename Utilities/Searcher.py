'''Searches through a version's decompiled files'''

import os
import shutil

def clear_search() -> None:
    '''Clears the contents of the "_search" folder'''
    file_list = os.listdir("./_search")
    for file in file_list:
        if os.path.isfile("./_search/%s" % file): os.remove("./_search/%s" % file)
        elif os.path.isdir("./_search/%s" % file): shutil.rmtree("./_search/%s" % file)

def in_multi(content:str, terms:list[str]) -> bool:
    '''Returns true if any term is in the content'''
    if not_terms is None: not_terms = []
    output = False
    for term in terms:
        if term in content: output = True
    if output == True:
        for not_term in not_terms:
            if not_term in content: output = False
    return output

def is_in(path:str, terms:list[str], keywords:set[str]) -> bool:
    def get_modifiers(term:str) -> tuple[str, list[str]]:
        '''Returns the term without the modifiers and the list of modifiers'''
        modifiers:list[str] = []
        for available_modifier in available_modifiers:
            if available_modifier+":" in term:
                modifiers.append(available_modifier)
                term = term.replace(available_modifier+":", "", 1)
        return term, modifiers
    def advanced_in(term:tuple[str,list[str]], content:str) -> bool:
        if "not" in term[1]:
            if "only" in term[1]:
                return term[0] != content
            else:
                return term[0] not in content
        else:
            if "only" in term[1]:
                return term[0] == content
            else:
                return term[0] in content
    def should_get_file_content(terms:list[tuple[str,list[str]]]) -> bool:
        '''If the terms contains "file", return False'''
        for term in terms:
            if "file" not in term[1]: return True
        else: return False

    available_modifiers = ["not", "file", "only"]
    terms:list[tuple[str,list[str]]] = [get_modifiers(term) for term in terms]
    if should_get_file_content(terms):
        with open(path, "rt") as f:
            file_content = f.read()
    for term in terms:
        if "file" in term[1]:
            if advanced_in(term, os.path.split(path)[1]): return True
        else:
            if advanced_in(term, file_content): return True
    else: return False

def full_path(version:str, side:str, file_path:str) -> str:
    '''Returns a filepath with the given name in the given version's side'''
    if side not in ("client", "server"): raise ValueError("Side \"%s\" is not a valid side!")
    path = "./_versions/%s/%s_decompiled/%s" % (version, side, file_path)
    if not os.path.exists(path):
        raise FileNotFoundError("file \"%s\" does not exist in %s's %s!" % (file_path, version, side))
    return path

def search(version:str, side:str, terms:list[str], keywords:set[str]=None, additional_path:str="/", output_path:str="", suppress_clear:bool=False) -> list[str]:
    '''Searches through a version's decompiled content to search for files containg the terms, with the keywords. Modify `output_path` to make subfolders of "_search".
    Will return items such as "/net/minecraft/world/entity/monster/Evoker.java.
    Modifiers can be attached to terms using colons, such as "only:file:SoundEvents.java". Here is a list of them, and their functions:
    * `not`: returns the opposite of normal
    * `only`: returns if the content exactly matches the term, instead of just containing it
    * `file`: uses the file name instead of the file contents.'''
    if keywords is None: keywords = set()
    if additional_path == "/" and not suppress_clear: clear_search() # if it's the top iteration
    if not output_path.startswith("/"): output_path = "/" + output_path
    path = "./_versions/%s/%s_decompiled%s" % (version, side, additional_path)
    if side not in ("client", "server"): raise ValueError("Side \"%s\" is not a valid side!")
    if not os.path.exists(path): raise FileNotFoundError("Version \"%s\"'s %s does not exist!" % (version, side))
    file_list = os.listdir(path)
    output = []
    for file in file_list:
        file_path = path + file # ./versions/1.19.3/client_decompiled/net/file.java
        cut_path = additional_path + file # such as /net/file.java
        if os.path.isdir(file_path):
            output.extend(search(version, side, terms, keywords, additional_path + file + "/", output_path))
        elif os.path.isfile(file_path):
            if is_in(file_path, terms, keywords):
                output.append(additional_path + file)
                copy_path = "./_search" + output_path + cut_path
                os.makedirs(os.path.split(copy_path)[0], exist_ok=True)
                shutil.copy(file_path, copy_path)
    return output
        
def main() -> None:
    possible_versions = os.listdir("./_versions")
    decompiled_versions = []
    for version in possible_versions:
        if os.path.exists("./_versions/%s/client_decompiled" % version):
            decompiled_versions.append(version)
    chosen_version = None
    while True:
        chosen_version = input("Choose from the following versions:\n%s\n" % "\n".join(decompiled_versions))
        if chosen_version in decompiled_versions: break
    search_terms = input("Search terms: ").split(" ")
    search(chosen_version, "client", search_terms, [])

if __name__ == "__main__":
    main()
