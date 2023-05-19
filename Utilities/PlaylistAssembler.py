import openal
import threading
import time
import tkinter as tk
from tkinter import ttk
import uuid

import Importer.AssetImporter as AssetImporter
import Importer.AssetsIndex as AssetsIndex
import Importer.Manifest as Manifest
import Importer.VersionJson as VersionJson

TITLES = {
    "11": "11", # no title
    "13": "Thirteen",
    "5": "Five",
    "a_familiar_room": "A Familiar Room",
    "aerie": "Aerie",
    "an_ordinary_day": "An Ordinary Day",
    "ancestry": "Ancestry",
    "axolotl": "Axolotl",
    "blocks": "Blocks",
    "boss": "boss", # no title
    "bromeliad": "Bromeliad",
    "calm1": "Minecraft",
    "calm2": "Clark",
    "calm3": "Sweden",
    "calm4": "Magnetic Circuit",
    "cat": "Cat",
    "chirp": "Chirp",
    "chrysopoeia": "Chrysopoeia",
    "comforting_memories": "Comforting Memories",
    "creative1": "Biome Fest",
    "creative2": "Blind Spots",
    "creative3": "Haunt Muskie",
    "creative4": "Aria Math",
    "creative5": "Dreiton",
    "creative6": "Taswell",
    "credits": "Alpha",
    "crescent_dunes": "Crescent Dunes",
    "dragon_fish": "Dragon Fish",
    "earth": "Earth",
    "echo_in_the_wind": "Echo in the Wind",
    "end": "The End",
    "far": "Far",
    "firebugs": "Firebugs",
    "floating_dream": "Floating Dream",
    "hal1": "Subwoofer Lullaby",
    "hal2": "Living Mice",
    "hal3": "Haggstrom",
    "hal4": "Danny",
    "infinite_amethyst": "Infinite Amethyst",
    "labyrinthine": "Labyrinthine",
    "left_to_bloom": "Left to Bloom",
    "mall": "Mall",
    "mellohi": "Mellohi",
    "menu1": "Mutation",
    "menu2": "Moog City 2",
    "menu3": "Beginning 2",
    "menu4": "Floating Trees",
    "nether1": "Concrete Halls",
    "nether2": "Dead Voxel",
    "nether3": "Warmth",
    "nether4": "Ballad of the Cats",
    "nuance1": "Key",
    "nuance2": "Oxygène",
    "one_more_day": "One More Day",
    "otherside": "otherside", # sic
    "piano1": "Dry Hands",
    "piano2": "Wet Hands",
    "piano3": "Mice on Venus",
    "pigstep": "Pigstep", # in files it is "pigstep"; mono mix
    "relic": "Relic",
    "rubedo": "Rubedo",
    "shuniji": "Shuniji",
    "so_below": "So Below",
    "sprouting": "Sprouting",
    "stal": "Stal",
    "stand_tall": "Stand Tall",
    "strad": "Strad",
    "wait": "Wait",
    "ward": "Ward",
    "wending": "Wending"
}
NONCAPITALIZED_WORDS = ["a", "an", "the", "and", "but", "for", "at", "by", "so", "to", "in", "of", "for"]

