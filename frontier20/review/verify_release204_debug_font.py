"""Fresh static native range/current Silver cmap/Goto label evidence, no game or build."""
from __future__ import annotations
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import zipfile

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent
SOURCE=ROOT/"native/menu_repairs.gml"
FONT=ROOT/"staging/project/datafiles/lang/Silver.ttf"
IPA=HOST.parents[1]/"outputs/NuclearThroneIOS.ipa"
OUTPUT=ROOT/"review/dbg-font-full-range-coverage-204.json"
MACHO=HOST.parent/"inspect_native_timing.py"
REGISTRATION=HOST/"audit_ios_vm_builtins.py"


def sha(data): return hashlib.sha256(data).hexdigest()


def functions(path,names,namespace):
    tree=ast.parse(path.read_text(encoding="utf-8-sig"))
    definitions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
    assert {node.name for node in definitions}==set(names)
    exec(compile(ast.Module(body=definitions,type_ignores=[]),str(path),"exec"),namespace)
    return namespace


def cmap_has(data,code):
    assert data[:4] in (b"\x00\x01\x00\x00",b"OTTO"),"Expected current standalone SFNT Silver font"
    count=struct.unpack_from(">H",data,4)[0]
    tables={data[12+16*i:16+16*i]:struct.unpack_from(">II",data,20+16*i) for i in range(count)}
    offset,length=tables[b"cmap"];assert offset+length<=len(data)
    cmaps=struct.unpack_from(">H",data,offset+2)[0]
    for index in range(cmaps):
        platform,encoding,relative=struct.unpack_from(">HHI",data,offset+4+8*index)
        if platform!=0 and not(platform==3 and encoding in(1,10)):continue
        start=offset+relative;fmt=struct.unpack_from(">H",data,start)[0]
        if fmt==4 and code<=65535:
            segments=struct.unpack_from(">H",data,start+6)[0]//2
            ends=start+14;starts=ends+2*segments+2;deltas=starts+2*segments;ranges=deltas+2*segments
            for item in range(segments):
                first=struct.unpack_from(">H",data,starts+2*item)[0];last=struct.unpack_from(">H",data,ends+2*item)[0]
                if not first<=code<=last:continue
                delta=struct.unpack_from(">h",data,deltas+2*item)[0]
                distance=struct.unpack_from(">H",data,ranges+2*item)[0]
                if not distance:glyph=(code+delta)&65535
                else:
                    at=ranges+2*item+distance+2*(code-first)
                    assert at+2<=offset+length
                    glyph=struct.unpack_from(">H",data,at)[0]
                    if glyph:glyph=(glyph+delta)&65535
                if glyph:return True
        elif fmt==12:
            groups=struct.unpack_from(">I",data,start+12)[0]
            for item in range(groups):
                first,last,glyph=struct.unpack_from(">III",data,start+16+12*item)
                if first<=code<=last and glyph+code-first:return True
    return False


