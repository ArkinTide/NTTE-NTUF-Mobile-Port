// Weather setup precedes native MusCont.Alarm11. Retain its selection for
// this generated room and reapply it after the native area-theme boundary.
// Never run this in ordinary Step: boss music must retain its own priority.
function scrFRWeatherMusic210(_sound,_loop=true) {
    if(instance_exists(GameCont)) GameCont.fr_weather_music210={sound:_sound,loop:_loop,
        area:GameCont.area,subarea:GameCont.subarea,loops:GameCont.loops};
    return scrFRSoundMusic(_sound,_loop);
}
function scrFRWeatherMusic210Apply() {
    if(!scrFREnabled() || !instance_exists(GameCont)) return false;
    var _music=scrNTTEFullValue(GameCont,"fr_weather_music210",undefined);
    if(!is_struct(_music) || _music.area!=GameCont.area
        || _music.subarea!=GameCont.subarea || _music.loops!=GameCont.loops) return false;
    scrFRSoundMusic(_music.sound,_music.loop);
    return true;
}
