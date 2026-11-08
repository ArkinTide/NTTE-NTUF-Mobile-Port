// Heavy Seal's authored 8:1.5 swing emphasis must not drive a normalized
// full-scale sample at8x gain into the shared output. Keep the exact source
// pitch/random-call and emphasis ratio, with headroom on this transient only.
// No resource, music, ambience, emitter, or global volume/pitch is edited.
function scrFRSealHeavySpinSound(_holding_anchor) {
    return snd_play(sndMeleeFlip,0.1+random(0.1),_holding_anchor ? 0.8:0.15);
}
