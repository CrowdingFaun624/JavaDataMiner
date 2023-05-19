import json
import os
import shutil
import zipfile

import Importer.AssetImporter as AssetImporter
import Importer.AssetsIndex as AssetsIndex
import Importer.Decompiler as Decompiler
import Importer.JarImporter as JarImporter
import Importer.JarRemapper as JarRemapper
import Importer.Manifest as Manifest
import Importer.MappingsEncoder as MappingsEncoder
import Importer.MappingsImporter as MappingsImporter
import Utilities.MappingCondenser as MappingsCondenser
import Importer.VersionJson as VersionJson
import Importer.WebRequest as WebRequest
import Utilities.Searcher as Searcher

def test_WebRequest() -> None:
    json_test:dict[str,dict|list] = WebRequest.web_request("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json", "j")
    assert isinstance(json_test, dict)
    assert list(json_test.keys()) == ["latest", "versions"]
    assert list(json_test["latest"].keys()) == ["release", "snapshot"]
    with open("./Tests/binary.ico", "rb") as f:
        BYTES_BYTES = f.read()
    binary_test:bytes = WebRequest.web_request("https://file-examples.com/storage/feb401d325641db2fa1dfe7/2017/10/file_example_favicon.ico", "b")
    assert isinstance(binary_test, bytes)
    assert binary_test == BYTES_BYTES
    with open("./Tests/text.txt", "rt") as f:
        TEXT_TEXT = f.read()
    text_test:str = WebRequest.web_request("https://filesamples.com/samples/document/txt/sample1.txt", "t")
    assert isinstance(text_test, str)
    assert text_test == TEXT_TEXT

def test_Manifest() -> None:
    fetch_test = Manifest.fetch_manifest(store=True)
    assert isinstance(fetch_test, dict)
    assert list(fetch_test.keys()) == ["latest", "versions"]
    assert list(fetch_test["latest"].keys()) == ["release", "snapshot"]
    assert isinstance(fetch_test["versions"], list)
    release:str = fetch_test["latest"]["release"]
    snapshot:str = fetch_test["latest"]["snapshot"]
    found_release, found_snapshot = False, False
    for version in fetch_test["versions"]:
        assert set(list(version.keys())) == set(["id", "type", "url", "time", "releaseTime", "sha1", "complianceLevel"])
        for key in ["id", "type", "url", "time", "releaseTime", "sha1"]: assert isinstance(version[key], str)
        assert isinstance(version["complianceLevel"], int)
        assert version["complianceLevel"] in [0, 1]
        if version["id"] == release: found_release = True
        elif version["id"] == snapshot: found_snapshot = True
    if not (found_release and found_snapshot): raise KeyError("Versions %s and %s were not found in version manifest!" % (release, snapshot))
    assert os.path.exists("./_versions/version_manifest.json")
    with open("./_versions/version_manifest.json", "rt") as f:
        store_test = json.loads(f.read())
    assert store_test == fetch_test
    def test_get_version(version_name:str=None, version_properties:dict[str,str|int]=None) -> None:
        '''Tests Manifest.get_version'''
        if version_properties is None:
            version_properties:dict[str,str|int] = Manifest.get_version(version_name, fetch_test)
        elif version_name is None:
            version_name = version_properties["id"]
        assert isinstance(version_properties, dict)
        assert set(list(version_properties.keys())) == set(["id", "type", "url", "time", "releaseTime", "sha1", "complianceLevel"])
        for key in ["id", "type", "url", "time", "releaseTime", "sha1"]: assert isinstance(version_properties[key], str)
        assert isinstance(version_properties["complianceLevel"], int)

    for version in ["23w12a", "1.19.3", "1.8.1", "14w33b", "1.7.6-pre2", "a1.2.1", "c0.30_01c", "rd-132211"]:
        test_get_version(version)
    random_version = Manifest.get_random_version(fetch_test)
    test_get_version(version_properties=random_version)
    assert Manifest.get_version_id("rd-132211") == 0
    assert Manifest.get_version_id("a1.1.2_01") == 20
    latest = Manifest.get_latest()
    assert isinstance(latest, tuple)
    assert len(latest) == 2
    for latest_thing in latest: assert isinstance(latest_thing, str); assert len(latest_thing) > 0
    assert Manifest.get_id_version(0) == "rd-132211"
    assert Manifest.get_id_version(20) == "a1.1.2_01"

