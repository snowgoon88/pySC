#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO : analyse_battle
# TODO : monitor dmg taken
# TODO : add vs time for dmg (need to read in time ...) and susbtract from
# beginning of battle or time of death.

import re
import parse as pa
import sys

import data_snib
from classes import *

import numpy as np

d_mk = {'Base':'Base','Mk0':'Mk0','Mk1':'Mk1', 'Rare':'Mk2', 'Mk3':'Mk3', 'Epic':'Mk4'} 
d_weapon = {
'Weapon_Railgun_Autofire':'Canon Shrapnel',
'SpaceMissile_AAMu':'Petit Missile (TH)',
'Module_PlasmaWeb':'Toile au Plasma',
'Module_EnergyLance':'Arc Plasma',
'SpaceMissile_AAMEMP':'Missile Plasma',
'Weapon_Railgun_Heavy':'Coil Mortar',
'SpaceMissile_Volley':'Pieuvre',
'Module_SmartBomb':'Pulsar',
}
d_heal_module = {
'Module_ShieldRestoreSmall':['---', 'SHIELD'],
'Module_ShieldRestoreLarge':['---', 'SHIELD'],
'Module_RepairDrones_s':['---', 'SHIELD/HULL'],
'Module_RepairDrones_m':['---', 'SHIELD/HULL'],
'Module_ShieldRestoreMedium':['---', 'SHIELD'],
'Module_FrigateDrone':['---', 'SHIELD/HULL'],
'Module_ShieldVampire':['---', 'SHIELD'],
'Module_RemoteRepairDrones':['---', 'SHIELD/HULL'],
'Module_ShieldEmitter':['---', 'SHIELD'],
}

    
    
l_Battles = []       # [Battle]
battles = []         # [[start,id,type,map,team,end,winner,time,reason]
kills = []           # [index,killer,target,dmg,weapon,[assister,dmg,weapon,None|debuf]...]
spawns = []          # [index,player,ship]
captures = []        # [index,team_nb,what,attackers,...] !!!! team_nb = 0 !!!!
damages = []         # [index,player,weapon,val,type,target,whom,which,crit,explosion]
l_heals = []         # [index, player, target, val, module]
l_spells = []        # [index,spell,player,module,nb_targets,targets]
l_apply = []         # [index,aura,id,module,target]
l_cancel = []        # [index,aura,id,target]

lines = []

def dump_battles( verb=False):
    print len(battles)," batailles, ",len(kills)," kills"
    ds = ""
    for b in battles:
        #ds += str(b)+"\n"
        ds += "Bataille type="+b[2]+" map="+b[3]+" team="+str(b[4])+" win=team"+str(b[6])+" time="+str(b[7])+"s cause="+b[8]+"\n"
        if verb:
            ds += "DEBUG de "+str(b[0])+" à "+str(b[5])+" id="+str(b[1])+"\n"
        # for k in kills:
        #     print "KILL=",k
        #     if (k[0] > b[0] and k[0] < b[5]):
        #         ds += "   KILL="+str(k)
        #         ds += 
    return ds
def dump_kills( battle ):
    """
    Affiche tous les kills d'une bataille.
    """
    ds = ""
    for k in kills:
        if (k[0] > battle[0] and k[0] < battle[5]):
            ds += k[2]+" KILLED by "+k[1]+" with "+k[4]+" ("+str(k[3])+" dmg)\n"
            ds += "DEBUG index="+str(k[0])+"\n"
            for a in k[5:]:
                ds += "   + "+a[0]+" with "+a[2]+" ("+str(a[1])+" dmg)"
                if a[3] != None:
                    ds += "<"+str(a[3])+"> "
                ds += "\n"
        elif k[0] > battle[5]:
            return ds
    return ds
def dump_spawns( battle):
    """
    Affiche tous les spawns d'une bataille.
    """
    ds = ""
    for s in spawns:
        if (s[0] > battle[0] and s[0] < battle[5]):
            ds += s[1]+" PLOP avec un "+s[2]+" => "+data_snib.d_ships[s[2]]+"\n"
            ds += "DEBUG index="+str(s[0])+"\n"
        elif s[0] > battle[5]:
            return ds
    return ds
def dump_captures( battle ):
    """
    Affiche toutes les captures d'un bataille
    """
    ds = ""
    for c in captures:
        if (c[0] > battle[0] and c[0] < battle[5]):
            ds += c[2]+" CAPTURED by team "+str(c[1])+ " ("
            for a in c[3:]:
                ds += a+", "
            ds += ")\n"
            ds += "DEBUG index="+str(c[0])+"\n"
        elif c[0] > battle[5]:
            return ds
    return ds
def dump_damages( battle ):
    """
    Affiche tous les dommages. # [index,player,weapon,val,type,target,whom,which,crit,explosion]
    """
    ds = ""
    for d in damages:
        if (d[0] > battle[0] and d[0] < battle[5]):
            ds += d[1]+" USED "+d[2]+"["+d[7]+"] on "+d[5]+"("+d[6]+") for "+d[3]+" "+d[4]+" (crit="+d[8]+" expl="+d[9]+")"
            ds += "\n"
            ds += "DEBUG index="+str(d[0])+"\n"
        elif d[0] > battle[5]:
            return ds
    return ds
def dump_heal( battle ):
    """
    heal_evt = (index, player, target, val, module)
    """
    ds = ""
    for h in l_heals:
        if (h[0] > battle[0] and h[0] < battle[5]):
            ds += h[1]+" HEALED "+h[2]+" of "+str(h[3])+" pt with "+h[4]
            ds += "\n"
            ds += "DEBUG index="+str(h[0])+"\n"
        elif h[0] > battle[5]:
            return ds
    return ds
