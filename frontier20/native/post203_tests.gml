function scrFRPost203ModuleOracle(_kind,_name) {
    if(_kind=="wep") _kind="weapon";
    _name=string_replace_all(_name,"\\","/");
    if(string_pos(":",_name)>0) return global.fr_module_aliases[$ _name]??_name;
    var _suffixes=[".mod.gml",".mod.ntgml",".wep.gml",".area.gml",".skill.gml",".race.gml",".skin.gml",".crown.gml"];
    for(var _i=0;_i<array_length(_suffixes);++_i) {
        var _suffix=_suffixes[_i],_at=string_length(_name)-string_length(_suffix)+1;
        if(_at>0 && string_copy(_name,_at,string_length(_suffix))==_suffix) {_name=string_delete(_name,_at,string_length(_suffix));break;}
    }
    var _key=_kind+":"+_name;
    return global.fr_module_aliases[$ _key]??_key;
}
function scrFRPost203CompatTests() {
    var _language=global.language_current[$ "Init:Id"],_game=scrNTTEFullAreaGeneratorSnapshot(GameCont),
        _before=scrNTTEFullInstances(all),_rows=[],_seed=random_get_seed(),_rng=scrNTTEFullArrayCopy(global.rng_state);
    try {
        var _names=["coast","oasis","pizza","lair","trench","red","undergrowth"];
        for(var _i=0;_i<array_length(_names);++_i) {
            for(var _form=0;_form<3;++_form) {
                var _area=_form==0?201+_i:(_form==1?_names[_i]:"area:"+_names[_i]);
                assert(scrFRSourceCurrentlyOutside(_area)==(_i==0),"Native area outside predicate changed source coast list or missing callback semantics");
                assert(is_undefined(scrFRModCall("area",_area,"area_outside")),"Native area invented an absent source area_outside callback");
                var _wet=_i==1 || _i==4;
                assert(scrFRScriptExists("area",_area,"area_underwater")==_wet,
                    "Native area underwater callback existence differs from NTTE source");
                assert((scrFRModCall("area",_area,"area_underwater")==true)==_wet,
                    "Native area underwater query lost the oasis/trench source distinction");
                if(! _wet) assert(is_undefined(scrFRModCall("area",_area,"area_underwater")),
                    "Native dry area fabricated an optional source callback");
            }
            // Exercise the reported real Main step against each native ID,
            // retaining its actual frame owner and all original dispatch.
            GameCont.area=201+_i;
            with(GameCont) scrFRModCall("mod","Frontier_Main","step");
        }
        for(var _id=301;_id<=306;++_id) {
            var _expected=(_id==302 || _id==304 || _id==305);
            assert(scrFRSourceCurrentlyOutside(_id)==_expected,"NTUF area_outside source callback changed");
        }
        var _failed=false;
        try {scrFRModCall("area","__unknown204","area_outside");} catch(_exception) {_failed=true;}
        assert(_failed,"Native metadata bridge swallowed an unknown module error");
        global.language_current[$ "Init:Id"]="Simplified Chinese";
        scrNTTEFullLocalizeInstall();
        assert(scrNTTEFullWeaponNameDisplay("LIGHTRING CANNON")=="电环加农炮"
            && scrNTTEFullWeaponNameDisplay("LIGHTRING LAUNCHER")=="电环发射器"
            && scrNTTEFullWeaponNameDisplay("LIGHTRING 加农炮")=="电环 加农炮",
            "LIGHTRING standalone/fusion names remain untranslated");
        assert(string_pos("LIGHTRING",scrNTTEFullWeaponNameDisplay("SUPER LIGHTRING SHOTGUN"))==0,
            "LIGHTRING generated name fragment was not translated");
        assert(wep_name[wep_ntte_lightring_launcher]=="LIGHTRING LAUNCHER"
            && scrNTTEFullWeaponDropNativeRecord(wep_ntte_lightring_launcher).raw=="lightring launcher",
            "Presentation translation changed canonical weapon or save identity");
        global.language_current[$ "Init:Id"]="English";
        assert(scrNTTEFullWeaponNameDisplay("LIGHTRING CANNON")=="LIGHTRING CANNON",
            "LIGHTRING translation changed English presentation");
        var _inputs=[["mod","Frontier_Main"],["mod","Frontier_Main.mod.gml"],
            ["area","Areas\\cove.area.gml"],["wep","Weapons/FR_Blunderbuss.wep.gml"],
            ["mod","mod:Frontier_Events"],["mod",""],["race","bubbles.race.gml"],
            ["skin","RobotBluescreened.skin.gml"],["skill","AugmentExtraFeet.skill.gml"]];
        repeat(2) for(var _i=0;_i<array_length(_inputs);++_i)
            assert(scrFRModuleKey(_inputs[_i][0],_inputs[_i][1])==scrFRPost203ModuleOracle(_inputs[_i][0],_inputs[_i][1]),
                "Cached module normalization differs from the original lexical oracle");
        var _alias="mod:__post203_alias";
        assert(!variable_struct_exists(global.fr_module_aliases,_alias),"Post203 test alias already exists");
        try {
            global.fr_module_aliases[$ _alias]="mod:Frontier_Main";
            assert(scrFRModuleKey("mod",_alias)=="mod:Frontier_Main","New alias was not read live");
            global.fr_module_aliases[$ _alias]="mod:Frontier_Events";
            assert(scrFRModuleKey("mod",_alias)=="mod:Frontier_Events","Cached normalization retained stale alias target");
            variable_struct_remove(global.fr_module_aliases,_alias);
            assert(scrFRModuleKey("mod",_alias)==_alias,"Removed alias stayed cached");
        } finally {variable_struct_remove(global.fr_module_aliases,_alias);}
        for(var _sample=0;_sample<5;++_sample) {
            var _times=[];
            for(var _pass=0;_pass<2;++_pass) {
                var _oracle=(_pass+_sample) mod 2==0;
                global.fr_module_key_oracle=_oracle;
                var _start=get_timer(),_checksum=0;
                repeat(4000) for(var _i=0;_i<array_length(_inputs);++_i)
                    _checksum+=string_length(scrFRModuleKey(_inputs[_i][0],_inputs[_i][1]));
                array_push(_times,{oracle:_oracle,microseconds:get_timer()-_start,checksum:_checksum});
            }
            assert(_times[0].checksum==_times[1].checksum,"Module lookup benchmark changed results");
            array_push(_rows,_times);
        }
        scrNTTESmokeLog("FRONTIER MODULE NORMALIZATION BENCHMARK "+json_stringify(_rows));
        var _file=file_text_open_write(working_directory+"frontier-post203-compat.json");
        file_text_write_string(_file,json_stringify({native_area_forms:21,ntuf_areas:6,
            source_main_steps:7,display_only_lightring:true,module_normalization:_rows}));file_text_close(_file);
    } finally {
        global.fr_module_key_oracle=false;global.language_current[$ "Init:Id"]=_language;
        scrNTTEFullMergedRuntimeTestCleanup(_before);scrNTTEFullAreaGeneratorRestore(_game);
        random_set_seed(_seed);global.rng_state=_rng;
    }
    scrNTTESmokeLog("PASS FRONTIER native area207 optional dispatch, all native area predicates, LIGHTRING display and live-alias cached module normalization");
}
