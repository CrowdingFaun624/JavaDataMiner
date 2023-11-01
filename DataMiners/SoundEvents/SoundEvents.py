import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner
import DataMiners.NoneDataMiner as NoneDataMiner

import DataMiners.SoundEvents.SoundEventsNew as SoundEventsNew
import DataMiners.SoundEvents.SoundEvents1 as SoundEvents1
import DataMiners.SoundEvents.SoundEvents2 as SoundEvents2
import DataMiners.SoundEvents.SoundEvents3 as SoundEvents3
import DataMiners.SoundEvents.SoundEvents4 as SoundEvents4 # MCL-2991 - sounds.json was removed in versions before 13w24a (13w23b and below), resulting in this nightmare

MANUAL_ADDITIONS_0 = ["step.grass", "step.gravel", "step.stone", "step.wood"] # extremely trivial sound events that I did not bother to make a dataminer for.
MANUAL_ADDITIONS_1 = ["mob.ghast.affectionate_scream"] # unused sound event.
MANUAL_ADDITIONS_2 = ["mob.ghast.affectionate_scream", "fireworks.blast", "fireworks.blast_far", "fireworks.largeBlast", "fireworks.largeBlast_far"] # firework sounds use concatenation; thus, they are not caught.
MANUAL_ADDITIONS_3 = ["mob.ghast.affectionate_scream", "fireworks.blast", "fireworks.blast_far", "fireworks.largeBlast", "fireworks.largeBlast_far", "mob.slime.big", "mob.slime.small"] # firework sounds use concatenation; thus, they are not caught.
MANUAL_ADDITIONS_4 = ["mob.ghast.affectionate_scream", "fireworks.blast", "fireworks.blast_far", "fireworks.largeBlast", "fireworks.largeBlast_far", "fireworks.twinkle", "fireworks.twinkle_far", "mob.slime.big", "mob.slime.small"]
MANUAL_ADDITIONS_5 = ["mob.ghast.affectionate_scream", "fireworks.blast", "fireworks.blast_far", "fireworks.largeBlast", "fireworks.largeBlast_far", "fireworks.twinkle", "fireworks.twinkle_far", "mob.slime.big", "mob.slime.small", "gui.button.press"]

dataminers:list[DataMiner.DataMiner] = [
    SoundEventsNew.SoundEventsNew("19w36a", "-"),
    SoundEvents1.SoundEvents1("1.14_combat-0", "19w35a"),
    SoundEventsNew.SoundEventsNew("1.14.4", "1.14.4"),
    SoundEvents1.SoundEvents1("18w43a", "1.14.4-pre7"),
    SoundEvents2.SoundEvents2("15w49b", "1.13.2"),
    SoundEvents3.SoundEvents3("1.8.9", "1.8.9"),
    SoundEvents2.SoundEvents2("15w43a", "15w49a"),
    SoundEvents3.SoundEvents3("14w25a", "15w42a", sounds_json_name="minecraft/sounds.json"),
    SoundEvents3.SoundEvents3("14w20a", "14w21b", sounds_json_name="sounds.json"),
    SoundEvents3.SoundEvents3("1.7.10-pre4", "1.7.10", sounds_json_name="minecraft/sounds.json"), # idk why it keeps switching
    SoundEvents3.SoundEvents3("13w49a", "1.7.10-pre3", sounds_json_name="sounds.json"),
    SoundEvents4.SoundEvents4("13w42a", "13w48b", records="records.ogg", manual_additions=MANUAL_ADDITIONS_5), # this is done at this time period due to assets "legacy.json" being inaccurate.
    SoundEvents4.SoundEvents4("13w24a", "13w41b", records="records.ogg", manual_additions=MANUAL_ADDITIONS_5), # this is done at this time period due to assets "legacy.json" being inaccurate.
    SoundEvents4.SoundEvents4("12w50a", "13w23b", records="streaming.mus", manual_additions=MANUAL_ADDITIONS_4), # sounds become chaotic evil instead of just neutral evil (no sounds.json at all)
    SoundEvents4.SoundEvents4("12w49a", "12w49a", records="streaming.mus", manual_additions=MANUAL_ADDITIONS_3),
    SoundEvents4.SoundEvents4("12w39a", "1.4.5", records="streaming.mus", manual_additions=MANUAL_ADDITIONS_1),
    SoundEvents4.SoundEvents4("12w38a", "12w38b", records="streaming.mus", sound_type_keys=["dig", "step"], manual_additions=MANUAL_ADDITIONS_1),
    SoundEvents4.SoundEvents4("1.0", "12w37a", records="streaming.mus", sound_type_keys=["dig", "step"], manual_additions=MANUAL_ADDITIONS_1),
    SoundEvents4.SoundEvents4("a1.2.0", "1.0.0-rc2-3", records="streaming.mus", sound_type_keys=["dig", "step"], grab_assets=False, manual_additions=MANUAL_ADDITIONS_1),
    SoundEvents4.SoundEvents4("in-20100105", "a1.1.2_01", records="streaming.mus", sound_type_keys=["dig", "step"], grab_assets=False),
    NoneDataMiner.NoneDataMiner("in-20091223-1", "in-20091231-2"), # sounds were removed during this time.
    NoneDataMiner.NoneDataMiner("c0.0.22a", "c0.30_01c", return_value=MANUAL_ADDITIONS_0),
    NoneDataMiner.NoneDataMiner("-", "c0.0.21a_01"), # sounds not yet added
]

SoundEvents = DataMinerType.DataMinerType("sound_events.json", dataminers)
