"""Mutable red-room boundaries use authored artwork, not compact collision."""
from apply_release210_repairs import ROOT, PROJECT, change
from install_native205 import apply


def main():
    path=PROJECT/'scripts/scrNTTEFullFloor/scrNTTEFullFloor.gml'
    change(path,'&& !position_meeting(_x,_y,Floor)) array_push(_out,instance_create(_x,_y,Wall))',
           '&& !position_meeting(_x,_y,Floor) && !scrNTTESolidWallPlanPoint(_x,_y)) array_push(_out,instance_create(_x,_y,Wall))')
    change(path,'l=place_free(x-16,y) ? 0:4; w=(place_free(x+16,y) ? 24:20)-l\n        r=place_free(x,y-16) ? 0:4; h=(place_free(x,y+16) ? 24:20)-r',
           'l=scrFRWallArtFree205(x-16,y) ? 0:4; w=(scrFRWallArtFree205(x+16,y) ? 24:20)-l\n        r=scrFRWallArtFree205(x,y-16) ? 0:4; h=(scrFRWallArtFree205(x,y+16) ? 24:20)-r')
    # TopSmall is an unowned transition cell. Repeated neighbouring floor
    # updates must reuse that cell, rather than stack opaque copies.
    path=PROJECT/'objects/TopSmall/Create_0.gml'
    before='var _area;'
    after='''// FRONTIER210 UNIQUE TRANSITION CELL
var _tx=x,_ty=y,_tid=real(id),_duplicate=false;
with(TopSmall) if(x==_tx && y==_ty && real(id)<_tid) {_duplicate=true;break;}
if(_duplicate) {instance_destroy(id,false);exit;}

var _area;'''
    change(path,before,after)
    path=PROJECT/'scripts/scrNTTEFullRedAreaNative/scrNTTEFullRedAreaNative.gml'
    change(path,'        instance_create(x+scrNTTEFullSourceChoose([0,16]),y+scrNTTEFullSourceChoose([0,16]),Wall)',
           '        var _rock=instance_create(x+scrNTTEFullSourceChoose([0,16]),y+scrNTTEFullSourceChoose([0,16]),Wall);_rock.fr_red210_rock=true;')
    change(path,'function scrNTTEFullRedPopulateNative() {scrPopulate();scrNTTEFullRedPopExtras()}',
           'function scrNTTEFullRedPopulateNative() {scrPopulate();scrNTTEFullRedPopExtras();scrFRRedTerrain210Finish();}')
    apply(PROJECT,{'red_terrain210_tests.gml':'scrFrontier_red_terrain210_tests',
                   'red_terrain210.gml':'scrFrontier_red_terrain210'})
    for path in [ROOT/'native/tests.gml',PROJECT/'scripts/scrFrontier_tests/scrFrontier_tests.gml']:
        change(path,'    if(fr_test_case=="features210") {',
               '''    if(fr_test_case=="red-terrain210") {
        if(!scrFRReadyTick() || ++fr_test_ticks<45) return;
        scrFRRedTerrain210Tests();
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
        game_end();return;
    }
    if(fr_test_case=="features210") {''')
    path=PROJECT/'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml'
    change(path,'if(scrNTTEFullSmokeAsyncCase("FrontierFeatures210Tests"))',
           'if(scrNTTEFullSmokeAsyncCase("FrontierRedTerrain210Tests")) {scrFRIntegrationTestStart("red-terrain210");return;}\n        if(scrNTTEFullSmokeAsyncCase("FrontierFeatures210Tests"))')


if __name__=='__main__': main()