def dump_spell( battle ):
    """
    [index,spell,player,module,targets]
    """
    ds = ""
    for s in l_spells:
        if (s[0] > battle[0] and s[0] < battle[5]):
            ds += "SPELL "+s[1]+" by "+s[2]+" using "+s[3]+" on ("+str(s[4])+") "+s[5]
            ds += "\n"
            if s[4] > 1:
                ds += "DEBUG index="+str(s[0])+"\n"
                ds += "      line="+lines[s[0]]+"\n"
        elif s[0] > battle[5]:
            return ds
    return ds
def dump_apply( battle ):
    """
    [index,aura,id,module,target]
    """
    ds = ""
    for a in l_apply:
        if (a[0] > battle[0] and a[0] < battle[5]):
            ds += "APPLY "+a[1]+"("+str(a[2])+") using "+a[3]+" on "+a[4]
            ds += "\n"
            ds += "DEBUG index="+str(a[0])+"\n"
            ds += "      line="+lines[a[0]]+"\n"
        elif a[0] > battle[5]:
            return ds
    return ds
def dump_cancel( battle ):
    """
    [index,aura,id,target]
    """
    ds = ""
    for c in l_cancel:
        if (c[0] > battle[0] and c[0] < battle[5]):
            ds += "CANCEL "+c[1]+"("+str(c[2])+") on "+c[3]
            ds += "\n"
            ds += "DEBUG index="+str(c[0])+"\n"
            ds += "      line="+lines[c[0]]+"\n"
        elif c[0] > battle[5]:
            return ds
    return ds

            
                                    
def prep_log( sourcename, destname ):
    """
    Remplace tous les | par des '-'.
    """
    # Open log file
    src_file = open(sourcename, 'r')
    des_file = open(destname, 'w')
    for line in src_file:
        rep = line.replace('|', '-')
        des_file.write(rep)
    src_file.close()
    des_file.close()
    
def read_log( filename ):
    """
    """
    global lines
    # Open log file
    log_file = open(filename, 'r')
    lines = log_file.readlines()
    print "Log file read =",len(lines)
    # TMP max_kill_read
    # max_kill_parse = 2
    
    global battles,kills,spawns,captures,damages,l_heals,l_apply,l_cancel,l_spells
    battles = []         # [[start,id,type,map,team,end,winner,time,reason]
    kills = []           # [index,killer,target,dmg,weapon,[assister,dmg,weapon,None|debuf]...]
    spawns = []          # [index,player,ship]
    captures = []        # [index,team_nb,what,attackers,...] !!!! team_nb = 0 !!!!
    damages = []         # [index,player,weapon,val,type,target,whom,which,crit,explosion]
    l_heals = []         # [index, player, target, val, module]
    l_spells = []        # [index,spell,player,module,nb_targets,targets]
    l_apply = []         # [index,aura,id,module,target]
    l_cancel = []        # [index,aura,id,target]

    
    # Cherche début de bataille
    index = 0
    data = [0] #start of battle
    while (index<len(lines)):
        line = lines[index]
        if re.search('Connect to game session', line ) :
            data = [index]
            res = pa.search( 'session {id:d} ======', line)
            data.append(res['id'])
            index += 1
        elif re.search('- ======= Start', line ):
            index = parse_start(line, index, data)
        elif re.search('- Gameplay finished', line) :
            index = parse_end(line, index, data)
            battles.append(data)
        #elif re.search( '- Killed', line):
        #    kill = []
        #    index = parse_kill( line, index, kill)
        #    kills.append(kill)
        #elif re.search( '- Spawn', line):
        #    spawn = []
        #    index = parse_spawn( line, index, spawn)
        #    spawns.append(spawn)
        #elif re.search( '- Captured', line):
        #    capt = []
        #    index = parse_capture( line, index, capt)
        #    captures.append(capt)
        #elif re.search( '- Damage', line):
        #    dam = []
        #    index = parse_dmg( line, index, dam )
        #    damages.append(dam)
        #elif re.search( '- Heal', line):
        #    heal_event = []
        #    index = parse_heal( line, index, heal_event)
        #    l_heals.append( heal_event )
        #elif re.search( '- Spell', line):
        #    spell_event = []
        #    index = parse_spell( line, index, spell_event)
        #    l_spells.append( spell_event )
        #elif re.search( '- Apply', line):
        #    apply_evt = []
        #    index = parse_apply( line, index, apply_evt)
        #    l_apply.append( apply_evt )
        elif re.search( '- Cancel', line):
            cancel_evt = []
            index = parse_cancel( line, index, cancel_evt)
            l_cancel.append(cancel_evt)
        else:
            #line = log_file.readline()
            index += 1     