AUTHORSHIP = {
    "Aaron Cherof": ["A Familiar Room", "Bromeliad", "Crescent Dunes", "Echo in the Wind", "Relic"],
    "C418": ["11", "Thirteen", "Axolotl", "Blocks", "boss", "Minecraft", "Clark", "Sweden", "Cat", "Chirp", "Biome Fest", "Blind Spots", "Haunt Muskie",
             "Aria Math", "Dreiton", "Taswell", "Alpha", "Dragon Fish", "The End", "Far", "Subwoofer Lullaby", "Living Mice", "Haggstrom", "Danny", "Mall",
             "Mellohi", "Mutation", "Moog City 2", "Beginning 2", "Floating Trees", "Concrete Halls", "Dead Voxel", "Warmth", "Ballad of the Cats", "Key",
             "Oxygène", "Dry Hands", "Wet Hands", "Mice on Venus", "Shuniji", "Stal", "Strad", "Wait", "Ward"],
    "Kumi Tanioka": ["An Ordinary Day", "Comforting Memories", "Floating Dream"],
    "Lena Raine": ["Aerie", "Ancestry", "Chrysopoeia", "Firebugs", "Infinite Amethyst", "Labyrinthine", "Left to Bloom", "One More Day",
                   "otherside", "Pigstep", "Rubedo", "So Below", "Stand Tall", "Wending"],
    "Markus Persson": ["Magnetic Circuit"],
    "Samuel Åberg": ["Five"],
    "Shauny Jang": ["Earth", "Sprouting"]
}

BUTTON_WIDTH = 30
REFRESH_INTERVAL = 0.05
AUTHOR_TITLE = "\"%s\" by %s"

def guess_title(title:str) -> str:
    output = title[:]
    output = output.replace("_", " ")
    words = output.split(" ")
    capitalized_words = []
    for index, word in enumerate(words):
        if word in NONCAPITALIZED_WORDS and index != 0:
            capitalized_words.append(word)
        else: capitalized_words.append(word.capitalize())
    output = " ".join(capitalized_words)
    return output

def get_author(title:str) -> str:
    for author_name, author_songs in list(AUTHORSHIP.items()):
        if title in author_songs: return author_name
    else: print("Unable to find author for \"%s\"." % title); return "Unknown"

def get_title(path_name:str) -> str:
    name = path_name.split("/")[-1].replace(".ogg", "")
    if name not in TITLES:
        print( "Unable to find title for \"%s\"." % name)
        title = guess_title(name)
    else: title = TITLES[name]
    author = get_author(title)
    return title

def find_sound_paths() -> dict[str,str]:
    '''Returns a dictionary of nice music titles and their path in `./_assets/objects/`.'''
    latest_version = Manifest.get_id_version(-1)
    asset_index = VersionJson.get_asset_index(latest_version)
    assets_index = AssetsIndex.fetch_assets_index(latest_version, store=True)

    asset_list = AssetsIndex.get_assets_in_folder("minecraft/sounds/music/", assets_index=assets_index)
    asset_list.extend(AssetsIndex.get_assets_in_folder("minecraft/sounds/records/", assets_index=assets_index))
    # for asset in asset_list: asset = "./_assets/objects/" + asset
    hashes = AssetImporter.get_hashes(asset_index, asset_list)
    additional_files = ["./Assets/calm4.ogg", "./Assets/earth.ogg", "./Assets/sprouting.ogg"]
    AssetImporter.get_assets_from_hash(list(hashes.values()), mode="b", collect=False)
    output = {}
    for path_name, hash in list(hashes.items()):
        title = get_title(path_name)
        first_two_letters = hash[:2]
        output[title] = "./_assets/objects/" + first_two_letters + "/" + hash
    for path_name in additional_files:
        title = get_title(path_name)
        output[title] = path_name
    return output

def get_position(index:int) -> tuple[int,int]:
    return index % 4, index // 4 + 3

def update_loop(sound:openal.SourceStream, playing_song:list[str], sound_id:str, song_playing:tk.StringVar) -> None:
    continue_updating = True
    stopped = False
    is_paused = False
    while continue_updating:
        if sound_id != playing_song[0]: sound.stop(); stopped = True
        if playing_song[2] == "pause" and not is_paused: sound.pause(); is_paused = True
        elif playing_song[2] == "play" and is_paused: sound.play(); is_paused = False
        continue_updating = sound.update()
        if is_paused: continue_updating = True
        time.sleep(REFRESH_INTERVAL)
    if playing_song[2] != "stop" and sound_id == playing_song[0]: song_playing.set(song_playing.get() + " (done)")
    playing_song[3] = False
    playing_song[4]:ttk.Button.configure(state="disabled")
    if not stopped: sound.stop()

