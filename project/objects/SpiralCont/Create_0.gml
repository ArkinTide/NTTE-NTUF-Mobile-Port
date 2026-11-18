enum SpiralType {
	Normal,
	Proto,
	IDPD,
	Venuz
}

fishx = view_width div 2
fishy = view_height div 2

image_angle = random_angle

bossfight = instance_exists(Nothing2) || instance_exists(Nothing2Appear) || instance_exists(NothingSpiral)

type = SpiralType.Normal

active = true
area = area_campfire
time = 0

// [60帧适配] 环的生成基准是 30Hz（见 Step_0.gml）
spawn_toggle = false

if instance_exists(GameCont) {
	area = GameCont.area
	
    if area == area_vault {
		type = SpiralType.Proto
	}
    else if area == area_hq {
		type = SpiralType.IDPD
	}
    else if (area == area_mansion || area == area_crib) {
		type = SpiralType.Venuz
	}
}


// [60帧适配] 预热循环按「帧」计数，60fps 下会少模拟一半逻辑步 → 按 timescale 折算次数。
//
// FRONTIER214 bounded decorative warm-up. Only these visual events are
// simulated here. Restore host timing even if an authored visual callback fails.
var _fr_spiral_saved_dt214=timescale;
try {
    global.time_scale=scrFRSpiralDelta214(_fr_spiral_saved_dt214);
    repeat (scrFRSpiralWarmCount214(timescale)) {
        event_perform(ev_step, 0)
        with Spiral event_perform(ev_step, 0)
        with SpiralDebris event_perform(ev_step, 0)
        with SpiralStar event_perform(ev_step, 0)
    }
} finally {global.time_scale=_fr_spiral_saved_dt214;}

snd_play_ambience(sndPortalLoop, true)


if (!instance_exists(NothingSpiral)) scrLetterbox(true)
// NTTE Pizza original star/cover transition
if(instance_exists(GameCont) && GameCont.area==scrNTTEFullAreaId("pizza")) scrNTTEFullPizzaSpiralSetup();
// NTTE Red original post-warmup loading-screen setup.
if(instance_exists(GameCont) && GameCont.area==scrNTTEFullAreaId("red")) scrNTTEFullRedSpiralSetup();