def test_VersionJson() -> None:
    VERSION = "1.19.3"
    def run_test() -> dict:
        fetch_test = VersionJson.fetch_version_json(VERSION, store=True)
        assert os.path.exists("./_versions/%s/version.json" % VERSION)
        with open("./_versions/%s/version.json" % VERSION, "rt") as f:
            store_test:dict = json.loads(f.read())
        assert store_test == fetch_test
        return fetch_test
    run_test()
    os.remove("./_versions/version_manifest.json")
    fetch_test = run_test()
    get_test = VersionJson.get_version_json(VERSION)
    assert fetch_test == get_test
    os.remove("./_versions/%s/version.json" % VERSION)
    get_test = VersionJson.get_version_json(VERSION)
    assert fetch_test == get_test
    assert VersionJson.get_asset_index(VERSION) == "2"

def verify_jar(path:str) -> None:
    '''Asserts that a jar exists, is valid, is not empty, and contains class files'''
    assert path.endswith(".jar")
    assert os.path.exists(path)
    jar_path = path
    zip_path = path[:-4] + ".zip"
    os.rename(jar_path, zip_path)
    with zipfile.ZipFile(zip_path) as zip_file:
        assert len(zip_file.namelist()) > 0
    os.rename(zip_path, jar_path)

def test_JarImporter() -> None:
    VERSION = "1.19.3"
    if os.path.exists("./_versions/%s/client.jar" % VERSION): os.remove("./_versions/%s/client.jar" % VERSION)
    if os.path.exists("./_versions/%s/server.jar" % VERSION): os.remove("./_versions/%s/server.jar" % VERSION)
    if os.path.exists("./_versions/%s/client.zip" % VERSION): os.remove("./_versions/%s/client.zip" % VERSION)
    if os.path.exists("./_versions/%s/server.zip" % VERSION): os.remove("./_versions/%s/server.zip" % VERSION)
    if os.path.exists("./_versions/%s/client_unzipped" % VERSION): shutil.rmtree("./_versions/%s/client_unzipped" % VERSION)
    if os.path.exists("./_versions/%s/server_unzipped" % VERSION): shutil.rmtree("./_versions/%s/server_unzipped" % VERSION)
    JarImporter.fetch_client(VERSION)
    JarImporter.fetch_server(VERSION)
    JarImporter.fetch_unzipped(VERSION, "client")
    JarImporter.fetch_unzipped(VERSION, "server")
    verify_jar("./_versions/%s/client.jar" % VERSION)
    verify_jar("./_versions/%s/server.jar" % VERSION)
    assert os.path.exists("./_versions/%s/client_unzipped" % VERSION)
    assert os.path.exists("./_versions/%s/server_unzipped" % VERSION)

def test_MappingsImporter() -> None:
    VERSION = "1.19.3"
    if os.path.exists("./_versions/%s/client.txt" % VERSION): os.remove("./versions/%s/client.txt" % VERSION)
    if os.path.exists("./_versions/%s/server.txt" % VERSION): os.remove("./versions/%s/server.txt" % VERSION)
    client_mappings = MappingsImporter.fetch_client(VERSION)
    server_mappings = MappingsImporter.fetch_server(VERSION)
    assert os.path.exists("./_versions/%s/client.txt" % VERSION)
    assert os.path.exists("./_versions/%s/server.txt" % VERSION)
    assert isinstance(client_mappings, str)
    assert isinstance(server_mappings, str)
    assert len(client_mappings) > 0
    assert len(server_mappings) > 0
    with open("./Tests/mappings_start.txt", "rt") as f: MAPPINGS_START = f.read()
    assert client_mappings.startswith(MAPPINGS_START)
    assert server_mappings.startswith(MAPPINGS_START)
    with open("./_versions/%s/client.txt" % VERSION, "rt") as f: client_stored = f.read()
    with open("./_versions/%s/server.txt" % VERSION, "rt") as f: server_stored = f.read()
    assert client_mappings == client_stored
    assert server_mappings == server_stored

