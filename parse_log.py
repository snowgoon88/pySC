#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
## regular expression
import re

from session import *

# ******************************************************************************
# *********************************************************************** GLOBAL
_cur_session = None
_pending_event = None
_all_sessions = []

class Param:
    def __init__(self):
        self.verb = False
        self.debug = True
_param = Param()

# ***************************************************************** path_to_text
def path_to_text( pathname ):
    infile = open( pathname )
    file_text = infile.read()

    return file_text
# ******************************************************************** readlines
def read_lines( pathname ):
    with open( pathname ) as fp:
        count = 0
        for line in fp:
        #for i in range(12032):
            #line = fp.next()
            # print( line )
            try:
                count += 1
                parse_line( line )
            except Exception as e:
                print( "EE_{}:".format(count)+line )
                print traceback.format_exc()
                sys.exit()


def parse_line( line ):
    global _cur_session, _all_sessions
    ## New session
    session_id = re.search( "game\ssession\s\d+", line )
    if session_id is not None:
        _cur_session = Session( id = int(session_id.group()[13:] ))
        _all_sessions.append( _cur_session )
        print( "__NEW Session : id={}".format( _cur_session.id ))
        return

    ## Spawn
    spawn_cmd = re.search( "Spawn SpaceShip for player\d+\s\(\w+,\s#\d+\)\.\s'.*'", line )
    if spawn_cmd is not None:
        look_for_player( spawn_cmd.group() )
        return

    ## Damage
    dmg_cmd = re.search( "\|\sDamage\s+", line )
    if dmg_cmd is not None:
        look_in_dmg( line )
        return

    ## Heal
    heal_cmd = re.search( "\|\sHeal\s+", line )
    if heal_cmd is not None:
        look_in_heal( line )
        return

    ## Spell
    spell_cmd = re.search( "\|\sSpell\s+", line )
    if spell_cmd is not None:
        look_in_spell( line )
        return

    ## Secondary
    second_cmd = re.search( "\|\sSecondary weapon\s+", line )
    if second_cmd is not None:
        look_in_secondary( line )
        return
    
    ignore_patterns = [ "\|\sReward\s+",
                        "\|\sCancel\s+",
                        "\|\s+Participant\s+",
                        "\|\sKilled\s+",
                        "\|\sRocket\s+",
                        "\|\sApply aura\s+",
                        "\|\sSet stage\s+",
                        "\|\sUncaptured\s+",
                        "\|\sTeleporting\s+",
                        "\|\sAddStack\s+",
                        "\|\sCaptured\s+",
                        "\|\sScores\s+",
                        "\|\sGameplay\sfinished.\s+",
                        "Start\sgameplay"
                        

    ]
    for pat in ignore_patterns:
        pat_re = re.search( pat, line )
        if pat_re is not None:
            return

    if _param.verb or _param.verb :
        print( "**"+line[20:] )
    

    

# ******************************************************************************
# ********************************************************************* look_for
# ******************************************************************************
# ************************************************************* look_for_session
def look_for_session( reg_txt ):
    """ Return character position for Session in a region_txt """
    session_l = []
    ## Parse to fin sessions
    session_re = re.compile( "Connect")
    all_session = re.finditer( session_re, reg_txt )
    
    session_pos = [s.start() for s in all_session]
    session_pos.append( len(reg_txt)-1 )
    
    print( session_pos )
    for start,end in zip(session_pos[:-1],session_pos[1:]):
        print( "__***** Session ({}, {}) *****".format( start, end ))
        session_id = re.search( "session\s\d+", reg_txt[start:end] )
        print( "  id={}".format( session_id.group()[8:] ) )
        session_l.append( Session( id=int(session_id.group()[8:]),
                                   reg_txt = reg_txt[start:end] ) )
    
    return session_l

# ************************************************************** look_for_player
def look_for_player( spawn_cmd ):
    """
    Return : [Player]
    """
    global _pending_event
    player_name = re.search( "\(\w+,", spawn_cmd )
    player_name = player_name.group()[1:-1]
    # print( "  Name={}".format( player_name) )
    player_id = re.search( "#\w+\)", spawn_cmd )
    player_id = player_id.group()[:-1]
    # print( "  ID={}".format( player_id ))
    player_ship = re.search( "'.*'", spawn_cmd )
    player_ship =  player_ship.group()[1:-1]
    # print( "  Ship={}".format( player_ship ))
    player_num = re.search( "player\d+", spawn_cmd )
    player_num = player_num.group()[6:]
    # print( "  num={}".format( player_num ))

    new_player = _cur_session.get_player( player_id )
    if new_player is None:
        new_player = Player( player_name,
                             player_id,
                             int(player_num) )
        _cur_session.add_player( new_player )

    new_player.add_ship( Ship(player_ship) )
    if _pending_event is not None and _pending_event.player_name == player_name:
        new_player.cur_ship.add_bonus( _pending_event.spellname )
        _pending_event = None