# ==============================================================================
def read_combatgame( name_combat, name_game):
    """
    Cherche les combat et surtout les teams.
    """
    global lines
    # Open log file
    log_file = open(name_combat, 'r')
    lines = log_file.readlines()
    print "Log file read =",len(lines)
    #
    # Game
    game_file = open( name_game, 'r')
    game_lines = game_file.readlines()
    print "GAME file read=",len(game_lines)
    # TMP max_kill_read
    # max_kill_parse = 2
    
    global battles,kills,spawns,captures,damages,l_heals,l_apply,l_cancel,l_spells
    battles = []         # [[start,id,type,map,team,end,winner,time,reason]
    kills = []           # [index,killer,target,dmg,weapon,[assister,dmg,weapon,None|debuf]...]
    spawns = []          # [index,player,ship]
    captures = []        # [index,team_nb,what,attackers,...] !!!! team_nb = 0 !!!!
    damages = []         # [index,player,weapon,val,type,target,whom,which,crit,explosion]
    l_heals = []         # [index, player, target, val, module]
    l_spells = []        # [index,spell,player,module,nb_targets,targets]
    l_apply = []         # [index,aura,id,module,target]
    l_cancel = []        # [index,aura,id,target]

    # Cherche débuts de bataille
    index = 0
    current_battle = None
    data = [0] #start of battle
    while (index<len(lines)):
        line = lines[index]
        #~ print "index=",index,"--",line
        if re.search('Connect to game session', line ) :      # ---------- GAME
            #~ print "GAME start"
            data = [index]
            res = pa.search( 'session {id:d} ======', line)
            data.append(res['id'])
            current_battle = Battle(res['id'])
            index += 1
        elif re.search('- ======= Start', line ):
            #~ print "START"
            index = parse_start(line, index, data)
        elif re.search('- Gameplay finished', line) :
            print "GAME end"
            index = parse_end(line, index, data)
            #battles.append(data)
            current_battle.set(data[0],data[5],data[2],data[3],data[4],data[6],data[7],data[8])
            l_Battles.append(current_battle)
        elif re.search( '- Spawn', line):  # ---------------------------- SPAWN
            #~ print "SPAWN"
            spawn = []
            index = parse_spawn( line, index, spawn)
            #spawns.append(spawn)
            if current_battle:
                current_battle._l_events.append(Spawn(spawn[0],spawn[1],spawn[2]))
        elif re.search( '- Killed', line):    # -------------------------- KILL
            #~ print "KILL"
            kill = []
            index = parse_kill( line, index, kill)
            #kills.append(kill)
            if current_battle:
                k = Kill(kill[0],kill[1],kill[2],kill[3],kill[4])
                for assist in kill[5:]:
                    k._assist.append(assist)
                current_battle._l_events.append(k)
        elif re.search( '- Captured', line):   # ---------------------- CAPTURE
            #~ print "CAPT"
            capt = []
            index = parse_capture( line, index, capt)
            #captures.append(capt)
            if current_battle:
                c = Capture(capt[0],capt[1],capt[2])
                for att in capt[3:]:
                    c._attackers.append(att)
                current_battle._l_events.append(c)
        elif re.search( '- Damage', line):    # --------------------------- DMG
            #~ print "DMG"
            dam = []
            index = parse_dmg( line, index, dam )
            #damages.append(dam)
            if current_battle:
                d = Dmg(dam[0],dam[1],dam[2],dam[3],dam[4],dam[5],dam[6],dam[7],dam[8],dam[9])
                current_battle._l_events.append(d)
                #~ #
                #~ # Des dmg de collision => kill : TODO a changer
                #~ # TODO
                #~ if d._weapon == 'crash':
                    #~ k = Kill(d._index,"-",d._target,d._val,d._weapon)
                    #~ current_battle._l_events.append(k)
        elif re.search( '- Heal', line):      # -------------------------- HEAL
            #~ print "HEAL"
            heal_event = []
            index = parse_heal( line, index, heal_event)
            #l_heals.append( heal_event )
            if current_battle:
                h = Heal(heal_event[0],heal_event[1],heal_event[2],heal_event[3],heal_event[4])
                current_battle._l_events.append(h)
        elif re.search( '- Spell', line):    # -------------------------- SPELL
            #~ print "SPELL"
            spell_event = []
            index = parse_spell( line, index, spell_event)
            #l_spells.append( spell_event )
            if current_battle:
                s = Spell(spell_event[0],spell_event[1],spell_event[2],spell_event[3])
                if spell_event[4] > 0:
                    s._target = spell_event[5]
                current_battle._l_events.append(s)
        elif re.search( '- Apply', line):
            #~ print "APPLY"
            apply_evt = []
            index = parse_apply( line, index, apply_evt)
            #l_apply.append( apply_evt )
            if current_battle:
                a = Apply(apply_evt[0],apply_evt[1],apply_evt[2],apply_evt[3],apply_evt[4])
                current_battle._l_events.append(a)
        else:
            #~ print "UNK"
            line = log_file.readline()
            index += 1     
    #~ print "LINE=",index
    # Peuple les batailles
    game_index = 0
    game_id = 0
    current_battle = None
    while (game_index<len(game_lines)):
        line = game_lines[game_index]
        if re.search( 'MasterServerSession', line) :
            #~ print "MASTER"
            res = pa.search( 'session {id:d}', line)
            game_id = res['id']
            for b in l_Battles:
                if b._id == game_id:
                    current_battle = b
            game_index += 1
        elif re.search( 'ADD_PLAYER', line):
            res = pa.search( 'ADD_PLAYER {num:d} ({player}, {id}) status {status:d} team {team:d}', line)
            if res != None and current_battle != None:
                if res['team'] == 1:
                    current_battle._l_players1.append(res['player'])
                else:
                    current_battle._l_players2.append(res['player'])
            game_index += 1
        elif re.search( '====== starting level', line):
            # on stoppe l'ajout des joueurs
            current_battle = None
            game_index += 1
        else:
            game_index += 1

    ## DUMP
    #for b_index in range(len(l_Battles)):
    #    print "["+str(b_index)+"] "+l_Battles[b_index].str_dump(True)
# ==============================================================================
def battle_events( battle, player_name ):
    """
    Find all battle event with that given player.
    """
    
    pass