def test_MappingsEncoder() -> None:
    VERSION = "1.19.3"
    if os.path.exists("./_versions/%s/client.tsrg" % VERSION): os.remove("./_versions/%s/client.tsrg" % VERSION)
    if os.path.exists("./_versions/%s/server.tsrg" % VERSION): os.remove("./_versions/%s/server.tsrg" % VERSION)
    if os.path.exists("./_versions/%s/server.txt" % VERSION):  os.remove("./_versions/%s/server.txt" % VERSION) # remove just the server for testing of both
    MappingsEncoder.create_client_mappings(VERSION)
    MappingsEncoder.create_server_mappings(VERSION)
    assert os.path.exists("./_versions/%s/client.tsrg" % VERSION)
    assert os.path.exists("./_versions/%s/server.tsrg" % VERSION)
    with open("./_versions/%s/client.tsrg" % VERSION, "rt") as f: client_mappings = f.read()
    with open("./_versions/%s/server.tsrg" % VERSION, "rt") as f: server_mappings = f.read()
    assert len(client_mappings) > 0
    assert len(server_mappings) > 0

def test_JarRemapper() -> None:
    VERSION = "1.19.3"
    JarRemapper.remap_client(VERSION)
    JarRemapper.remap_server(VERSION)
    verify_jar("./_versions/%s/client_remapped.jar" % VERSION)
    verify_jar("./_versions/%s/server_remapped.jar" % VERSION)

def get_file_tree(path:str, additional_path:str="/") -> list[str]:
    '''Returns a list of paths that make up a directory, starting from the given path'''
    assert os.path.exists(path)
    assert os.path.isdir(path)
    file_list = os.listdir(path + additional_path)
    output = []
    for file in file_list:
        if os.path.isfile(path + additional_path + file):
            output.append(additional_path + file)
        elif os.path.isdir(path + additional_path + file):
            output.extend(get_file_tree(path, additional_path + file + "/"))
    return output

def test_Decompiler() -> None:
    VERSION = "1.19.3"
    if os.path.exists("./_versions/%s/client_decompiled" % VERSION): shutil.rmtree("./_versions/%s/client_decompiled" % VERSION)
    if os.path.exists("./_versions/%s/server_decompiled" % VERSION): shutil.rmtree("./_versions/%s/server_decompiled" % VERSION)
    print("\tDecompiling client...")
    Decompiler.decompile_client(VERSION)
    print("\tDecompiling server...")
    Decompiler.decompile_server(VERSION)
    client_tree = get_file_tree("./_versions/%s/client_decompiled" % VERSION)
    server_tree = get_file_tree("./_versions/%s/server_decompiled" % VERSION)
    for client_file in client_tree: assert client_file.endswith(".java")
    for server_file in server_tree: assert server_file.endswith(".java")

def test_AssetsIndex() -> None:
    VERSION = "1.19.3"
    fetch_test = AssetsIndex.fetch_assets_index(VERSION)
    assert isinstance(fetch_test, dict)
    assert list(fetch_test.keys()) == ["objects"]
    for key, value in list(fetch_test["objects"].items()):
        assert isinstance(key, str)
        assert isinstance(value, dict)
        assert list(value.keys()) == ["hash", "size"]
        assert isinstance(value["hash"], str)
        assert isinstance(value["size"], int)
        assert len(value["hash"]) == 40
        for character in value["hash"]: assert character in "0123456789abcdef"
        assert value["size"] > 0
    with open("./_assets/indexes/2.json", "rt") as f:
        store_test = json.loads(f.read())
    assert store_test == fetch_test
    get_test = AssetsIndex.get_assets_index("2", VERSION)
    assert get_test == fetch_test

