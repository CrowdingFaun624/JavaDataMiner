# import DataMiners.DataMiners as DataMiners

import os

import Importer.Decompiler as Decompiler
import Importer.Manifest as Manifest
import Utilities.AssetsStorage as AssetsStorage
import Utilities.Installer as Installer
import Utilities.Searcher as Searcher

Manifest.fetch_manifest(store=True)

version = Manifest.get_latest()[1] # latest snapshot
print("Extracting version \"%s\"" % version)
Manifest.add_latest_to_version_order(version)
Manifest.fetch_manifest(store=True)

import DataMiners.DataMiners as DataMiners # must be done after version fnoodling so it doesn't explode
import Utilities.LanguageKeyGenerator as LanguageKeyGenerator
import Utilities.SoundsJsonTablifier as SoundsJsonTablifier

Installer.install(version, True)

Decompiler.get_decompiled_client(version)

if not os.path.exists("./_versions/%s/data" % version):
    DataMiners.run_all(version)
if not os.path.exists("./_versions/%s/data" % version):
    print("Dataminers failed to activate.")

search_versions = [version, Manifest.get_id_version(Manifest.get_version_id(version)-1)]

# print(search_versions)
Searcher.clear_search()
for search_version in search_versions:
    Searcher.search(search_version, "client", ["sound", "Sound", "SOUND"], output_path=search_version, suppress_clear=True, actually_copy_files=True)

if not os.path.exists("./_assets_storage/%s" % version):
    AssetsStorage.reconstruct(version)

SoundsJsonTablifier.main()# TODO: Add zip functionality to asset archival
LanguageKeyGenerator.main()

if not os.path.exists("./_versions/%s/data" % version):
    print("Dataminers failed to activate.")
