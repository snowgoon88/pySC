#!/usr/bin/python
# -*- coding: utf-8 -*-

from data_snib import *

class Session:
    def __init__(self, id, type="PvP"):
        self.id = id
        self.type = type
        self.players = {}

    def to_str(self):
        msg = "Session {} : {}".format( self.id, self.type )
        for p in self.players.itervalues():
            msg += "\n"+p.to_str()

        return msg

    def add_player(self, player ):
        if not player.id in self.players:
            self.players[player.id] = player
    def get_player(self, player_id ):
        if player_id in self.players:
            return self.players[player_id]
        else:
            return None
    def get_player_name(self, name):
        for player in self.players.itervalues():
            if player.name == name:
                return player
        return None

class Player:
    def __init__(self, name, id, num):
        self.name = name
        self.id = id
        self.num = num
        self.ships = {}
        self.cur_ship = None

    def to_str(self):
        msg = "{} [{}] as player{} with {}".format( self.name, self.id,
                                                    str(self.num),
                                                    self.cur_ship.gamename)
        for ship in self.ships.itervalues():
            msg += "\n  "+ship.to_str()
        
        return msg

    def add_ship(self, ship ):
        if not ship.gamename in self.ships:
            self.ships[ship.gamename] = ship
        self.cur_ship = ship
    def get_ship(self, gamename ):
        if gamename in self.ships:
            return self.ships[gamename]
        else:
            return None
    
class Ship:
    def __init__(self, gamename):
        self.gamename = gamename
        self.weapons = {}
        self.missiles = {}
        self.modules = {}
        self.bonuses = {}
        self.parse_gamename()

    def to_str(self):
        msg = "  "+self.gamename+" => "+self.get_realname()
        msg += " ("+self.race+" "+self.size+")"
        for wep in self.weapons.itervalues():
            msg += "\n"+wep.to_str()
        for mis in self.missiles.itervalues():
            msg += "\n"+mis.to_str()
        for mod in self.modules.itervalues():
            msg += "\n"+mod.to_str()
        for bon in self.bonuses.itervalues():
            msg += "\n"+bon.to_str()
            
        return msg

    def get_realname(self):
        if self.gamename in d_ships:
            return d_ships[self.gamename]
        else:
            return "???"

    def get_fullname(self):
        return self.get_realname()+" ("+self.race+" "+self.size+")"

    def parse_gamename(self):
        tokens = self.gamename.split( '_' )
        race = tokens[1]
        if race != 'PresetE':
            self.race = d_race[tokens[1]]
            self.size = d_size[tokens[2]]
        else:
            self.race = d_race[tokens[2]]
            self.size = d_size[tokens[3]]
            self.gamename = 'NPC Ship'


    def add_primary_weapon(self, gamename ):
        if gamename not in self.weapons:
            self.weapons[gamename] = Weapon( gamename )

    def add_missile(self, gamename ):
        if gamename not in self.missiles:
            self.missiles[gamename] = Missile( gamename )

    def add_module(self, gamename):
        if gamename not in self.modules:
            self.modules[gamename] = Module( gamename )

    def add_bonus(self, gamename):
        if gamename not in self.bonuses:
            self.bonuses[gamename] = Bonus( gamename )
    
class Weapon:
    def __init__(self, gamename):
        self.gamename = gamename

    def to_str(self):
        msg = "      PW: "+self.gamename

        return msg

class Missile:
    def __init__(self, gamename):
        self.gamename = gamename

    def to_str(self):
        msg = "      MIS: "+self.gamename

        return msg

class Module:
    def __init__(self, gamename):
        self.gamename = gamename

    def to_str(self):
        msg = "      MOD: "+self.gamename

        return msg

class Bonus:
    def __init__(self, gamename):
        self.gamename = gamename

    def to_str(self):
        msg = "      BON: "+self.gamename

        return msg

class PendingEvent:
    def __init__(self, player_name, spell_name):
        self.player_name = player_name
        self.spellname = spell_name



