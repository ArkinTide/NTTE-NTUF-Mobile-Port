"""Preserve weather music across the native generated-room music boundary."""
from apply_release210_repairs import ROOT, PROJECT, change
from install_native205 import apply as install


def main():
    files=list(PROJECT.glob('scripts/frCode_Frontier_Events_mod_*/*.gml'))
    assert len(files)==1
    # Exactly the authored weather-local EventMusic variable, excluding boss
    # controllers, source cleanup calls, Casino's ambient loops and ordinary
    # game/area music. The upstream source is retained in original/Frontier.
    for token in ['_fr.vars._EventMusic','_frl__EventMusic']:
        text=files[0].read_text('utf-8-sig')
        old='scrFRSoundMusic('+token+');'
        new='scrFRWeatherMusic210('+token+');'
        if old in text: change(files[0],old,new,count=text.count(old))
        text=files[0].read_text('utf-8-sig')
        old='if ((! audio_is_playing('+token+'))) {'
        new='if (true) { // FRONTIER210 RECORD EVEN AN ALREADY PLAYING WEATHER TRACK'
        if old in text: change(files[0],old,new,count=text.count(old))
    path=PROJECT/'objects/MusCont/Alarm_11.gml'
    change(path,'if(scrNTTEFullMusicArea()) exit;',
           'if(scrNTTEFullMusicArea()) {scrFRWeatherMusic210Apply();exit;} // FRONTIER210 WEATHER MUSIC')
    change(path,'\toldarea = _area\n}',
           '\toldarea = _area\n}\nscrFRWeatherMusic210Apply(); // FRONTIER210 WEATHER AFTER NATIVE THEME')
    path=PROJECT/'objects/GenCont/Create_0.gml'
    text=path.read_text('utf-8-sig')
    marker='if(instance_exists(GameCont)) GameCont.fr_weather_music210=undefined; // FRONTIER210 ROOM MUSIC RESET\n'
    if marker not in text: path.write_text(marker+text,encoding='utf8')
    install(PROJECT,{'weather_music210.gml':'scrFrontier_weather_music210'})


if __name__=='__main__': main()