# ==============================================================================                                    
def parse_start( line, index, data):
    """
    - ======= Start gameplay 'Sentinel' map 's8256_thar_threshold', local client team 2 =======
    - ======= Start PVE mission 'asteroid_building_t3' map 's1550_pve_asteroid_building' =======
    """
    start = pa.search( "gameplay '{game:w}' map '{map}', local client team {team:d} =======", line)
    if start == None:
        start = pa.search( "PVE mission '{game:w}' map '{map}' =======", line)
        if start == None:
            print "START\n",line
        else:
            data.append( start['game'] )
            data.append( start['map'] )
            data.append( '-' )
    else:
        data.append( start['game'] )
        data.append( start['map'] )
        data.append( start['team'] )
    index +=1
    return index    
def parse_end( line, index, data):
    """
    - Gameplay finished. Winner team: 1(ALL_ENEMY_SHIPS_KILLED). Finish reason: 'All SpaceShips destroyed'. Actual game time 406.8 se
    - Gameplay finished. Winner team: 2. Finish reason: 'unknown'. Actual game time 338.8 sec
    """
    end = pa.search( "- Gameplay finished. Winner team: {team:d}({type:w}). Finish reason: '{reason}'. Actual game time {time:f} sec", line)
    if end == None:
        end = pa.search( "- Gameplay finished. Winner team: {team:d}. Finish reason: '{reason}'. Actual game time {time:f} sec", line)
    if end == None:
        print "END\n",line
    else:
        data.append(index)
        data.append(end['team'])
        data.append(end['time'])
        data.append(end['reason'])
    index += 1
    return index 
def parse_kill( line, index, kill):
    """
    Lit qui tue qui et continue tant qu'il y a des assists.
    Renvoie la première ligne qui n'est pas un assist.
    - Killed Rhoard -> rochok;	 totalDamage 5377.57; Weapon_Laser_Economic_T3_Mk3
    - Killed bitsbytes -> Expendable_BasicGuidedDron_T3_Mk3(bitsbytes);	 totalDamage 1530.00; (suicide) <FriendlyFire>
    -   Assisted Mordanius assisted to Rhoard -> rochok;	 totalDamage 7441.04; Weapon_Railgun_Basic_T3_Rare <buff> <debuff>
    """
    player = pa.search( 'Killed {killer} -> {dead};', line)
    if player == None:
        print "KILL PLAYER\n",line
        sys.exit(0)
        index +=1
        return index
    dmg = pa.search ('totalDamage {dom:f}; {weapon:w}', line)
    if dmg == None:
        dmg = pa.search ('totalDamage {dom:f}; ({weapon})', line)
        if dmg == None:
            dmg = pa.search ('totalDamage {dom:f};', line)
            if dmg == None:
                print "KILL DMG\n",line
                print "     player=",player
                sys.exit(0)
            else:
                dmg.named['weapon'] = '-'
    # print player," = ",dmg
    #print player['killer']," KILLED ",player['dead'],", (",dmg['dom']," with ",dmg['weapon'],")"
    kill.append(index)
    kill.append(player['killer'])
    kill.append(player['dead'])
    kill.append(dmg['dom'])
    kill.append(dmg['weapon'])
    # Cherche les assists
    index += 1
    line = lines[index]
    while (re.search('Assisted', line)) : 
        assist = pa.search( 'Assisted {player} assisted', line)
        ass_dmg = pa.search( 'totalDamage {dom:f}; {weapon:w}', line)
        if ass_dmg == None :
            ass_dmg = {'dom':0, 'weapon':'-'}
        ass_debuf = pa.search( '<{debuf}>', line)
        if ass_debuf == None:
            help = [assist['player'], ass_dmg['dom'], ass_dmg['weapon'], None]
        else:
            help = [assist['player'], ass_dmg['dom'], ass_dmg['weapon'], ass_debuf['debuf']]
        kill.append(help)
        # print "assist >> ",assist, " = ",ass_dmg," [",ass_debuf,"]"
        # msg = "   ASSIST by "+str(assist['player'])+" ("+str(ass_dmg['dom'])+" with "+str(ass_dmg['weapon'])
        # if ass_debuf:
        #     msg += " ["+str(ass_debuf)+"]"
        # print msg
        index += 1
        line = lines[index]
    return index
def parse_spawn( line, index, spawn):
    """
    Lit qui spawn dans quel vaisseau.
    """
    sp = pa.search( "Spawn SpaceShip for player{num:d} ({player}, #{id}). '{ship}'", line)
    #pl = pa.search( '({player:w}, #', line )
    #sh = pa.search( "'{ship}'", line )
    # print "player=",pl," ship=",sh
    # print "SPAWN of ",pl['player']," in ",sh['ship']
    if sp == None :
        print "SPAWN\n",line
        sys.exit(1)
    spawn.append(index)
    spawn.append(sp['player'])
    spawn.append(sp['ship'])
    index += 1
    return index
def parse_capture( line, index, capt):
    """
    Lit qui capture quoi.
    capt = (index,id_team,what)
    """
    evt = pa.search( "Captured '{what}'(team {id_team:d}).", line)
    atk = pa.search( "Attackers: {atk}\n", line)
    if atk == None:
        print "CAPTURE\n",line
        sys.exit(1)
    attackers = atk['atk'].split(' ');
    # print "CAPTURE\n",line
    # print "       =",evt
    # print "       =",atk
    capt.append(index)
    capt.append(evt['id_team'])
    capt.append(evt['what'])
    for a in attackers:
        capt.append(a)
    # msg = "CAPTURE of "+str(evt['what'])+" by "
    # for player in attackers:
    #     msg += str(player)+" "
    # print msg
    index += 1
    return index
