'''Searches through a version's decompiled files'''

import os
import shutil

try:
    import Importer.Decompiler as Decompiler
except ImportError: pass

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
    def get_modifiers(term:str) -> tuple[str, dict[str,list[any]]]:
        '''Returns the term without the modifiers and the list of modifiers'''
        modifiers:dict[str,list[any]] = {}
        # for available_modifier in available_modifiers:
        #     if available_modifier+":" in term:
        #         modifiers.append(available_modifier)
        #         term = term.replace(available_modifier+":", "", 1)
        # return term, modifiers
        while True:
            had_term = False
            for available_modifier in available_modifiers:
                if term.startswith(available_modifier + ":") or term.startswith(available_modifier + "("): # notes plingy plingy pling hahaha
                    had_term = True
                    if term.startswith(available_modifier + "("):
                        modifier_parameters = term.split("(")[1].split(")")[0].split(",")
                        modifier_parameters = [modifier_parameter.strip() for modifier_parameter in modifier_parameters]
                    else: modifier_parameters = []
                    modifiers[available_modifier] = modifier_parameters
                    term = ":".join(term.split(":")[1:]) # remove first term
            if not had_term: break
        return term, modifiers
    def advanced_in(term:str, modifiers:dict[str,list[any]], content:str) -> bool:
        if "not" in modifiers:
            if "only" in modifiers:
                return term != content
            else:
                return term not in content
        else:
            if "only" in modifiers:
                return term == content
            else:
                return term in content
    def get_count_condition_satisfied(term:str, modifiers:dict[str,list[any]], content:str) -> bool:
        condition_type:str = modifiers["count"][0]
        condition_number:int = int(modifiers["count"][1])
        if condition_type in ("==", "="):
            output = content.count(term) == condition_number
        elif condition_type == "<":
            output = content.count(term) < condition_number
        elif condition_type == "<=":
            output = content.count(term) <= condition_number
        elif condition_type == ">":
            output = content.count(term) > condition_number
        elif condition_type == ">=":
            output = content.count(term) >= condition_number
        elif condition_type == "!=":
            output = content.count(term) >= condition_number
        if "not" in modifiers: return not output
        else: return output
    def should_get_file_content(terms:list[tuple[str,list[str]]]) -> bool:
        '''If the terms contains "file", return False'''
        for term in terms:
            if "file" not in term[1]: return True
        else: return False
    def get_content_to_search(term:str, modifiers:dict[str,list[any]], file_content:str, path:str) -> str:
        '''Returns the file name or file contents based on the modifiers'''
        if "file" in modifiers:
            output = os.path.split(path)[1]
        else:
            output = file_content
        if "nocaps" in modifiers:
            output = output.lower()
        return output

    available_modifiers = ["not", "file", "only", "count", "nocaps"]
    terms:list[tuple[str,dict[str,list[any]]]] = [get_modifiers(term) for term in terms]
    if should_get_file_content(terms):
        with open(path, "rt") as f:
            file_content = f.read()
    else: file_content = ""
    
    for term, modifiers in terms:
        contains_this_term = False
        if "nocaps" in modifiers: term = term.lower()
        content_to_search = get_content_to_search(term, modifiers, file_content, path)
        if advanced_in(term, modifiers, content_to_search):
            contains_this_term = True
            if "count" in modifiers:
                contains_this_term = get_count_condition_satisfied(term, modifiers, file_content) # special probably slower search for count modifier
        
        if "and" in keywords:
            if contains_this_term is False:
                return False
            else: continue
        else: # doesn't contain and
            if contains_this_term is True:
                return True
            else: continue
    else:
        if "and" in keywords: return True
        else: return False

def full_path(version:str, side:str, file_path:str) -> str:
    '''Returns a filepath with the given name in the given version's side'''
    if side not in ("client", "server"): raise ValueError("Side \"%s\" is not a valid side!")
    path = "./_versions/%s/%s_decompiled/%s" % (version, side, file_path)
    if not os.path.exists(path):
        raise FileNotFoundError("file \"%s\" does not exist in %s's %s!" % (file_path, version, side))
    return path

def search(version:str, side:str, terms:list[str], keywords:set[str]=None, additional_path:str="/", output_path:str="", actually_copy_files:bool=False, suppress_clear:bool=False, allow_decompile:bool=False) -> list[str]:
    '''Searches through a version's decompiled content to search for files containg the terms, with the keywords. Modify `output_path` to make subfolders of "_search".
    Will return items such as "net/minecraft/world/entity/monster/Evoker.java.
    Modifiers can be attached to terms using colons, such as "only:file:SoundEvents.java". Here is a list of them, and their functions:
    * `not`: returns the opposite of normal
    * `only`: returns if the content exactly matches the term, instead of just containing it
    * `file`: uses the file name instead of the file contents.
    * `count(<=,==,>,>=,<,<=,!=>,[int]): how many times the string shows up'''
    if allow_decompile and not os.path.exists(os.path.join("./_versions", version, "%s_decompiled" % side)): Decompiler.get_decompiled(version, side)
    if keywords is None: keywords = set()
    if additional_path == "/" and not suppress_clear: clear_search() # if it's the top iteration
    if not output_path.startswith("/"): output_path = "/" + output_path
    path = "./_versions/%s/%s_decompiled%s" % (version, side, additional_path)
    if side not in ("client", "server"): raise ValueError("Side \"%s\" is not a valid side!")
    if not os.path.exists(path): Decompiler.get_decompiled(version, side)# raise FileNotFoundError("Version \"%s\"'s %s does not exist!" % (version, side))
    file_list = os.listdir(path)
    output:list[str] = []
    for file in file_list:
        file_path = path + file # ./versions/1.19.3/client_decompiled/net/file.java
        cut_path = additional_path + file # such as /net/file.java
        if os.path.isdir(file_path):
            output.extend(search(version, side, terms, keywords, additional_path + file + "/", output_path, actually_copy_files, suppress_clear, allow_decompile))
        elif os.path.isfile(file_path):
            if is_in(file_path, terms, keywords):
                output.append(additional_path + file)
                if actually_copy_files:
                    copy_path = "./_search" + output_path + cut_path
                    os.makedirs(os.path.split(copy_path)[0], exist_ok=True)
                    shutil.copy(file_path, copy_path)
    output2:list[str] = [path[1:] if path.startswith("/") else path for path in output] # prevent absolute paths starting with "/"
    return output2
        
def get_keywords(terms:list[str]) -> tuple[list[str], list[str]]:
    '''Returns the output terms and output keywords in two separate lists'''
    POSSIBLE_KEYWORDS = ["and"]
    output_keywords:list[str] = []
    output_terms:list[str] = []
    for term in terms:
        if term in POSSIBLE_KEYWORDS: output_keywords.append(term)
        else: output_terms.append(term)
    return output_terms, output_keywords

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
    search_terms, search_keywords = get_keywords(search_terms)
    paths = search(chosen_version, "client", search_terms, search_keywords, actually_copy_files=True)
    print("Found %s file(s)!" % len(paths))

if __name__ == "__main__":
    main()
