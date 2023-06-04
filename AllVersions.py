import os
import shutil
import threading
import time
import traceback

import DataMiners.DataMiners as DataMiners
import Importer.Manifest as Manifest
import Utilities.Cleaner as Cleaner
import Utilities.DecompileZipper as DecompileZipper

def get_version_collections(manifest:list[dict[str,str|int]], group_size:int=8) -> list[list[str]]:
    '''From the manifest, creates a list of list of eight version names.'''
    version_list:list[str] = [version["id"] for version in manifest]
    output:list[list[str]] = []
    group:list[str] = []
    for version in version_list:
        group.append(version)
        if len(group) >= group_size:
            output.append(group)
            group = []
    return output

def terminate_version(version:str) -> None:
    # print("Please remove version %s; it must be reevaluated." % version)
    data_path = os.path.join("./_versions", version, "data")
    if os.path.exists(data_path):
        shutil.rmtree(data_path)

def do_version(version:str, exception_holder:dict[str,any]) -> None:
    try:
        if not os.path.exists(os.path.join("./_versions", version, "data")):
            print("\t" + version)
            DataMiners.run_all(version, error_on_none=False)
        else:
            print(version)
        DecompileZipper.zip_decompiled_client(version, does_not_exist_error=False)
        Cleaner.clear_unzipped([version])
    except KeyboardInterrupt: # doesn't actually occur lol
        terminate_version(version)
        exception_holder[version] = "KeyboardInterrupt"
    except BaseException as e:
        print("%s HAD AN EXCEPTION" % version)
        terminate_version(version)
        exception_holder[version] = e

def main() -> None:
    Cleaner.clear_incomplete_decompiles()
    versions_properties = Manifest.get_manifest()["versions"]
    CONCURRENT_COUNT = 4
    # version_groups = get_version_collections(versions, CONCURRENT_COUNT)
    versions = [version["id"] for version in versions_properties]
    active_threads:dict[str,threading.Thread] = {}
    exception_holder:dict[str,any] = {}
    stop_creating_threads = False
    index = 0
    keyboard_interruptions = 0
    while True:
        version = versions[index] # do this so it never skips any
        if not stop_creating_threads and len(active_threads) < CONCURRENT_COUNT:
            # thread creator
            time.sleep(0.125)
            new_thread = threading.Thread(target=do_version, args=(version, exception_holder))
            exception_holder[version] = None # default, empty error message
            new_thread.start()
            active_threads[version] = new_thread
            index += 1
        else:
            # thread ender
            while True:
                try:
                    time.sleep(0.025)
                except KeyboardInterrupt:
                    print("Preparing to exit...")
                    keyboard_interruptions += 1
                    stop_creating_threads = True
                    if keyboard_interruptions >= 2: os._exit(0)
                thread_finished = False
                threads_finished:list[str] = []
                for thread_name, active_thread in list(active_threads.items()):
                    if not active_thread.is_alive():
                        del active_threads[thread_name]
                        threads_finished.append(thread_name)
                        thread_finished = True
                if thread_finished:
                    for thread_name in threads_finished:
                        if exception_holder[thread_name] is not None:
                            stop_creating_threads = True
                            print(thread_name)
                            traceback.print_exception(exception_holder[thread_name])
                    break
        if stop_creating_threads and len(active_threads) == 0: break
    print("Finished datamining; cleaning up...")
    Cleaner.clear_mappings()
    Cleaner.clear_mappings_tsrg()
    Cleaner.clear_incomplete_decompiles()
    Cleaner.clear_unzipped()

if __name__ == "__main__":
    main()