def parse_dmg( line, index, evt):
    """
    Lit qui endommage qui.
    """
    #print "DAMAGE\n",line
    dmg = pa.search( "- Damage{d1:s}{player} ->{d2:s}{target}{d3:s}{val:f} {weapon:w} {type:w}-{which:w}", line)#|{crit:w}", line)
    if dmg == None:
        dmg = pa.search( "- Damage{d1:s}{player} ->{d2:s}{target}({whom:w}){d3:s}{val:f} {weapon:w} {type:w}-{which:w}", line)#|{crit:w}", line)
        if dmg == None:
            dmg = pa.search( "- Damage{d1:s}{player} ->{d2:s}{target}{d3:s}{val:f} {weapon:w} {type:w}", line)#|{crit:w}", line)
            if dmg == None:
                dmg = pa.search( "- Damage{d1:s}{player} ->{d2:s}{target}{d3:s}{val:f} ({weapon:w}) {type:w}-{which:w}", line)#|{crit:w}", line)
                if dmg == None:
                    dmg = pa.search( "- Damage{d1:s}n/a ->{d2:s}{target}{d3:s}{val:f} ({weapon:w}) {type:w}-{which:w}", line)#|{crit:w}", line)
                    if dmg == None:
                        dmg = pa.search( "- Damage{d1:s}n/a ->{d2:s}{target}{d3:s}{val:f} {weapon:w} {type:w}-{which:w}", line)#|{crit:w}", line)                        
                        if dmg == None:
                            dmg = pa.search( "- Damage{d1:s}{player} ->{d2:s}{target}({whom:w}){d3:s}{val:f} {weapon:w} {type:w}", line)
                            if dmg == None:
                                print "DMG\n",line
                                sys.exit(0)
                            else:
                                dmg.named['which'] = "-"
                        else:
                            dmg.named['player'] = "n/a"
                            dmg.named['whom'] = "-"
                    else:
                        dmg.named['player'] = "n/a"
                        dmg.named['whom'] = "-"
                else:
                    dmg.named['whom'] = "-"
            else:
                dmg.named['whom'] = "-"
                dmg.named['which'] = "-"
        else:
            dmg.named['whom'] = "-"
            dmg.named['which'] = "-"
    else:
        dmg.named['whom'] = "-"
    dmg.named['whom'] = "-"
    evt.append(index)
    evt.append(dmg['player'])
    evt.append(dmg['weapon'])
    evt.append(dmg['val'])
    evt.append(dmg['type'])
    evt.append(dmg['target'])
    evt.append(dmg['whom'])
    evt.append(dmg['which']) 
    #        
    crit = False
    if re.search( '-CRIT', line):
        #print "      CRIT=",re.search( '-CRIT',line)
        crit = True
    evt.append(crit)
    expl = False
    if re.search( '-EXPLOSION', line):
        expl = True
    evt.append(expl)
    # print "      =",dmg
    # print "      =C",crit," E",expl
    # line = logfile.readline()
    # return line
    index += 1
    return index
def parse_heal( line, index, heal_evt ):
    """
    heal_evt = (index, player, target, val, module)
    Lit Heal
    - Heal              Kyuzo ->            Kyuzo 311.03 Module_ShieldRestoreMedium_T3_Rare
    - Heal                n/a ->            SMok3   5.00
    """
    heal = pa.search( "- Heal{d1:s}{player} ->{d2:s}{target}{d3:s}{val:f} {module:w}", line)
    if heal == None:
        heal = pa.search( "- Heal{d1:s}n/a ->{d2:s}{target}{d3:s}{val:f}", line)
        if heal == None:
            heal = pa.search( "- Heal{d1:s}n/a ->{d2:s}n/a{d3:s}{val:f}", line)
            if heal == None:
                print "HEAL\n",line
                sys.exit(1)
            else:
                heal.named['player'] = "-"
                heal.named['target'] = "-"
                heal.named['module'] = "-"
        else:
            heal.named['player'] = "-"
            heal.named['module'] = "-"
    
    heal_evt.append(index)
    heal_evt.append(heal['player'])
    heal_evt.append(heal['target'])
    heal_evt.append(heal['val'])
    heal_evt.append(heal['module'])
    
    index += 1
    return index
def parse_spell( line, index, spell_evt ):
    """
    spell_evt = [index,spell,player,module,nb_target,targets]
    
    - Spell 'ShieldVampire_T3_Rare' by Metabaron(Module_ShieldVampire_T3_Rare) targets(1): rochok
    - Spell 'BombCarrier' by zertul targets(1): zertul
    - Spell 'SpaceMissile_Ion_T3_Mk3_spl' by Mordanius(SpaceMissile_Ion_T3_Mk3) targets(0):
    - Spell 'PhaseShield_Phase0' by n/a(Module_PhaseShield_T2_Base) targets(1): n/a
    """
    spell = pa.search( "- Spell '{spell:w}' by {player}({module:w}) targets({d1:d}):{d2:s}{targets}\n", line)
    if spell == None:
        spell = pa.search( "- Spell '{spell:w}' by {player} targets({d1:d}):{d2:s}{targets}\n", line)
        if spell == None:
            spell = pa.search( "- Spell '{spell:w}' by {player}({module:w}) targets(0):", line)
            if spell == None:
                spell = pa.search( "- Spell '{spell:w}' by n/a({module:w}) targets(1): n/a", line)
                if spell == None:
                    print "SPELL\n",line
                    sys.exit(1)
                else:
                    spell.named['d1'] = 1
                    spell.named['targets'] = "-"
                    spell.named['player'] = "-"
            else:
                spell.named['d1'] = 0
                spell.named['targets'] = "-"
        else:
            spell.named['module'] = "-"
    
    spell_evt.append(index)
    spell_evt.append(spell['spell'])
    spell_evt.append(spell['player'])
    spell_evt.append(spell['module'])
    spell_evt.append(spell['d1'])
    spell_evt.append(spell['targets'])
    
    index += 1
    return index
