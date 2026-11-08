// Crush Trap's collision wall moves with its projectile body. It is not a
// duplicate level-generation tile and must survive overlap with other walls.
function scrFRPalaceBlockProxy(_wall) {
    return instance_exists(_wall) && (_wall[$ "fr_palace_block_proxy"]??false);
}

function scrFRPalaceBlockWallPair(_a,_b) {
    return scrFRPalaceBlockProxy(_a) || scrFRPalaceBlockProxy(_b);
}

function scrFRPalaceRememberPush(_block) {
    // Capture before the original source changes a victim's position. More
    // than one trap can push it during the same frame; retain the first safe
    // position while keeping the last live pushing body as provenance.
    if((self[$ "fr_palace_push_frame"]??-1)!=current_frame) {
        fr_palace_push_x=x;fr_palace_push_y=y;
    }
    fr_palace_push_frame=current_frame;fr_palace_push_owner=_block;
}

function scrFRPalacePlayerWallCollision(_wall) {
    var _proxy=scrFRPalaceBlockProxy(_wall),
        _age=current_frame-(self[$ "fr_palace_push_frame"]??-1000),
        _owner=self[$ "fr_palace_push_owner"]??noone,
        _pushed=_age>=0 && _age<=1 && instance_exists(_owner)
            && (_owner[$ "name"]??"")=="fr_CrushBlock";
    if(!_proxy && !_pushed) return false;
    // The authored trap already pushes hitme actors and owns crush damage.
    // Native Player's map-wall recovery repeatedly searches every room Floor
    // for an exit, then destroys the wall after 100 unsuccessful one-pixel
    // moves. A moving proxy can close that exit again on the next frame.
    // Let the engine's solid contact and the trap's bounded source push own
    // this pair; never run map-generation recovery against a moving body.
    // Keep the native Hammerhead fast path, which exits before that search.
    if(hammerhead && hammering>6) return false;
    // A squeezed victim can contact the map wall in the same collision pass.
    // Restore its pre-push position only when that position is clear of the
    // contacted wall. It can still overlap the trap, so the authored smush
    // hit and reverse-on-crush run normally. Never search the map or delete
    // either wall to resolve the squeeze.
    var _restored=false;
    if(!_proxy && _pushed && place_meeting(x,y,_wall)
        && !place_meeting(fr_palace_push_x,fr_palace_push_y,_wall)) {
        x=fr_palace_push_x;y=fr_palace_push_y;_restored=true;
    }
    if(os_type==os_windows && scrNTTEFullSmokeEnabled()
        && variable_instance_exists(id,"fr_palace_contact_test")) {
        var _row=fr_palace_contact_test;
        if(is_struct(_row)) {
            _row.collision_calls++;
            if(!_proxy) _row.map_wall_calls++;
            if(_restored) _row.squeeze_restores++;
        }
    }
    return true;
}

function scrFRPalaceSmushStep() {
    // The upstream one-tick impact is born inside a Collision event. Its
    // coroutine wait can resume in the host Step before a new projectile has
    // received its first native Collision phase. Own only this impact's
    // lifetime in End Step, after its real native collision opportunity.
    return self[$ "fr_palace_smush"]??false;
}

function scrFRPalaceSmushHit() {
    var _target=scrFROther(other);
    if(!instance_exists(_target)) return;
    var _key=string(real(_target.id));
    // One authored source tick can span two host Collision phases at60Hz.
    // Apply its actual on_hit once per victim, preserving the source's
    // player/enemy damage choice and the block's reverse-on-crush behavior.
    if(fr_palace_smush_targets[$ _key]??false) return;
    fr_palace_smush_targets[$ _key]=true;
    var _before=_target[$ "hp"]??0;
    scrFRInvoke(id,fr_Objects_Frontier_Palace_mod_gml_CrushBlockSmush_hit,[]);
    if(os_type==os_windows && scrNTTEFullSmokeEnabled())
        scrFRPalaceBlockTestsSmushHit(id,_target,_before);
}

function scrFRPalaceBlockEndStep() {
    if(self[$ "fr_palace_smush"]??false) {
        if(!lockstep_stop) {
            // Do not count the partial Collision-to-End-Step birth frame as
            // a source tick. All later aging happens after native Collision.
            if(fr_palace_smush_age<0) fr_palace_smush_age=0;
            else {
                fr_palace_smush_age+=timescale;
                if(fr_palace_smush_age>=1) instance_destroy();
            }
        }
        return true;
    }
    if((self[$ "name"]??"")!="fr_CrushBlock") return false;
    // Its authored End Step applies native, already scaled hspeed_raw and
    // synchronizes a solid proxy. Run that physical bookkeeping on every host
    // frame; only the AI/cooldowns/cosmetics remain on the source 30 Hz clock.
    if(!lockstep_stop) {
        scrFRActorCallback("on_end_step");
        // The source synchronizes mywall before its final inactive grid snap.
        // After a wall impact the body therefore ends at the snapped point
        // while its collision wall remains at the preceding physical point.
        // Bind the proxy to the completed body position, after that authored
        // snap as well as on every 60 Hz host movement frame.
        if(instance_exists(mywall)) {
            mywall.x=x;mywall.y=y;
            mywall.xprevious=x;mywall.yprevious=y;
        }
        if(os_type==os_windows && scrNTTEFullSmokeEnabled()) scrFRPalaceBlockTestsObserve(id);
    }
    return true;
}
