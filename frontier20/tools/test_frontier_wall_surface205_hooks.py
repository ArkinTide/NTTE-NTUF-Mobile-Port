import unittest
from fr_wall_surface205_hooks import transform_macro, transform_top


class WallSurface205Hooks(unittest.TestCase):
    def test_macro_only_clips_art_and_is_idempotent(self):
        source = ("before\n#macro mcr_wall_update_lrwh { \\\n"
                  "if(place_free(x-16,y)) l=0; if(place_free(x+16,y)) w=24; \\\n"
                  "if(place_free(x,y-16)) r=0; if(place_free(x,y+16)) h=24; \\\n"
                  "}\n\nafter=place_free(x,y);\n")
        changed = transform_macro(source)
        self.assertEqual(changed.count("scrFRWallArtFree205("), 4)
        self.assertIn("after=place_free(x,y)", changed)
        self.assertEqual(transform_macro(changed), changed)

    def test_fill_precedes_all_edge_art(self):
        source = ("prefix\nvar _list = global.lis_walls_visible,\n_count=0;\n"
                  "draw_sprite_part_ext(outspr,0,0,0,24,24,x,y,1,1,0,1);\n"
                  "scrNTTESolidWallDraw();\nwith TopSmall draw_self();\n")
        changed = transform_top(source)
        self.assertLess(changed.index("scrNTTESolidWallDraw();"), changed.index("draw_sprite_part_ext("))
        self.assertEqual(transform_top(changed), changed)

    def test_changed_and_partial_anchors_rejected(self):
        with self.assertRaises(ValueError):
            transform_macro("no macro")
        with self.assertRaises(RuntimeError):
            transform_top("var _list = global.lis_walls_visible,")
        with self.assertRaises(RuntimeError):
            transform_top("// FRONTIER WALL ART205 FILL BEFORE SOURCE EDGES\n"
                          "var _list = global.lis_walls_visible,\nscrNTTESolidWallDraw();")


if __name__ == "__main__":
    unittest.main()