def parse_apply( line, index, apply_evt):
    """
    apply_evt = [index,aura,id,module,target]
    - Apply aura 'CommandArmorResist_T3_Epic' id 36 type AURA_HULL_RESIST_ALL to 'rafa'
    """
    aura = pa.search( "- Apply aura '{aura:w}' id {id:d} type {module:w} to '{target}'", line)
    if aura == None:
        print "APPLY AURA\n",line
        sys.exit(1)
        
        
    apply_evt.append(index)
    apply_evt.append(aura['aura'])
    apply_evt.append(aura['id'])
    apply_evt.append(aura['module'])
    apply_evt.append(aura['target'])
    
    index += 1
    return index
def parse_cancel( line, index, cancel_evt):
    """
    cancel_evt = [index,aura,id,target]
    
    - Cancel aura 'CommandShieldResist_T3_Epic' id 35 type AURA_SHIELD_RESIST_ALL from 'Spitfire'
    """
    aura = pa.search( "- Cancel aura '{aura:w}' id {id:d} type {module:w} from '{target}'", line)
    if aura == None:
        print "CANCEL AURA\n",line
        sys.exit(1)

    cancel_evt.append(index)
    cancel_evt.append(aura['aura'])
    cancel_evt.append(aura['id'])
    cancel_evt.append(aura['target'])

    index += 1
    return index
    
# =================================================================== PlayerStat
class PlayerStat(object):
    """
    self._dmg : tot damage given
    self._wounds : monitor wounds (+dmg, -heal)
    """
    def __init__(self, name):
        self._player = name
        self._dmg_atk = [0,0,0,0] 
        self._dmg_def = [0,0,0,0] 
        self._wounds = []
        self._l_ships = []
        self._ship = None
    def spawn(self, ship):
        if self._ship != None:
            self._dmg_atk = np.add(self._dmg_atk, self._ship._dmg_atk)
            self._dmg_def = np.add(self._dmg_def, self._ship._dmg_def)
        self._ship = ShipStat( ship )
        self._l_ships.append( self._ship )
    def end_battle(self):
        if self._ship != None:
            self._dmg_atk = np.add(self._dmg_atk, self._ship._dmg_atk)
            self._dmg_def = np.add(self._dmg_def, self._ship._dmg_def)
    def str_detailed(self):
        res = ""
        for ship in self._l_ships:
            res += ship.str_detailed()
            res += '\n'
        res += "  TOTAL = "
        res += "ATK TH:{0:.0f} EMP:{1:.0f} CIN:{2:.0f} ??:{3:.0f}".format(*self._dmg_atk)
        res += "   DEF TH:{0:.0f} EMP:{1:.0f} CIN:{2:.0f} ??:{3:.0f}".format(*self._dmg_def)
        return res
class ShipStat(object):
    """
    self._dmg : tot damage given
    self._wounds : monitor wounds (+dmg, -heal)
    """
    def __init__(self, ship):
        self._ship = ship
        self._dmg_atk = [0,0,0,0]
        self._dmg_def = [0,0,0,0]
        self._wounds = []
        self._l_modules = []
    def str_detailed(self):
        res = ""
        res += "  {0} ".format(self._ship)
        res += "ATK TH:{0:.0f} EMP:{1:.0f} CIN:{2:.0f} ??:{3:.0f}".format(*self._dmg_atk)
        res += "   DEF TH:{0:.0f} EMP:{1:.0f} CIN:{2:.0f} ??:{3:.0f}".format(*self._dmg_def)
        res += "\n     Module="+str(self._l_modules)
        return res