def test_AssetImporter() -> None:
    VERSION = "1.19.3"
    if os.path.exists("./_versions/%s/assets" % VERSION):
        shutil.rmtree("./_versions/%s/assets" % VERSION)
    if os.path.exists("./_assets/objects/50/508bb207d3fa3013a84638b2c8a8c29f5ba401df"):
        os.remove("./_assets/objects/50/508bb207d3fa3013a84638b2c8a8c29f5ba401df") # sounds.json
    if os.path.exists("./_versions/%s/assets/minecraft/sounds.json" % VERSION):
        os.remove("./_versions/%s/assets/minecraft/sounds.json" % VERSION)
    assert AssetImporter.get_hash("2", "minecraft/sounds.json") == "508bb207d3fa3013a84638b2c8a8c29f5ba401df"
    fetch_test = AssetImporter.fetch_asset("2", "minecraft/sounds.json", "j", VERSION, store=True, store_in_version=True)
    assert isinstance(fetch_test, dict)
    object_test = AssetImporter.get_asset("2", "minecraft/sounds.json", "j")
    assert object_test == fetch_test
    version_test = AssetImporter.get_asset_version(VERSION, "minecraft/sounds.json", "j")
    assert version_test == fetch_test
    with open("./Tests/2-sounds.json", "rt") as f:
        test_test = json.loads(f.read())
    assert test_test == fetch_test