# ****************************************************************** look_in_dmg
def look_in_dmg( dmg_cmd ):
    """
    Look for Weapon, Missile, Modules
    """
    # ignore (crash), ...ShipExplode..., (suicide)
    # TODO : des fois, (suicide) permet de savoir qu'il y avait une battestation
    #        ou des SentryDrone
    ignore_patterns = [ "\(crash\)",
                        "\(suicide\)",
                        "ShipExplode" ]
    for pat in ignore_patterns:
        pat_re = re.search( pat, dmg_cmd )
        if pat_re is not None:
            return
    
    attacker_name = re.search( "Damage\s+\w+\|", dmg_cmd)
    if attacker_name is not None:
        attacker_name = attacker_name.group()[6:-1]
        attacker_name = attacker_name.strip()

        ## ignore
        if attacker_name == 'GuardDrone_RC':
            return
        if attacker_name == 'n/a':
            return

    weapon_patterns = [ "Weapon\w+\s",
                        "Turret\w+\s",
                        "Drone_Destr\w+\s",
                        "BlastWave\w+\s"]
    for pat in weapon_patterns:
        weapon_name = re.search( pat, dmg_cmd )
        if weapon_name is not None:
            weapon_name = weapon_name.group()[:-1]
            # print( "="+str(attacker_name)+" : "+weapon_name )
            player = _cur_session.get_player_name( attacker_name )
            if player is not None:
                player.cur_ship.add_primary_weapon( weapon_name )
                return
        
    module_name = re.search( "Module\w+\s", dmg_cmd )
    if module_name is not None:
        module_name = module_name.group()[:-1]
        # print( "="+str(attacker_name)+" : "+module_name )
        player = _cur_session.get_player_name( attacker_name )
        if player is not None:
            player.cur_ship.add_module( module_name )
            return

    missile_name = re.search( "SpaceMissile\w+\s", dmg_cmd )
    if missile_name is not None:
        missile_name = missile_name.group()[:-1]
        # print( "="+str(attacker_name)+" : "+missile_name )
        player = _cur_session.get_player_name( attacker_name )
        if player is not None:
            player.cur_ship.add_missile( missile_name )
            return
    
    if _param.verb :
        print( dmg_cmd[21:] )

# ***************************************************************** look_in_heal
def look_in_heal( heal_cmd ):
    """
    Look for Module, Weapon
    """

    healer_name = re.search( "Heal\s+\w+\|", heal_cmd)
    if healer_name is not None:
        healer_name = healer_name.group()[6:-1]
        healer_name = healer_name.strip()

        # ## ignore
        # if healer_name == 'GuardDrone_RC':
        #     return
        # if healer_name == 'n/a':
        #     return

    module_name = re.search( "Module\w+", heal_cmd )
    if module_name is not None:
        module_name = module_name.group()
        # print( "="+str(attacker_name)+" : "+module_name )
        player = _cur_session.get_player_name( healer_name )
        if player is not None:
            player.cur_ship.add_module( module_name )
            return

    weapon_patterns = [ "Weapon\w+",
                        ]
    for pat in weapon_patterns:
        weapon_name = re.search( pat, heal_cmd )
        if weapon_name is not None:
            weapon_name = weapon_name.group()
            # print( "="+str(attacker_name)+" : "+weapon_name )
            player = _cur_session.get_player_name( healer_name )
            if player is not None:
                player.cur_ship.add_primary_weapon( weapon_name )
                return

    if _param.verb : 
        print( "__HEAL" )
        print( heal_cmd[21:] )