# =============================================================== Analyse Battle
def analyse_battle( battle , verb_spawn=False, verb_dmg=False, verb_kill=False):
    """
    Spawn => new ship dans joueur.
    Test sur nb kills
    """
    #~ nb_max_kill = 5
    th,emp,cin,other = 0,1,2,3
    d_players = {}
    for e in battle._l_events:
        if isinstance(e, Spawn):
            if verb_spawn:
                print e.str_dump()
            # crée player si besoin
            if not d_players.has_key( e._player ):
                d_players[e._player] = PlayerStat(e._player)
            d_players[e._player].spawn(e._ship_game)
        elif isinstance(e, Dmg):
            if verb_dmg:
                print e.str_dump()
            if d_players.has_key(e._player):
                ship_atk = d_players[e._player]._ship
                if e._type == "THERMAL":    
                    ship_atk._dmg_atk[th] += e._val
                elif e._type == "EMP":
                    ship_atk._dmg_atk[emp] += e._val
                elif e._type == "KINETIC":
                    ship_atk._dmg_atk[cin] += e._val
                elif e._type == "TRUE_DAMAGE":
                    ship_atk._dmg_atk[other] += e._val
                else:
                    print "UNKNOWN DMG TYPE ",e._type
                    print "           ",e.str_dump()
            if d_players.has_key(e._target):
                ship_def = d_players[e._target]._ship
                if e._type == "THERMAL":    
                    ship_def._dmg_def[th] += e._val
                elif e._type == "EMP":
                    ship_def._dmg_def[emp] += e._val
                elif e._type == "KINETIC":
                    ship_def._dmg_def[cin] += e._val
                elif e._type == "TRUE_DAMAGE":
                    ship_def._dmg_def[other] += e._val
                else:
                    print "UNKNOWN DMG TYPE ",e._type
                    print "           ",e.str_dump()
                if verb_dmg:
                    print "TD dmg=",ship_def._dmg_def[other]
                    print "SHIP_DEF=",ship_def.str_detailed()
        elif isinstance(e, Kill):
            if verb_kill:
                print e.str_dump()
            #~ nb_max_kill -= 1
            #~ if nb_max_kill < 0:
                #~ break
        elif isinstance(e, Spell):
            # who played that spell ?
            if d_players.has_key(e._player):
                ship = d_players[e._player]._ship
                # Already "owned" by ship+player
                if e._module <> "-" and e._module not in ship._l_modules:
                    ship._l_modules.append(e._module)
                #~ elif e._module == '-':
                    #~ print e.str_dump()
    #
    # Make sur ships leave battle
    for key,val in d_players.iteritems():
        val.end_battle()
        print "** {0} **".format(key)
        print val.str_detailed()
    #
    # Pourcentage pour équipe 1
    team1_dmg_atk = [0,0,0,0]
    team1_dmg_def = [0,0,0,0]
    res = "TEAM1 : "
    for player in battle._l_players1:
        res += player+", "
        team1_dmg_atk = np.add( team1_dmg_atk, d_players[player]._dmg_atk )
        team1_dmg_def = np.add( team1_dmg_def, d_players[player]._dmg_def )
    print res
    team1_sum_atk = np.sum( team1_dmg_atk )
    team1_sum_def = np.sum( team1_dmg_def )
    res = "ATK TOT={0:2.0f}".format( team1_sum_atk )
    res += " TH:{0:.0f} EMP:{1:.0f} CIN:{2:.0f} ??:{3:.0f}".format(*team1_dmg_atk)
    res += " || DEF TOT={0:.0f}".format( team1_sum_def )
    res += " TH:{0:.0f} EMP:{1:.0f} CIN:{2:.0f} ??:{3:.0f}".format(*team1_dmg_def)
    print res
    for player in battle._l_players1:
        res = "{0:15}".format(player)
        ratio = np.divide( d_players[player]._dmg_atk, team1_dmg_atk) * 100.0
        player_sum_atk = np.sum( d_players[player]._dmg_atk )
        res += "\tATK TOT={0:4.1f}%".format(player_sum_atk/team1_sum_atk*100.0)
        res += " TH:{0:2.0f}% EMP:{1:2.0f}% CIN:{2:2.0f}% ??:{3:2.0f}%".format(*ratio)
        player_sum_def = np.sum( d_players[player]._dmg_def )
        ratio = np.divide( d_players[player]._dmg_def, team1_dmg_def) * 100.0
        res += "\tDEF TOT={0:4.1f}%".format(player_sum_def/team1_sum_def*100.0)
        res += " TH:{0:2.0f}% EMP:{1:2.0f}% CIN:{2:2.0f}% ??:{3:2.0f}%".format(*ratio)
        print res
    # Pourcentage pour équipe 2
    team2_dmg_atk = [0,0,0,0]
    team2_dmg_def = [0,0,0,0]
    res = "TEAM2 : "
    for player in battle._l_players2:
        res += player+", "
        team2_dmg_atk = np.add( team2_dmg_atk, d_players[player]._dmg_atk )
        team2_dmg_def = np.add( team2_dmg_def, d_players[player]._dmg_def )
    print res
    team2_sum_atk = np.sum( team2_dmg_atk )
    team2_sum_def = np.sum( team2_dmg_def )
    res = "ATK TOT={0:.0f}".format( team2_sum_atk )
    res += " TH:{0:.0f} EMP:{1:.0f} CIN:{2:.0f} ??:{3:.0f}".format(*team2_dmg_atk)
    res += " || DEF TOT={0:.0f}".format( team2_sum_def )
    res += " TH:{0:.0f} EMP:{1:.0f} CIN:{2:.0f} ??:{3:.0f}".format(*team2_dmg_def)
    print res
    for player in battle._l_players2:
        res = "{0:15}".format(player)
        ratio = np.divide( d_players[player]._dmg_atk, team2_dmg_atk) * 100.0
        player_sum_atk = np.sum( d_players[player]._dmg_atk )
        res += "\tATK TOT={0:4.1f}%".format(player_sum_atk/team2_sum_atk*100.0)
        res += " TH:{0:2.0f}% EMP:{1:2.0f}% CIN:{2:2.0f}% ??:{3:2.0f}%".format(*ratio)
        player_sum_def = np.sum( d_players[player]._dmg_def )
        ratio = np.divide( d_players[player]._dmg_def, team2_dmg_def) * 100.0
        res += "\tDEF TOT={0:4.1f}%".format(player_sum_def/team2_sum_def*100.0)
        res += " TH:{0:2.0f}% EMP:{1:2.0f}% CIN:{2:2.0f}% ??:{3:2.0f}%".format(*ratio)
        print res