def test_Searcher() -> None:
    def assert_path(path:str, files:list[str]) -> None:
        '''Asserts that the given path contains the correct stuff.'''
        assert os.listdir("./_search" + path) == files
    searcher_results = Searcher.search("1.19.3", "client", ["Sheep"], [], output_path="1.19.3")
    assert_path("", ["1.19.3"])
    assert_path("/1.19.3", ["net"])
    assert_path("/1.19.3/net", ["minecraft"])
    assert_path("/1.19.3/net/minecraft", ["client", "data", "util", "world"])
    assert_path("/1.19.3/net/minecraft/client", ["model", "renderer"])
    assert_path("/1.19.3/net/minecraft/client/model", ["geom", "SheepFurModel.java", "SheepModel.java"])
    assert_path("/1.19.3/net/minecraft/client/model/geom", ["LayerDefinitions.java"])
    assert_path("/1.19.3/net/minecraft/client/renderer", ["entity"])
    assert_path("/1.19.3/net/minecraft/client/renderer/entity", ["EntityRenderers.java", "layers", "SheepRenderer.java"])
    assert_path("/1.19.3/net/minecraft/client/renderer/entity/layers", ["SheepFurLayer.java"])
    assert_path("/1.19.3/net/minecraft/data", ["advancements", "loot", "worldgen"])
    assert_path("/1.19.3/net/minecraft/data/advancements", ["packs"])
    assert_path("/1.19.3/net/minecraft/data/advancements/packs", ["VanillaHusbandryAdvancements.java"])
    assert_path("/1.19.3/net/minecraft/data/loot", ["EntityLootSubProvider.java", "packs"])
    assert_path("/1.19.3/net/minecraft/data/loot/packs", ["VanillaEntityLoot.java"])
    assert_path("/1.19.3/net/minecraft/data/worldgen", ["biome", "BiomeDefaultFeatures.java"])
    assert_path("/1.19.3/net/minecraft/data/worldgen/biome", ["OverworldBiomes.java"])
    assert_path("/1.19.3/net/minecraft/util", ["datafix"])
    assert_path("/1.19.3/net/minecraft/util/datafix", ["fixes", "schemas"])
    assert_path("/1.19.3/net/minecraft/util/datafix/fixes", ["EntityHealthFix.java", "EntityIdFix.java", "ItemSpawnEggFix.java", "StatsCounterFix.java"])
    assert_path("/1.19.3/net/minecraft/util/datafix/schemas", ["V100.java", "V99.java"])
    assert_path("/1.19.3/net/minecraft/world", ["entity", "item"])
    assert_path("/1.19.3/net/minecraft/world/entity", ["ai", "animal", "EntityType.java", "monster", "SpawnPlacements.java"])
    assert_path("/1.19.3/net/minecraft/world/entity/ai", ["attributes"])
    assert_path("/1.19.3/net/minecraft/world/entity/ai/attributes", ["DefaultAttributes.java"])
    assert_path("/1.19.3/net/minecraft/world/entity/animal", ["Sheep.java", "Wolf.java"])
    assert_path("/1.19.3/net/minecraft/world/entity/monster", ["Evoker.java"])
    assert_path("/1.19.3/net/minecraft/world/item", ["DyeItem.java", "Items.java"])
    assert searcher_results == ['/net/minecraft/client/model/geom/LayerDefinitions.java', '/net/minecraft/client/model/SheepFurModel.java',
                               '/net/minecraft/client/model/SheepModel.java', '/net/minecraft/client/renderer/entity/EntityRenderers.java',
                               '/net/minecraft/client/renderer/entity/layers/SheepFurLayer.java', '/net/minecraft/client/renderer/entity/SheepRenderer.java',
                               '/net/minecraft/data/advancements/packs/VanillaHusbandryAdvancements.java', '/net/minecraft/data/loot/EntityLootSubProvider.java',
                               '/net/minecraft/data/loot/packs/VanillaEntityLoot.java', '/net/minecraft/data/worldgen/biome/OverworldBiomes.java',
                               '/net/minecraft/data/worldgen/BiomeDefaultFeatures.java', '/net/minecraft/util/datafix/fixes/EntityHealthFix.java',
                               '/net/minecraft/util/datafix/fixes/EntityIdFix.java', '/net/minecraft/util/datafix/fixes/ItemSpawnEggFix.java',
                               '/net/minecraft/util/datafix/fixes/StatsCounterFix.java', '/net/minecraft/util/datafix/schemas/V100.java',
                               '/net/minecraft/util/datafix/schemas/V99.java', '/net/minecraft/world/entity/ai/attributes/DefaultAttributes.java',
                               '/net/minecraft/world/entity/animal/Sheep.java', '/net/minecraft/world/entity/animal/Wolf.java',
                               '/net/minecraft/world/entity/EntityType.java', '/net/minecraft/world/entity/monster/Evoker.java',
                               '/net/minecraft/world/entity/SpawnPlacements.java', '/net/minecraft/world/item/DyeItem.java', '/net/minecraft/world/item/Items.java']
    Searcher.clear_search()

def test_MappingsCondenser() -> None:
    fetch_test = MappingsCondenser.fetch_condensed_mappings("1.19.2", "client", store=True)
    assert os.path.exists("./_versions/1.19.2/client_mappings_compressed.txt")
    assert os.path.isfile("./_versions/1.19.2/client_mappings_compressed.txt")
    get_test = MappingsCondenser.get_condensed_mappings("1.19.2", "client")
    assert fetch_test == get_test
    assert len(fetch_test) > 1
    assert len(get_test) > 1

os.chdir(os.path.split(__file__)[0])
# test_WebRequest(); print("WebRequest is good!")
# test_Manifest(); print("Manifest is good!")
# test_VersionJson(); print("VersionJson is good!")
# test_JarImporter(); print("JarImporter is good!")
# test_MappingsImporter(); print("MappingsImporter is good!")
# test_MappingsEncoder(); print("MappingsEncoder is good!")
# test_JarRemapper(); print("JarRemapper is good!")
test_Decompiler(); print("Decompiler is good!")
test_AssetsIndex(); print("AssetsIndex is good!")
test_AssetImporter(); print("AssetImporter is good!")
test_Searcher(); print("Searcher is good!")
test_MappingsCondenser(); print("MappingsCondenser is good!")
