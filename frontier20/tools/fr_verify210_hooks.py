"""Install additional 2.1.0 coverage without reimporting source modules."""
from apply_release210_repairs import ROOT, PROJECT, change
from install_native205 import apply


def main():
    path=PROJECT/'scripts/scrNTTEFullSystems/scrNTTEFullSystems.gml'
    change(path,'return {schema:1,achievements_blocked210:',
           'return {schema:1,content210:{ntuf:scrFRContent210Active("ntuf"),undergrowth:scrFRContent210Active("undergrowth")},achievements_blocked210:')
    change(path,'    GameCont.ntte_full_skills=_state.skills',
           '    scrFRContent210Import(_state); // FRONTIER210 CONTINUE CONTENT\n    GameCont.ntte_full_skills=_state.skills')
    apply(PROJECT,{'features210_tests.gml':'scrFrontier_features210_tests',
                   'content210.gml':'scrFrontier_content210',
                   'hyperion_projectile_tests.gml':'scrFrontier_hyperion_projectile_tests'})


if __name__=='__main__': main()