# =============================================================== Analyse Player
def analyse_kills( battle, player):
    """
    Pour l'instant, fait stat sur un joueur d'une Battle
    """
    th,emp,cin,other = 0,1,2,3
    dmg = [0,0,0,0]
    dmg_tot = [0,0,0,0]
    shield = 0
    hull = 1
    heal = [0,0]
    heal_tot = [0,0]
    # Dommages reçus
    for e in battle._l_events:
        if isinstance(e, Dmg):
            if e._target == player:
                if e._type == "THERMAL":
                    dmg[th] += e._val
                elif e._type == "EMP":
                    dmg[emp] += e._val
                elif e._type == "KINETIC":
                    dmg[cin] += e._val
                elif e._type == "TRUE_DAMAGE":
                    dmg[other] += e._val
                else:
                    print "UNKNOWN DMG TYPE ",e._type
                    print "           ",e.str_dump()
        elif isinstance(e, Heal):
            if e._target == player:
                #print e.str_dump()
                h1,heal_type,h3,h4 = decode_heal( e._module )
                if heal_type == 'SHIELD':
                    heal[shield] += e._val
                elif heal_type == 'HULL':
                    heal[hull] += e._val
                elif heal_type == 'SHIELD/HULL':
                    heal[hull] += e._val
                    heal[shield] += e._val
                else:
                    print "UNKNOWN HEAL TYPE ",heal_type
                    print "            ",e.str_dump()
        elif isinstance(e, Kill):
            if e._target == player:
                print player+" WAS KILL WITH DMG="+str(dmg)+" HEAL="+str(heal)
                print "TOT=",np.sum(dmg)-np.sum(heal)
                dmg_tot = np.add( dmg_tot, dmg)
                heal_tot = np.add( heal_tot, heal)
                print e.str_dump()
                dmg = [0,0,0,0]
                heal = [0,0]
    # Print
    print "DMG=",dmg_tot
    print "HEAL=",heal_tot
                
# =============================================================== Detect Weapons    
def detect_unknown_weapon( battle ):
    """
    Regarde tous les KILL et DMG faits et répertorie les armes inconnues.
    Propose de les ajouter à d_weapon (avec print console à coller)
    """
    for evt in battle._l_events:
        if isinstance(evt, Kill):
            decode_weapon( evt._weapon )
        elif isinstance(evt, Dmg):
            decode_weapon( evt._weapon )
    print "d_weapon = {"
    for k,v in d_weapon.iteritems():
        print "'"+k+"':'"+v+"',"
    print "}"
def decode_weapon( log_name ):
    """
    Returns : game_name,T,Mk xor None
    """
    gun = pa.search( '{name}_T{tier:d}_{mk:w}', log_name )
    if gun == None:
        return None
    else:
        # print "GUN=",gun
        try:
            gun_name = d_weapon[gun['name']]
            gun_mk = d_mk[gun['mk']]
            return gun_name,gun['tier'],gun_mk
        except KeyError:
            print "log_name=",log_name
            d_weapon[gun['name']] = '---'
            print "UNKNOWN =","'"+gun['name']+"':'???',"
            return None
# ========================================================== Detect Heal Modules
def detect_unknown_heal( battle ):
    """
    Reagarde tous les HEAL et répertorie les modules inconnus.
    Propose de les ajouter à d_heal_module (avec print console à coller)
    """
    for evt in battle._l_events:
        if isinstance(evt, Heal):
            decode_heal( evt._module )
    print "d_heal_module = {"
    for k,v in d_heal_module.iteritems():
        print "'"+k+"':"+str(v)+","
    print "}"
def decode_heal( log_name ):
    """
    Returns : game_name,type(SHIELD/ULL) xor None
    """
    module = pa.search( '{name}_T{tier:d}_{mk:w}', log_name )
    if module == None:
        return None
    else:
        # print "HEAL_MODULE=",module
        try:
            module_name = d_heal_module[module['name']][0]
            module_mk = d_mk[module['mk']]
            module_type = d_heal_module[module['name']][1]
            return module_name,module_type,module['tier'],module_mk
        except KeyError:
            print "log_name=",log_name
            d_heal_module[module['name']] = ['---','SHIELD/HULL']
            print "UNKNOWN =","'"+module['name']+"':'???',"
            return None
def decode_ship( ship ):
    pass
def decode_module( module ):
    pass
    
def interface():
    pass

if __name__ == '__main__':
    # NEW WAYS : combat and game log
    # read_combatgame( '0112_combat_v3.log', '0112_game_v3.log')
    read_combatgame( '0112_combat_b0.log', '0112_game_b0.log')
    # DUMP
    for b_index in range(len(l_Battles)):
        print "["+str(b_index)+"] "+l_Battles[b_index].str_dump(True)
    print "******** BATTLE 0 *********\n"
    print l_Battles[0].str_dump(False)
    #~ for e in l_Battles[0]._l_events:
        #~ print e.str_dump(False)
    #~ detect_unknown_weapon(l_Battles[0])
    #~ detect_unknown_heal( l_Battles[0] )
    #~ analyse_kills( l_Battles[0], 'Chalain' )
    analyse_battle( l_Battles[0], verb_spawn=False, verb_dmg=False, verb_kill=False)
    # OLD WAYS
    #read_log( 'combat_1204_v1.log' )
    #read_log( 'combat_1205_v3.log' )
    #print dump_battles()
    # print dump_kills( battles[0] )
    # print dump_spawns( battles[0] )
    #print dump_captures( battles[3] )
    # print dump_damages( battles[3] )
    #print dump_heal( battles[3] )
    #print dump_spell( battles[2] )
    #print dump_apply( battles[3] )
    #print dump_cancel( battles[3] )
    #prep_log( 'combat_1205_v3.log.ori', 'test.log')
