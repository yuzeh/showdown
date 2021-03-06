import constants

from showdown.calculate_damage import is_super_effective


def choiceband(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def choicespecs(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.SPECIAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def lifeorb(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.3
        attacking_move[constants.HEAL] = [-1, 10]
        attacking_move[constants.HEAL_TARGET] = constants.SELF
    return attacking_move


def expertbelt(attacking_move, attacking_pokemon, defending_pokemon):
    if is_super_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


item_lookup = {
    'choiceband': choiceband,
    'choicespecs': choicespecs,
    'lifeorb': lifeorb,
    'expertbelt': expertbelt
}


def item_modify_attack_being_used(item_name, attacking_move, attacking_pokemon, defending_pokemon):
    item_func = item_lookup.get(item_name)
    if item_func is not None:
        return item_func(attacking_move, attacking_pokemon, defending_pokemon)
    else:
        return attacking_move
