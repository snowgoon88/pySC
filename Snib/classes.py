#!/usr/bin/python
# -*- coding: utf-8 -*-

import data_snib

# *********************************************************************** Battle
class Battle:
    # [[start,id,type,map,team,end,winner,time,reason]
    # --------------------------------------------------------------------------
    def __init__(self,id):
        self._id = id
        self._l_players1 = []
        self._l_players2 = []
        self._l_events = []
    # --------------------------------------------------------------------------
    def set(self,start,end,type,map,team,winner,time,reason):
        self._start = start
        self._end = end
        self._type = type
        self._map = map
        self._team = team
        self._winner = winner
        self._time = time
        self._reason = reason
    # --------------------------------------------------------------------------
    def str_head():
        pass
    # --------------------------------------------------------------------------
    def str_dump(self, verb=False):
        ds = ""
        ds += "Bataille id="+str(self._id)
        ds += " type="+self._type+" map="+self._map
        ds += " team="+str(self._team)+" win=team"+str(self._winner)
        ds += " time="+str(self._time)+"s cause="+self._reason+"\n"
        if verb:
            ds += "DEBUG de "+str(self._start)+" à "+str(self._end)+" id="+str(self._id)+"\n"
        ds += " TEAM1="+str(self._l_players1)+"\n"
        ds += " TEAM2="+str(self._l_players2)+"\n"
        ds += " "+str(len(self._l_events))+" events"
        return ds
# ************************************************************************ Spawn
class Spawn:
    # [index,player,ship]
    # --------------------------------------------------------------------------
    def __init__(self,index,player,ship_log):
        self._index = index
        self._player = player
        self._ship_log = ship_log
        try:
            self._ship_game = data_snib.d_ships[ship_log]
        except KeyError:
            self._ship_game = "UNKNOWN ("+ship_log+")"
    # --------------------------------------------------------------------------
    def str_dump(self, verb=False):
        ds = ""
        ds += "SPAWN of "+self._player+" on a "+self._ship_game
        if verb:
            ds += "\nDEBUG at "+str(self._index)+" ship="+self._ship_log+"\n"
        return ds
# ************************************************************************* Kill
class Kill:
    # [index,killer,target,dmg,weapon,[assister,dmg,weapon,None|debuf]...]
    # --------------------------------------------------------------------------
    def __init__(self,index,killer,target,dmg,weapon):
        self._index = index
        self._killer = killer
        self._target = target
        self._dmg = dmg
        self._weapon = weapon
        self._assist = []
    # --------------------------------------------------------------------------
    def str_dump(self, verb=False):
        ds = ""
        ds += "KILL  by "+self._killer+" of "+self._target+" with "+self._weapon+" ("+str(self._dmg)+")"
        if verb:
            ds += "\nDEBUG at "+str(self._index)
        for a in self._assist:
            ds += "\n    ASSIST by "+a[0]+" with "+a[2]+" ("+str(a[1])+") "+str(a[3])
        return ds
# ********************************************************************** Capture
class Capture:
    # [index,team_nb,what,attackers,...] !!!! team_nb = 0 !!!!
    # --------------------------------------------------------------------------
    def __init__(self,index,team,what):
        self._index = index
        self._team = team
        self._what = what
        self._attackers = []
    # --------------------------------------------------------------------------
    def str_dump(self, verb=False):
        ds = ""
        ds += "CAPT of "+self._what+" for team "+str(self._team)
        if verb:
            ds += "\nDEBUG at "+str(self._index)
        for a in self._attackers:
            ds += "\n    ATTACKERS : "+a
        return ds
# ************************************************************************** Dmg
class Dmg:
    # [index,player,weapon,val,type,target,whom,which,crit,explosion]
    # --------------------------------------------------------------------------
    def __init__(self,index,player,weapon,val,type,target,whom,which,crit,expl):
        self._index = index
        self._player = player
        self._weapon = weapon
        self._val = val
        self._type = type
        self._target = target
        self._whom = whom
        self._which = which
        self._crit = crit
        self._expl = expl
    # --------------------------------------------------------------------------
    def str_dump(self, verb=False):
        ds = ""
        ds += "DMG  by "+self._player+" with "+self._weapon+" ["+self._which+"]"
        ds += " on "+self._target+"("+self._whom+") for "+str(self._val)+" "+self._type
        ds += " (crit="+str(self._crit)+" expl="+str(self._expl)+")"
        if verb:
            ds += "\nDEBUG at "+str(self._index)
        return ds
# ************************************************************************* Heal
class Heal:
    # [index, player, target, val, module]
    # --------------------------------------------------------------------------
    def __init__(self,index,player,target,val,module):
        self._index = index
        self._player = player
        self._target = target
        self._val = val
        self._module = module
    # --------------------------------------------------------------------------
    def str_dump(self, verb=False):
        ds = ""
        ds += "HEAL  of "+self._target+" "+str(self._val)+" by "+self._player
        ds += " with "+self._module
        if verb:
            ds += "\nDEBUG at "+str(self._index)
        return ds
# ************************************************************************ Spell
class Spell:
    # [index,spell,player,module,nb_targets,targets]
    # --------------------------------------------------------------------------
    def __init__(self,index,spell,player,module):
        self._index = index
        self._spell = spell
        self._player = player
        self._module = module
        self._target = "-"
    # --------------------------------------------------------------------------
    def str_dump(self, verb=False):
        ds = ""
        ds += "SPELL "+self._spell+" by "+self._player+" for "+self._module+" on "+self._target
        if verb:
            ds += "\nDEBUG at "+str(self._index)
        return ds
# ************************************************************************ Apply
class Apply:
    # [index,aura,id,module,target]
    # --------------------------------------------------------------------------
    def __init__(self,index,aura,id,module,target):
        self._index = index
        self._aura = aura
        self._id = id
        self._module = module
        self._target = target
    # --------------------------------------------------------------------------
    def str_dump(self, verb=False):
        ds = ""
        ds += "APPLY "+self._aura+" from "+self._module+" on "+self._target
        if verb:
            ds += "\nDEBUG at "+str(self._index)
        return ds
# *********************************************************************** Cancel
class Cancel:
    # [index,aura,id,target]
    # --------------------------------------------------------------------------
    def __init__(self,index,aura,id,target):
        self._index = index
        self._aura = aura
        self._id = id
        self._target = target
    # --------------------------------------------------------------------------
    def str_dump(self, verb=False):
        ds = ""
        ds += "STOP  "+self._aura+" on "+self._target
        if verb:
            ds += "\nDEBUG at "+str(self._index)
        return ds
# ******************************************************************************