import DataMiners.DataMinerType as DataMinerType
import DataMiners.DataMiner as DataMiner

import DataMiners.SoundEvents.SoundEventsNew as SoundEventsNew
import DataMiners.SoundEvents.SoundEvents1 as SoundEvents1
import DataMiners.SoundEvents.SoundEvents2 as SoundEvents2
import DataMiners.SoundEvents.SoundEvents3 as SoundEvents3
import DataMiners.SoundEvents.SoundEvents4 as SoundEvents4 # MCL-2991 - sounds.json was removed in versions before 13w24a (13w23b and below), resulting in this nightmare

dataminers:list[DataMiner.DataMiner] = [
    SoundEventsNew.SoundEventsNew("19w36a", "-"),
    SoundEvents1.SoundEvents1("19w34a", "19w35a"),
    SoundEventsNew.SoundEventsNew("1.14.4", "1.14.4"),
    SoundEvents1.SoundEvents1("18w43a", "1.14.4-pre7"),
    SoundEvents2.SoundEvents2("15w49b", "1.13.2"),
    SoundEvents3.SoundEvents3("1.8.9", "1.8.9"),
    SoundEvents2.SoundEvents2("15w43a", "15w49a"),
    SoundEvents3.SoundEvents3("14w25a", "15w42a", sounds_json_name="minecraft/sounds.json"),
    SoundEvents3.SoundEvents3("14w20a", "14w21b", sounds_json_name="sounds.json"),
    SoundEvents3.SoundEvents3("1.7.10-pre4", "1.7.10", sounds_json_name="minecraft/sounds.json"), # idk why it keeps switching
    SoundEvents3.SoundEvents3("13w49a", "1.7.10-pre3", sounds_json_name="sounds.json"),
    SoundEvents4.SoundEvents4("13w24a", "13w48b", records="records.ogg"), # this is done at this time period due to assets "legacy.json" being inaccurate.
    SoundEvents4.SoundEvents4("12w39a", "13w23b", records="streaming.mus"), # sounds become chaotic evil instead of just neutral evil (no sounds.json at all)
    SoundEvents4.SoundEvents4("1.0", "12w38b", records="streaming.mus", sound_type_keys=["dig", "step"]),
    SoundEvents4.SoundEvents4("-", "1.0.0-rc2-3", records="streaming.mus", sound_type_keys=["dig", "step"], grab_assets=False),
]

SoundEvents = DataMinerType.DataMinerType("sound_events.json", dataminers)
