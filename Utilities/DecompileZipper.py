import os
import shutil

def zip_decompiled(version:str, side:str, does_not_exist_error:bool=True, decompile_on_error:bool=False) -> None:
    if side not in ("client", "server"):
        raise ValueError("%s is not a valid client or server value!" % side)
    if not os.path.exists(os.path.join("./_versions", version)):
        raise FileNotFoundError("Version \"%s\" does not exist!" % version)
    if does_not_exist_error and not os.path.exists(os.path.join("./_versions", version, "%s_decompiled" % side)):
        raise FileNotFoundError("Version \"%s\"'s %s does not exist!" % (version, side))
    if os.path.exists(os.path.join("./_versions", version, "%s_decompiled.zip" % side)): return
    folder_path = os.path.join("./_versions", version, "%s_decompiled" % side)
    dest_path = os.path.join("./_versions", version, "%s_decompiled" % side)
    shutil.make_archive(dest_path, "zip", root_dir=folder_path)
    shutil.rmtree(folder_path)

def zip_decompiled_client(version:str, does_not_exist_error:bool=True) -> None:
    zip_decompiled(version, "client", does_not_exist_error)

def zip_decompiled_server(version:str, does_not_exist_error:bool=True) -> None:
    zip_decompiled(version, "server", does_not_exist_error)

def main() -> None:
    def user_input() -> tuple[str,str]:
        '''Returns the version and side'''
        all_versions = os.listdir("./_versions")
        client_versions = [version for version in all_versions if os.path.exists(os.path.join("./_versions", version, "client_decompiled"))]
        server_versions = [version for version in all_versions if os.path.exists(os.path.join("./_versions", version, "server_decompiled"))]
        user_input = None
        while True:
            user_input = input("Use \"client\" or \"server\"? ")
            if user_input in ("client", "server"): break
        selected_side = user_input
        side_versions = client_versions if selected_side == "client" else server_versions
        user_input = None
        while True:
            user_input = input("Use what version? ")
            if user_input in side_versions: break
            else:
                if user_input in all_versions: print("Version \"%s\" does not have a decompiled client." % user_input)
        selected_version = user_input
        return selected_version, selected_side
    version, side = user_input()
    zip_decompiled(version, side)
