"""Keep Ultimate Quest wave gaps out of ordinary level-exit recovery.

Only these two native consumers consult the live locked-chest owner. The
quest's real enemy list and the explicit CrownPickup exit remain unchanged.
Importing this module never writes a project; apply preflights both files
before committing either one and rolls back any failed write.
"""
from pathlib import Path


SITES = (
    (
        "scripts/scrNTTEFullLairWorld/scrNTTEFullLairWorld.gml",
        "function scrNTTEFullPortalBlocked() {",
        "    if(scrFRQuestPortal204Blocked()) return true;",
        "ORDINARY EXIT",
        False,
    ),
    (
        "scripts/scrNTTEAllies/scrNTTEAllies.gml",
        "    if (!global.is_server || !scrNTTEPortalRecoveryAllowed() || !instance_exists(Player) || instance_exists(Portal)) return;",
        "    if(scrFRQuestPortal204Blocked()) return;",
        "RECOVERY SCHEDULER",
        True,
    ),
)


def transform(source, signature, guard, identity, before=False):
    """Accept one exact pristine or fully installed function-entry anchor."""
    source = source.replace("\r\n", "\n")
    begin = f"    // BEGIN FRONTIER QUEST PORTAL204 {identity}\n"
    end = f"    // END FRONTIER QUEST PORTAL204 {identity}\n"
    block = begin + guard + "\n" + end
    original = signature + "\n"
    installed = block + original if before else original + block
    if source.count(signature) != 1:
        raise RuntimeError("Quest portal204 function identity is ambiguous: " + signature)
    if begin in source or end in source:
        if (source.count(begin) != 1 or source.count(end) != 1
                or source.count(installed) != 1
                or source.count("scrFRQuestPortal204Blocked()") != 1):
            raise RuntimeError("Quest portal204 partial, duplicated or moved guard: " + identity)
        return source
    if "scrFRQuestPortal204Blocked()" in source:
        raise RuntimeError("Quest portal204 unowned guard: " + identity)
    if source.count(original) != 1:
        raise RuntimeError("Quest portal204 function entry changed: " + signature)
    return source.replace(original, installed, 1)


def apply(project):
    """Preflight exact two native scripts, then commit a bounded transaction."""
    project = Path(project).resolve()
    changes = []
    for relative, signature, guard, identity, before in SITES:
        target = project / relative
        if target.is_symlink() or not target.resolve().is_relative_to(project):
            raise RuntimeError("Quest portal204 path escapes project: " + relative)
        original = target.read_bytes()
        source = original.decode("utf-8-sig")
        updated = transform(source, signature, guard, identity, before)
        if updated != source.replace("\r\n", "\n"):
            changes.append((target, original, updated.encode("utf8")))
    written = []
    try:
        for target, original, updated in changes:
            written.append((target, original))
            target.write_bytes(updated)
    except BaseException:
        for target, original in reversed(written):
            target.write_bytes(original)
        raise
    return {
        "quest_owner_guard": True,
        "owner": "NTTEFullLockedHugeQuestChest",
        "changed_paths": [target.relative_to(project).as_posix() for target, _, _ in changes],
        "consumer_count": len(SITES),
    }
