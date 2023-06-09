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

def do_version(version:str, exception_holder:dict[str,any], time_holder:dict[str,any]) -> None:
    try:
        if not DataMiners.has_all_files(version):
            print("\t" + version)
            DataMiners.run_all(version, error_on_none=False, run_if_already_existing=False)
            time_holder[version] = 1
        else:
            print(version)
            time_holder[version] = 0
        DecompileZipper.zip_decompiled_client(version, does_not_exist_error=False)
        Cleaner.clear_unzipped([version])
    except KeyboardInterrupt: # doesn't actually occur lol
        terminate_version(version)
        exception_holder[version] = "KeyboardInterrupt"
        time_holder[version] = 1
    except BaseException as e:
        print("%s HAD AN EXCEPTION" % version)
        terminate_version(version)
        exception_holder[version] = e
        time_holder[version] = 1

def main() -> None:
    def sleep(wait_time:float, keyboard_interruptions:list[int], stop_creating_threads:list[bool]) -> None:
        try:
            time.sleep(wait_time)
        except KeyboardInterrupt:
            print("Preparing to exit...")
            keyboard_interruptions[0] += 1
            stop_creating_threads[0] = True
            if keyboard_interruptions[0] >= 2: os._exit(0)

    Cleaner.clear_incomplete_decompiles()
    versions_properties = Manifest.fetch_manifest(store=True)["versions"]
    CONCURRENT_COUNT = 4
    # version_groups = get_version_collections(versions, CONCURRENT_COUNT)
    versions = [version["id"] for version in versions_properties]
    active_threads:dict[str,threading.Thread] = {}
    exception_holder:dict[str,any] = {}
    time_holder:dict[str,any] = {}
    stop_creating_threads = [False]
    index = 0
    keyboard_interruptions = [0]
    all_short = True
    while True:
        version = versions[index] # do this so it never skips any
        if not stop_creating_threads[0] and len(active_threads) < CONCURRENT_COUNT:
            # thread creator
            next_wait = 0.0025 if all_short else 0.125
            sleep(next_wait, keyboard_interruptions, stop_creating_threads)
            new_thread = threading.Thread(target=do_version, args=(version, exception_holder, time_holder))
            exception_holder[version] = None # default, empty error message
            new_thread.start()
            active_threads[version] = new_thread
            index += 1
        else:
            # thread ender
            while True:
                sleep(0.025, keyboard_interruptions, stop_creating_threads)
                thread_finished = False
                threads_finished:list[str] = []
                for thread_name, active_thread in list(active_threads.items()):
                    if not active_thread.is_alive():
                        del active_threads[thread_name]
                        threads_finished.append(thread_name)
                        thread_finished = True
                if thread_finished:
                    all_short = True
                    for thread_name in threads_finished:
                        if exception_holder[thread_name] is not None:
                            stop_creating_threads[0] = True
                            print(thread_name)
                            traceback.print_exception(exception_holder[thread_name])
                        if time_holder[thread_name] > 0: all_short = False
                    break
        if stop_creating_threads[0] and len(active_threads) == 0: break
    print("Finished datamining; cleaning up...")
    Cleaner.clear_mappings()
    Cleaner.clear_mappings_tsrg()
    Cleaner.clear_incomplete_decompiles()
    Cleaner.clear_unzipped()

if __name__ == "__main__":
    main()