def audit():
    assert not OUTPUT.exists(),"Preserve completed204 font evidence"
    source=SOURCE.read_bytes();text=source.decode("utf-8-sig")
    call='dbg_add_font_glyphs("lang/Silver.ttf",13,3)'
    assert text.count(call)==1,"Current source lost its Chinese Full range3 request"
    body=text.split("function scrFRDebugAreaLabel(",1)[1].split("\nfunction ",1)[0]
    labels=[(int(area),json.loads(label)) for area,label in re.findall(r'case\s+(\d+):_name=("(?:[^"\\]|\\.)*")',body)]
    assert labels and len({area for area,_ in labels})==len(labels)
    font=FONT.read_bytes();needed={ord(char) for _,label in labels for char in label if ord(char)>127}
    assert needed and all(cmap_has(font,code) for code in needed),"Current Silver cmap omits a current localized Goto character"
    with zipfile.ZipFile(IPA) as archive:
        members=[name for name in archive.namelist() if name.startswith("Payload/") and name.endswith(".app/nuclearthronemobile")]
        assert len(members)==1;native=archive.read(members[0])
    namespace=functions(MACHO,{"read_macho"},{"struct":struct})
    namespace=functions(REGISTRATION,{"sign_extend","registrations"},namespace)
    sections,symbols=namespace["read_macho"](native)
    total,registrations=namespace["registrations"](native)
    registered=registrations["dbg_add_font_glyphs"]
    assert any(row["implementation_in_text"] for row in registered),"Retained native has no real debugger font registration"
    def symbol(name):
        values={row["value"] for row in symbols if row["name"]==name}
        assert len(values)==1,(name,values)
        return values.pop()
    def file_offset(address):
        candidates=[section["offset"]+address-section["addr"] for section in sections
            if section["addr"]<=address<section["addr"]+section["size"]]
        assert len(candidates)==1
        return candidates[0]
    ranges_address=symbol("__ZZN11ImFontAtlas25GetGlyphRangesChineseFullEvE6ranges")
    offset=file_offset(ranges_address);ranges=[];cursor=offset
    while True:
        first,last=struct.unpack_from("<HH",native,cursor)
        if first==0:break
        assert first<=last and len(ranges)<32;ranges.append([first,last]);cursor+=4
    range_bytes=native[offset:cursor+2]
    assert all(any(first<=code<=last for first,last in ranges) for code in needed)
    action=symbol("__Z14ActionFontInfov")
    full=symbol("__ZN11ImFontAtlas25GetGlyphRangesChineseFullEv")
    compare=None
    for step in range(0,1024,4):
        address=action+step;word=struct.unpack_from("<I",native,file_offset(address))[0]
        if word!=0x71000d1f:continue # cmp w8,#3
        branch=struct.unpack_from("<I",native,file_offset(address+4))[0]
        if branch&0xff00001f!=0x54000001:continue # b.ne bypasses range3, unlike the earlier range-limit b.gt
        end=address+4+(namespace["sign_extend"]((branch>>5)&0x7ffff,19)<<2)
        calls=[]
        for here in range(address+8,end,4):
            opcode=struct.unpack_from("<I",native,file_offset(here))[0]
            if opcode&0xfc000000==0x94000000:
                calls.append((here,here+(namespace["sign_extend"](opcode&0x3ffffff,26)<<2)))
        matches=[here for here,target in calls if target==full]
        assert len(matches)==1,"Native range3 branch does not call Chinese Full"
        compare={"address":hex(address),"word":hex(word),"decoded":"cmp w8, #3"}
        conditional={"address":hex(address+4),"word":hex(branch)};call_address=hex(matches[0]);break
    assert compare is not None,"Native font range dispatcher proof was not found"
    # Independently verify the selected function returns the actual table.
    registers={};returned=False
    for here in range(full,full+32,4):
        opcode=struct.unpack_from("<I",native,file_offset(here))[0];dest=opcode&31
        if opcode&0x9f000000==0x90000000:
            immediate=((opcode>>5&0x7ffff)<<2)|(opcode>>29&3)
            registers[dest]=(here&~0xfff)+(namespace["sign_extend"](immediate,21)<<12)
        elif opcode&0xff000000==0x91000000:
            registers[dest]=registers[opcode>>5&31]+((opcode>>10&0xfff)<<(12 if opcode>>22&1 else 0))
        elif opcode==0xd65f03c0:
            assert registers.get(0)==ranges_address;returned=True;break
    assert returned,"Chinese Full function did not return the inspected range table"
    result={"status":"PASS","version":"2.0.4","internal":100,"utc":datetime.now(timezone.utc).isoformat(),
        "scope":"Fresh static retained native registration/dispatcher/table and current Silver cmap/current localized Goto labels; no phone overlay rendering",
        "audit_tool_sha256":sha(Path(__file__).read_bytes()),"native_sha256":sha(native),
        "native_registration_calls":total,"dbg_add_font_glyphs_registration":registered,
        "range_id":3,"range_name":"Chinese Full","dispatcher_symbol":"__Z14ActionFontInfov",
        "compare_instruction":compare,"conditional_not_equal_branch":conditional,"chinese_full_call":call_address,
        "chinese_full_function":hex(full),"full_range_table_sha256":sha(range_bytes),"ranges":ranges,
        "labels":[{"area":area,"text":label,"missing":"","missing_from_current_font":""} for area,label in labels],
        "all_cjk_characters":len(needed),"source_sha256":sha(source),"source_call":call,
        "silver_font_sha256":sha(font),"silver_font_bytes":len(font),"silver_font_cmap_coverage_verified":True,
        "static_helper_sha256":{MACHO.name:sha(MACHO.read_bytes()),REGISTRATION.name:sha(REGISTRATION.read_bytes())},
        "physical_device_tested":False,"physical_device_overlay_rendering_tested":False}
    with OUTPUT.open("x",encoding="utf8") as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write("\n")
    print(json.dumps({"status":"PASS","evidence":str(OUTPUT),"labels":len(labels),"cjk_characters":len(needed),"physical_device_tested":False}))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("operation",choices=("plan","audit"),default="plan",nargs="?")
    args=parser.parse_args()
    if args.operation=="audit":audit()
    else:print(json.dumps({"status":"NOT_REVIEWED","evidence_exists":OUTPUT.exists(),"writes":"Only explicit audit writes new204 static font evidence","game_build_or_network":False}))


if __name__=="__main__":main()
