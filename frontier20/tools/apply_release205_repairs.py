"""Sequentially integrate the reviewed narrow 2.0.5 changes into current stage."""
from pathlib import Path
import json
import argparse
from install_native205 import apply as register_native, load
from set_release205_identity import apply as set_identity
import fr_wall_surface205_hooks
import fr_audio_bubbles205_hooks
import fr_visual205_hooks
import fr_quest_portal205_hooks
import fr_lair_return205_hooks
import fr_quest_portal205_test_hooks
import fr_lair_return205_test_hooks
import fr_quest_continue205_test_hooks
import fr_pirate_visibility205_test_hooks
import fr_cluster_factory205_hooks
import fr_bloodlust205_hooks

ROOT = Path(__file__).resolve().parents[1]


def apply(project):
    project = Path(project).resolve()
    if project != (ROOT / "staging/project").resolve():
        raise RuntimeError("Explicit current-stage integration only")
    report = []
    report.append(register_native(project, load(ROOT / "review/release205-native-map.json")))
    report.append(set_identity(project))
    for module in (fr_wall_surface205_hooks, fr_audio_bubbles205_hooks,
                   fr_visual205_hooks, fr_quest_portal205_hooks, fr_lair_return205_hooks,
                   fr_cluster_factory205_hooks, fr_bloodlust205_hooks):
        report.append({module.__name__: module.apply(project)})
    report.append({"wall_tests": fr_wall_surface205_hooks.apply_tests(project)})
    report.append({"audio_bubbles_tests": fr_audio_bubbles205_hooks.apply(project, tests=True)})
    report.append({"visual_tests": fr_visual205_hooks.apply_tests(project)})
    report.append({"quest_tests": fr_quest_portal205_test_hooks.apply(project)})
    report.append({"lair_tests": fr_lair_return205_test_hooks.apply(project)})
    report.append({"quest_continue_tests": fr_quest_continue205_test_hooks.apply(project)})
    report.append({"pirate_tests": fr_pirate_visibility205_test_hooks.apply(project)})
    report.append({"bloodlust_tests": fr_bloodlust205_hooks.apply_tests(project)})
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(apply(ROOT / "staging/project"), ensure_ascii=False, indent=2))
