// NTTE SOURCE LEAD RIBS BEFORE CHILD DEATH
if(hp<=0) scrNTTEFullLeadRibsDeath(id);
// BEGIN FRONTIER BLOODLUST205 DYING ENEMY
scrFRBloodlust205EnemyDeath();
// END FRONTIER BLOODLUST205 DYING ENEMY
instance_create(x, y, Nothing2Death)

with (MusCont) alarm[1] = 1

with projectile {
    if (team != team_player) instance_destroy()
}

snd_play_hit_big(sndNothing2DeadStart, 0.2)

repeat (2) scrDrop(100, 0)

//event_inherited()
scrOnBossKill()