def play(path:str, playing_song:list[str], title:str, song_playing:tk.StringVar) -> None:
    '''Open a sound from the file'''
    sound_id = uuid.uuid4()
    playing_song[0] = sound_id
    playing_song[1] = title
    playing_song[2] = "play"
    playing_song[3] = True
    playing_song[4]:ttk.Button.configure(state="enabled")
    playing_song[5]:tk.StringVar.set("Pause")
    song_playing.set(AUTHOR_TITLE % (title, get_author(title)))
    if title is not None: print("Now playing \"%s\"" % title)
    sound = openal.oalStream(path, "ogg")
    sound.play()
    thread = threading.Thread(target=update_loop, args=[sound, playing_song, sound_id, song_playing])
    thread.start()

def get_play_function(sound:str, title:str, playing_song:list[str], song_playing:tk.StringVar):
    return lambda: play(sound, playing_song, title, song_playing)

def stop_all(playing_song:list[str], song_playing:tk.StringVar=None, is_paused:tk.StringVar=None) -> None:
    playing_song[2] = "stop"
    playing_song[3] = False
    playing_song[4]:ttk.Button.configure(state="disabled")
    if song_playing is not None: song_playing.set("")
    if is_paused is not None: is_paused.set("Pause")
    playing_song[0] = uuid.uuid4()

def quit(root:tk.Tk, playing_song:list[str]) -> None:
    stop_all(playing_song)
    time.sleep(REFRESH_INTERVAL*1.01)
    root.destroy()
    openal.oalQuit()

def pause(playing_song:list[str], is_paused:tk.StringVar) -> None:
    '''Pauses or unpauses the sound'''
    if playing_song[2] == "pause":
        playing_song[2] = "play"
        is_paused.set("Pause")
    else:
        playing_song[2] = "pause"
        is_paused.set("Play")

def main() -> None:
    root = tk.Tk("Minecraft Music Player")
    frm = ttk.Frame(root, padding=10)
    root.title("Minecraft Music Player")
    sound_paths = find_sound_paths()
    ASSET_PATH = "./_assets/objects/%s"
    sounds:dict[str,str] = {}
    for title, sound_path in list(sound_paths.items()):
        sounds[title] = sound_path
    song_playing = tk.StringVar()
    song_playing.set("")
    is_paused = tk.StringVar()
    is_paused.set("Pause")
    ttk.Button(frm, text="Quit", command=lambda: quit(root, playing_song), width=BUTTON_WIDTH).grid(column=0, row=1)
    ttk.Button(frm, text="Stop all", command=lambda: stop_all(playing_song, song_playing), width=BUTTON_WIDTH).grid(column=1, row=1)
    pause_button = ttk.Button(frm, textvariable=is_paused, command=lambda: pause(playing_song, is_paused), width=BUTTON_WIDTH)
    pause_button.grid(column=0, row=2, columnspan=2)
    ttk.Label(frm, textvariable=song_playing).grid(column=2, row=1, columnspan=2)
    playing_song = ["", "", "", False, pause_button, is_paused] # [random_id, title, "pause"/"play", song_is_loaded, pause_button]
    frm.grid()
    ttk.Label(frm, text="Minecraft Music Player").grid(column=0, row=0, columnspan=4)
    index = 0
    for title, sound in list(sounds.items()):
        x, y = get_position(index)
        index += 1
        ttk.Button(frm, text=title, command=get_play_function(sound, title, playing_song, song_playing), width=BUTTON_WIDTH).grid(column=x, row=y)
    print("Started program")
    root.mainloop()
    stop_all(playing_song)
    time.sleep(REFRESH_INTERVAL * 1.01)
    openal.oalQuit()

# TODO: thing that shows length of song
# TODO: volume slider

if __name__ == "__main__":
    main()