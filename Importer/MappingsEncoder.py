'''Creates .tsrg files from the .txt mapping files'''

import os

import Importer.MappingsImporter as MappingsImporter

def remap_file_path(path:str) -> str:
    remap_primitives = {"int": "I", "double": "D","boolean": "Z", "float": "F", "long": "J", "byte": "B", "short": "S", "char": "C", "void": "V"}
    return "L" + "/".join(path.split(".")) + ";" if path not in remap_primitives else remap_primitives[path]

def remove_brackets(line:str, counter:int) -> tuple[str, int]:
    while '[]' in line:  # get rid of the array brackets while counting them
        counter += 1
        line = line[:-2]
    return line, counter

def convert_mappings(version:str, side:str) -> None: # from MCDecompiler: https://github.com/hube12/DecompilerMC
    '''Creates the converted mappings file. `side` is either "client" or "server"'''
    input_file = MappingsImporter.get(version, side)
    file_name = {}
    for line in input_file.split("\n"):
        if line.startswith('#'): continue # comment at the top, could be stripped
        if line in ("", "\n"): continue
        deobf_name, obf_name = line.split(' -> ')
        if not line.startswith('    '):
            obf_name = obf_name.split(":")[0]
            file_name[remap_file_path(deobf_name)] = obf_name  # save it to compare to put the Lb

    with open("./_versions/%s/%s.txt" % (version, side), 'r') as input_file, open("./_versions/%s/%s.tsrg" % (version, side), 'w+') as outputFile:
        for line in input_file.readlines():
            if line.startswith('#'): continue # comment at the top, could be stripped
            deobf_name, obf_name = line.split(' -> ')
            if line.startswith('    '):
                obf_name = obf_name.rstrip()  # remove leftover right spaces
                deobf_name = deobf_name.lstrip()  # remove leftover left spaces
                method_type, method_name = deobf_name.split(" ")  # split the `<methodType> <methodName>`
                method_type = method_type.split(":")[
                    -1]  # get rid of the line numbers at the beginning for functions eg: `14:32:void`-> `void`
                if "(" in method_name and ")" in method_name:  # detect a function function
                    variables = method_name.split('(')[-1].split(')')[0]  # get rid of the function name and parenthesis
                    function_name = method_name.split('(')[0]  # get the function name only
                    array_length_type = 0

                    method_type, array_length_type = remove_brackets(method_type, array_length_type)
                    method_type = remap_file_path(
                        method_type)  # remap the dots to / and add the L ; or remap to a primitives character
                    method_type = "L" + file_name[
                        method_type] + ";" if method_type in file_name else method_type  # get the obfuscated name of the class
                    if "." in method_type:  # if the class is already packaged then change the name that the obfuscated gave
                        method_type = "/".join(method_type.split("."))
                    for i in range(array_length_type):  # restore the array brackets upfront
                        if method_type[-1] == ";":
                            method_type = "[" + method_type[:-1] + ";"
                        else:
                            method_type = "[" + method_type

                    if variables != "":  # if there is variables
                        array_length_variables = [0] * len(variables)
                        variables = list(variables.split(","))  # split the variables
                        for i in range(len(variables)):  # remove the array brackets for each variable
                            variables[i], array_length_variables[i] = remove_brackets(variables[i],
                                                                                      array_length_variables[i])
                        variables = [remap_file_path(variable) for variable in
                                     variables]  # remap the dots to / and add the L ; or remap to a primitives character
                        variables = ["L" + file_name[variable] + ";" if variable in file_name else variable for variable
                                     in variables]  # get the obfuscated name of the class
                        variables = ["/".join(variable.split(".")) if "." in variable else variable for variable in
                                     variables]  # if the class is already packaged then change the obfuscated name
                        for i in range(len(variables)):  # restore the array brackets upfront for each variable
                            for j in range(array_length_variables[i]):
                                if variables[i][-1] == ";":
                                    variables[i] = "[" + variables[i][:-1] + ";"
                                else:
                                    variables[i] = "[" + variables[i]
                        variables = "".join(variables)

                    outputFile.write(f'\t{obf_name} ({variables}){method_type} {function_name}\n')
                else:
                    outputFile.write(f'\t{obf_name} {method_name}\n')

            else:
                obf_name = obf_name.split(":")[0]
                outputFile.write(remap_file_path(obf_name)[1:-1] + " " + remap_file_path(deobf_name)[1:-1] + "\n")

def create_client_mappings(version:str) -> None:
    '''Gets the client .tsrg mappings and saves them in a file.'''
    convert_mappings(version, "client")

def create_server_mappings(version:str) -> None:
    '''Gets the server .tsrg mappings and saves them in a file.'''
    convert_mappings(version, "server")

def create_mappings(version:str, side:str) -> None:
    '''Gets the .tsrg mappings from the provided side and saves them in a file'''
    if side == "client": create_client_mappings(version)
    elif side == "server": create_server_mappings(version)
    else: raise ValueError("%s is not a valid side!" % side)

def get_mappings(version:str, side:str) -> str:
    '''Returns the mappings file, creating it if it does not exist'''
    if side not in ("client", "server"): raise ValueError("%s is an invalid side!" % side)
    if not os.path.exists("./_versions/%s/%s.tsrg" % (version, side)):
        create_mappings(version, side)
    with open("./_versions/%s/%s.tsrg" % (version, side), "rt") as f:
        return f.read()
