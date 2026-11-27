"""Version-only 2.1.6/build111 edits; save/network protocol remains3004."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'staging/project'

def apply():
    sites={
        'objects/UberCont/Create_0.gml':[('#macro GAME_VERSION "2.1.5"','#macro GAME_VERSION "2.1.6"')],
        'scripts/scrNTTEUpdate/scrNTTEUpdate.gml':[
            ('#macro NTTE_RELEASE_NUMBER 110','#macro NTTE_RELEASE_NUMBER 111'),
            ('#macro NTTE_RELEASE_TAG "2.1.5"','#macro NTTE_RELEASE_TAG "2.1.6"'),
            ('#macro NTTE_RELEASE_VERSION "2.1.5"','#macro NTTE_RELEASE_VERSION "2.1.6"')],
        'options/android/options_android.yy':[('"option_android_version": "2.1.5"','"option_android_version": "2.1.6"')],
        'options/ios/options_ios.yy':[
            ('"option_ios_version": "2.1.5"','"option_ios_version": "2.1.6"'),
            ('"option_ios_build_number": 110','"option_ios_build_number": 111')],
        'options/windows/options_windows.yy':[('"option_windows_version": "2.1.5.0"','"option_windows_version": "2.1.6.0"')],
    }
    pending=[]
    for name,pairs in sites.items():
        path=PROJECT/name;data=path.read_bytes()
        for old,new in pairs:
            old,new=old.encode(),new.encode()
            if new in data:continue
            assert data.count(old)==1,(name,old)
            data=data.replace(old,new)
        pending.append((path,data))
    for path,data in pending:
        if path.read_bytes()!=data:path.write_bytes(data)
if __name__=='__main__':apply()