# **************************************************************** look_in_spell
def look_in_spell( spell_cmd ):
    """
    Look for Module, Weapon
    """
    global _pending_event
    ignore_patterns = [ "SpawnWarpInvulnerability",
    ]
    for pat in ignore_patterns:
        pat_re = re.search( pat, spell_cmd )
        if pat_re is not None:
            return

    speller_name = re.search( "by\s\w+\(", spell_cmd)
    if speller_name is not None:
        speller_name = speller_name.group()[3:-1]
        speller_name = speller_name.strip()

        # ## ignore
        # if speller_name == 'GuardDrone_RC':
        #     return
        # if speller_name == 'n/a':
        #     return

    module_patterns = [ "\(Module\w+\)", "\(Platform\w+\)" ]    
    for pat in module_patterns:
        module_name =  re.search( pat, spell_cmd )
        if module_name is not None:
            module_name = module_name.group()[1:-1]
            # print( "="+str(attacker_name)+" : "+module_name )
            player = _cur_session.get_player_name( speller_name )
            if player is not None:
                player.cur_ship.add_module( module_name )
                # print( "++SPELL {} : {}".format( speller_name, module_name ))
                return

    weapon_patterns = [ "Weapon\w+",
                        "SpaceMissile\w+"]
    for pat in weapon_patterns:
        weapon_name = re.search( pat, spell_cmd )
        if weapon_name is not None:
            weapon_name = weapon_name.group()
            # print( "="+str(attacker_name)+" : "+weapon_name )
            player = _cur_session.get_player_name( speller_name )
            if player is not None:
                player.cur_ship.add_primary_weapon( weapon_name )
                return

    bonus_name = re.search( "\(Bonus\w+\)", spell_cmd )
    if bonus_name is not None:
        bonus_name = bonus_name.group()[1:-1]
        # print( "="+str(attacker_name)+" : "+bonus_name )
        player = _cur_session.get_player_name( speller_name )
        if player is not None:
            player.cur_ship.add_bonus( bonus_name )
            # print( "++SPELL {} : {}".format( speller_name, bonus_name ))
            return

    # bonus at beginning
    speller_name = re.search( "by\s\w+\s", spell_cmd)
    if speller_name is not None:
        speller_name = speller_name.group()[3:-1]
        speller_name = speller_name.strip()
    debug_msg = ""
    bonus_patterns = [ "'Rank\w+'",
                       "'Talent\w+'",
                       "'Test\w+'",
                        ]
    for pat in bonus_patterns:
        bonus_name = re.search( pat, spell_cmd )
        debug_msg += pat+":"
        if bonus_name is not None:
            bonus_name = bonus_name.group()[1:-1]
            debug_msg += bonus_name
            # print( "="+str(attacker_name)+" : "+bonus_name )
            player = _cur_session.get_player_name( speller_name )
            if player is not None:
                player.cur_ship.add_bonus( bonus_name )
                # print( "++SPELL {} : {}".format( speller_name, bonus_name ))
                return
            elif pat == bonus_patterns[0]: ## Rank
                # pending event
                _pending_event = PendingEvent( speller_name, bonus_name )
                return
        debug_msg += " / "

    if _param.verb :
        print( "__SPELL by -{}-".format( speller_name ) )
        print( "      debug "+debug_msg )
        print( spell_cmd[21:] )


# ************************************************************ look_in_secondary
def look_in_secondary( second_cmd ):
    """
    Look for Mines
    """
    attacker_name = re.search( "owner '\w+'", second_cmd)
    if attacker_name is not None:
        attacker_name = attacker_name.group()[7:-1]
        attacker_name = attacker_name.strip()

    weapon_patterns = [ "def\s'SpaceMissile\w+'",
                        "def\s'ProximityMine\w+'",
    ]
    for pat in weapon_patterns:
        weapon_name = re.search( pat, second_cmd )
        if weapon_name is not None:
            weapon_name = weapon_name.group()[5:-1]
            # print( "="+str(attacker_name)+" : "+weapon_name )
            player = _cur_session.get_player_name( attacker_name )
            if player is not None:
                player.cur_ship.add_missile( weapon_name )
                return

    if _param.verb :
        print( "__SECOND by -{}-".format( attacker_name ) )
        print( second_cmd[21:] )

# *********************************************************** list_unknown_ships
def list_unknown_ships( session ):
    for player in session.players.itervalues():
        for ship in player.ships.itervalues():
            if ship.get_realname().startswith( '???' ):
                print( ship.to_str() )
def list_all_ships( session ):
    for player in session.players.itervalues():
        print( player.name )
        for ship in player.ships.itervalues():
            print( "  "+ship.gamename+" : "+ship.get_fullname() )
# ******************************************************************************
# ************************************************************************* Main
# ******************************************************************************
if __name__ == '__main__':
    if len( sys.argv ) < 2:
        print( "Utilisation : "+sys.argv[0]+" fichier_log" )
    else:
        read_lines( sys.argv[1] )

    print( "******** ALL SESSIONS = {} ********".format( len(_all_sessions) ))

    sess = _all_sessions[0]
    print( "__SESSION ******************************" )
    print( sess.to_str() )
    print( "***************** UKN *******************" )
    list_unknown_ships( sess )
    sys.exit()
    
    print( "******** LAST SESSION *********" )
    print( _cur_session.to_str() )

    print( "******** Uknown Ships ****" )
    list_unknown_ships( _cur_session )

    # print( "******** All Ships *******" )
    # list_all_ships( _cur_session )

    
        # file_txt = path_to_text( sys.argv[1] )
        # print( "******** ALL SESSIONS ********" )
        # session_list = look_for_session( file_txt )
        # for session in session_list:
        #     print( session.to_str() )
        #     # print( session.reg_txt )
            
        #     # look_for_player( session )
        #     #print( session.to_str() )
            
        # for start,end in zip(session_list[:-1],session_list[1:]):
        #     print( "__***** Session ({}, {}) *****".format( start, end ))
        #     player_list = look_for_player( file_txt[start:end] )
        #     for p in player_list:
        #         print( p.to_str() )
        #     print( "" )

