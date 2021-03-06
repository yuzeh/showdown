import unittest
import constants
from showdown.search.instruction_generator import InstructionGenerator
from showdown.state.pokemon import Pokemon as StatePokemon
from showdown.search.state_mutator import StateMutator
from showdown.search.objects import State
from showdown.search.objects import Side
from showdown.search.objects import Pokemon
from showdown.search.transpose_instruction import TransposeInstruction
from collections import defaultdict


class TestGetInstructionsFromFlinched(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instructions = TransposeInstruction(1, [], False)

    def test_flinch_sets_state_to_frozen_and_returns_one_state(self):
        defender = constants.SELF

        self.state.self.active.volatile_status.add(constants.FLINCH)
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_flinched(mutator, defender, self.previous_instructions)

        flinch_instruction = (
            constants.MUTATOR_REMOVE_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )

        expected_instructions = [
            TransposeInstruction(1.0, [flinch_instruction], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_flinch_being_false_does_not_freeze_the_state(self):
        defender = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_flinched(mutator, defender, self.previous_instructions)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromConditionsThatFreezeState(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.move = {constants.FLAGS: dict()}

    def test_paralyzed_attacker_results_in_two_instructions(self):
        attacker = constants.OPPONENT
        defender = constants.SELF
        self.state.opponent.active.status = constants.PARALYZED
        previous_instruction = TransposeInstruction(1.0, [], False)

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(1 - constants.FULLY_PARALYZED_PERCENT, [], False),
            TransposeInstruction(constants.FULLY_PARALYZED_PERCENT, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_attacker_results_in_two_instructions(self):
        attacker = constants.OPPONENT
        defender = constants.SELF
        self.state.opponent.active.status = constants.FROZEN
        previous_instruction = TransposeInstruction(1.0, [], False)

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(constants.THAW_PERCENT, [], False),
            TransposeInstruction(1 - constants.THAW_PERCENT, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_asleep_attacker_results_in_two_instructions(self):
        attacker = constants.OPPONENT
        defender = constants.SELF
        self.state.opponent.active.status = constants.SLEEP
        previous_instruction = TransposeInstruction(1.0, [], False)

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(constants.WAKE_UP_PERCENT, [], False),
            TransposeInstruction(1 - constants.WAKE_UP_PERCENT, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_powder_move_on_grass_type_does_nothing_and_freezes_the_state(self):
        attacker = constants.OPPONENT
        defender = constants.SELF
        self.state.self.active.types = ['grass']
        previous_instruction = TransposeInstruction(1.0, [], False)
        move = {
            constants.FLAGS: {
                constants.POWDER: 1
            }
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_powder_move_used_by_asleep_pokemon_produces_correct_states(self):
        attacker = constants.OPPONENT
        defender = constants.SELF
        self.state.opponent.active.status = constants.SLEEP
        self.state.self.active.types = ['grass']
        previous_instruction = TransposeInstruction(1.0, [], False)
        move = {
            constants.FLAGS: {
                constants.POWDER: 1
            }
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(constants.WAKE_UP_PERCENT, [], True),
            TransposeInstruction(1-constants.WAKE_UP_PERCENT, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_powder_against_fire_has_no_effect(self):
        attacker = constants.OPPONENT
        defender = constants.SELF
        self.state.self.active.types = ['fire']
        previous_instruction = TransposeInstruction(1.0, [], False)
        move = {
            constants.FLAGS: {
                constants.POWDER: 1
            }
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromDamage(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_100_percent_move_returns_one_state(self):
        defender = constants.SELF
        damage = 50
        accuracy = 100

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, None, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            50
        )

        expected_instructions = [
            TransposeInstruction(1.0, [mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_move_with_drain_heals_the_attacker(self):
        defender = constants.SELF
        damage = 50
        accuracy = 100

        # start the attacker with 10 HP
        self.state.opponent.active.hp = 10

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, [1, 2], None, None, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            defender,
            50
        )

        drain_instruction = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            25
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, drain_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_move_with_recoil_hurts_the_attacker(self):
        defender = constants.SELF
        damage = 50
        accuracy = 100

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, [1, 2], None, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            defender,
            50
        )

        drain_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            25
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, drain_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_95_percent_move_with_crash_hurts_the_attacker(self):
        defender = constants.SELF
        damage = 50
        accuracy = 95

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, [1, 2], self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            defender,
            50
        )

        crash_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            self.state.opponent.active.maxhp / 2
        )

        expected_instructions = [
            TransposeInstruction(0.95, [damage_instruction], False),
            TransposeInstruction(0.050000000000000044, [crash_instruction], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_move_that_does_no_damage_hurts_the_attacker(self):
        defender = constants.SELF
        damage = 0
        accuracy = 100

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, [1, 2], self.previous_instruction)

        crash_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            self.state.opponent.active.maxhp / 2
        )

        expected_instructions = [
            TransposeInstruction(1, [crash_instruction], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_95_percent_move_with_no_damage_causes_crash(self):
        defender = constants.SELF
        damage = 0
        accuracy = 95

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, [1, 2], self.previous_instruction)

        crash_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            self.state.opponent.active.maxhp / 2
        )

        expected_instructions = [
            TransposeInstruction(1, [crash_instruction], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_0_damage_move_with_50_accuracy_returns_one_state_that_is_frozen(self):
        defender = constants.SELF
        damage = 0
        accuracy = 50

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, None, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_killing_move_doesnt_drop_health_below_zero(self):
        defender = constants.SELF
        damage = 1000
        accuracy = 100

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, None, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            self.state.self.active.maxhp
        )

        expected_instructions = [
            TransposeInstruction(1.0, [mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_50_percent_move_returns_two_states_with_proper_percentages(self):
        defender = constants.SELF
        damage = 50
        accuracy = 50

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, None, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            damage
        )

        expected_instructions = [
            TransposeInstruction(0.5, [mutator_instructions], False),
            TransposeInstruction(0.5, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_75_percent_move_returns_two_states_with_proper_percentages(self):
        defender = constants.SELF
        damage = 50
        accuracy = 75

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, None, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            damage
        )

        expected_instructions = [
            TransposeInstruction(0.75, [mutator_instructions], False),
            TransposeInstruction(0.25, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_0_percent_move_returns_one_state_with_no_changes(self):
        defender = constants.SELF
        damage = 50
        accuracy = 0

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, None, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_move_returns_one_state_when_state_percentage_already_existed(self):
        defender = constants.SELF
        damage = 50
        accuracy = 100

        # pre-set the previous percentage to ensure it is updated properly
        self.previous_instruction.percentage = 0.5

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, None, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            damage
        )

        expected_instructions = [
            TransposeInstruction(0.5, [mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_state_does_not_change(self):
        defender = constants.SELF
        damage = 50
        accuracy = 100

        # a frozen state usually has a percentage, though for testing it doesn't matter
        self.previous_instruction.percentage = 0.1
        self.previous_instruction.frozen = True

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_damage(mutator, defender, damage, accuracy, None, None, None, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(0.1, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromSideConditions(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_using_stealthrock_sets_side_condition(self):
        side_string = constants.OPPONENT
        condition = constants.STEALTH_ROCK

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_side_conditions(mutator, constants.SELF, side_string, condition, self.previous_instruction)

        expected_mutator_instructions = (
            constants.MUTATOR_SIDE_START,
            side_string,
            condition,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [expected_mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_using_spikes_sets_side_condition(self):
        side_string = constants.OPPONENT
        condition = constants.SPIKES

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_side_conditions(mutator, constants.SELF, side_string, condition, self.previous_instruction)

        expected_mutator_instructions = (
            constants.MUTATOR_SIDE_START,
            side_string,
            condition,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [expected_mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_spikes_can_have_more_than_one(self):
        side_string = constants.OPPONENT
        condition = constants.SPIKES

        self.state.opponent.side_conditions[constants.SPIKES] = 1

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_side_conditions(mutator, constants.SELF, side_string, condition, self.previous_instruction)

        expected_mutator_instructions = (
            constants.MUTATOR_SIDE_START,
            side_string,
            condition,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [expected_mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_spikes_stops_at_3(self):
        side_string = constants.OPPONENT
        condition = constants.SPIKES

        self.state.opponent.side_conditions[constants.SPIKES] = 3

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_side_conditions(mutator, constants.SELF, side_string, condition, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_using_stealthrock_into_side_already_containing_stealthrock_does_nothing(self):
        side_string = constants.OPPONENT
        condition = constants.STEALTH_ROCK

        self.state.opponent.side_conditions[constants.STEALTH_ROCK] = 1

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_side_conditions(mutator, constants.SELF, side_string, condition, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromHazardClearingMoves(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_rapidspin_clears_stealthrocks(self):
        attacker_string = constants.SELF
        self.state.self.side_conditions[constants.STEALTH_ROCK] = 1

        move = {
            constants.ID: 'rapidspin'
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, self.previous_instruction)

        expected_mutator_instructions = [(
            constants.MUTATOR_SIDE_END,
            attacker_string,
            constants.STEALTH_ROCK,
            1
        )]

        expected_instructions = [
            TransposeInstruction(1.0, expected_mutator_instructions, False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_rapidspin_clears_stealthrocks_and_spikes(self):
        attacker_string = constants.SELF
        self.state.self.side_conditions[constants.STEALTH_ROCK] = 1
        self.state.self.side_conditions[constants.SPIKES] = 3

        move = {
            constants.ID: 'rapidspin'
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, self.previous_instruction)

        expected_mutator_instructions = [
            (
                constants.MUTATOR_SIDE_END,
                attacker_string,
                constants.STEALTH_ROCK,
                1
            ),
            (
                constants.MUTATOR_SIDE_END,
                attacker_string,
                constants.SPIKES,
                3
            ),
        ]

        expected_instructions = [
            TransposeInstruction(1.0, expected_mutator_instructions, False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_defog_clears_both_sides_side_conditions(self):
        attacker_string = constants.SELF
        defender_string = constants.OPPONENT
        self.state.self.side_conditions[constants.STEALTH_ROCK] = 1
        self.state.self.side_conditions[constants.SPIKES] = 3
        self.state.opponent.side_conditions[constants.STEALTH_ROCK] = 1
        self.state.opponent.side_conditions[constants.SPIKES] = 1
        self.state.opponent.side_conditions[constants.REFLECT] = 1

        move = {
            constants.ID: 'defog'
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, self.previous_instruction)

        expected_mutator_instructions = [
            (
                constants.MUTATOR_SIDE_END,
                attacker_string,
                constants.STEALTH_ROCK,
                1
            ),
            (
                constants.MUTATOR_SIDE_END,
                attacker_string,
                constants.SPIKES,
                3
            ),
            (
                constants.MUTATOR_SIDE_END,
                defender_string,
                constants.STEALTH_ROCK,
                1
            ),
            (
                constants.MUTATOR_SIDE_END,
                defender_string,
                constants.SPIKES,
                1
            ),
            (
                constants.MUTATOR_SIDE_END,
                defender_string,
                constants.REFLECT,
                1
            )
        ]

        expected_instructions = [
            TransposeInstruction(1.0, expected_mutator_instructions, False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_rapidspin_does_not_clear_reflect(self):
        attacker_string = constants.SELF
        defender_string = constants.OPPONENT
        self.state.self.side_conditions[constants.REFLECT] = 1

        move = {
            constants.ID: 'rapidspin'
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, self.previous_instruction)

        expected_mutator_instructions = []

        expected_instructions = [
            TransposeInstruction(1.0, expected_mutator_instructions, False)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromDirectStatusEffects(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                {
                    "rattata": Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    "charmander": Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    "squirtle": Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    "bulbasaur": Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    "pidgey": Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                },
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_100_percent_status_returns_one_state(self):
        status = constants.BURN
        accuracy = 100
        defender = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_APPLY_STATUS,
            defender,
            status
        )

        expected_instructions = [
            TransposeInstruction(1.0, [mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_status_cannot_be_inflicted_on_pkmn_in_substitute(self):
        self.state.self.active.volatile_status.add(constants.SUBSTITUTE)
        status = constants.BURN
        accuracy = 100
        defender = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_75_percent_status_returns_two_states(self):
        status = constants.BURN
        accuracy = 75
        defender = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_APPLY_STATUS,
            defender,
            status
        )

        expected_instructions = [
            TransposeInstruction(0.75, [mutator_instructions], False),
            TransposeInstruction(0.25, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_pokemon_cannot_be_burned(self):
        status = constants.BURN
        accuracy = 100
        defender = constants.SELF

        # set 'frozen' in the defender's active statuses
        self.state.self.active.status = constants.FROZEN

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_sleep_clause_activates(self):
        status = constants.SLEEP
        accuracy = 100
        defender = constants.SELF

        self.state.self.reserve['rattata'].status = constants.SLEEP

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_poison_type_cannot_be_poisoned(self):
        status = constants.POISON
        accuracy = 100
        defender = constants.SELF

        self.state.self.active.types = ['poison']

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switching_in_pokemon_cannot_be_statused_if_it_is_already_statused(self):
        status = constants.POISON
        accuracy = 100
        defender = constants.SELF

        self.state.self.reserve['rattata'].status = constants.PARALYZED

        switch_instruction = (
            constants.MUTATOR_SWITCH,
            constants.SELF,
            'pikachu',
            'rattata'
        )
        self.previous_instruction.instructions = [
            switch_instruction
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(
                1.0,
                [switch_instruction],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_steel_type_cannot_be_poisoned(self):
        status = constants.POISON
        accuracy = 100
        defender = constants.SELF

        self.state.self.active.types = ['steel']

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_state_cannot_be_changed(self):
        status = constants.BURN
        accuracy = 100
        defender = constants.SELF

        # freeze the state
        self.previous_instruction.frozen = True

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromBoosts(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_no_boosts_results_in_one_unchanged_state(self):
        boosts = {}
        accuracy = True
        side = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_boosts_cannot_exceed_max_boosts(self):
        self.state.self.active.attack_boost = 6
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = True
        side = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            0
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_boosts_cannot_go_below_min_boosts(self):
        self.state.self.active.attack_boost =  -1*constants.MAX_BOOSTS
        boosts = {
            constants.ATTACK: -1
        }
        accuracy = True
        side = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            0
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_guaranteed_atk_boost_returns_one_state(self):
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = True
        side = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_50_percent_boost_returns_two_states(self):
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = 50
        side = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )

        expected_instructions = [
            TransposeInstruction(0.5, [boost_instruction], False),
            TransposeInstruction(0.5, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_guaranteed_atk_boost_returns_one_state_when_attack_boost_already_existed(self):
        self.state.self.active.attack_boost = 1
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = True
        side = constants.SELF

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_pre_existing_boost_does_not_affect_new_boost(self):
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = True
        side = constants.SELF

        self.state.self.active.defense_boost = 1
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_multiple_new_boosts_with_multiple_pre_existing_boosts(self):
        boosts = {
            constants.ATTACK: 1,
            constants.DEFENSE: 1
        }
        accuracy = True
        side = constants.SELF

        self.state.self.active.defense_boost = 1
        self.state.self.active.speed_boost = 1
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_states_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        attack_boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )
        defense_boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.DEFENSE,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [attack_boost_instruction, defense_boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromFlinchingMoves(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_30_percent_flinching_move_returns_two_states(self):
        accuracy = 30
        defender = constants.SELF

        instructions = self.state_generator.get_states_from_flinching_moves(defender, accuracy, True, self.previous_instruction)

        flinched_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )

        expected_instructions = [
            TransposeInstruction(0.3, [flinched_instruction], False),
            TransposeInstruction(0.7, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_flinching_move_returns_one_state(self):
        accuracy = 100
        defender = constants.SELF

        instructions = self.state_generator.get_states_from_flinching_moves(defender, accuracy, True, self.previous_instruction)

        flinched_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )

        expected_instructions = [
            TransposeInstruction(1.0, [flinched_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_0_percent_flinching_move_returns_one_state(self):
        accuracy = 0
        defender = constants.SELF

        instructions = self.state_generator.get_states_from_flinching_moves(defender, accuracy, True, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_pre_exising_percentage_propagates_downward(self):
        accuracy = 30
        defender = constants.SELF

        self.previous_instruction.percentage = 0.5
        instructions = self.state_generator.get_states_from_flinching_moves(defender, accuracy, True, self.previous_instruction)

        flinched_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )

        expected_instructions = [
            TransposeInstruction(0.15, [flinched_instruction], False),
            TransposeInstruction(0.35, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetStateFromSwitch(unittest.TestCase):
    def setUp(self):

        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                {
                    "rattata": Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    "charmander": Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    "squirtle": Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    "bulbasaur": Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    "pidgey": Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                },
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                {
                    "rattata": Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    "charmander": Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    "squirtle": Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    "bulbasaur": Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    "pidgey": Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                },
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_basic_switch_with_no_side_effects(self):
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        expected_instructions = [TransposeInstruction(1, [
            (
                constants.MUTATOR_SWITCH,
                attacker,
                self.state.self.active.id,
                switch_pokemon_name
            ),
        ], False)]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_unboosts_active_pokemon(self):
        self.state.self.active.attack_boost = 3
        self.state.self.active.defense_boost = 2
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        expected_instructions = [TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_UNBOOST,
                    attacker,
                    constants.ATTACK,
                    3
                ),
                (
                    constants.MUTATOR_UNBOOST,
                    attacker,
                    constants.DEFENSE,
                    2
                ),
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.self.active.id,
                    switch_pokemon_name
                ),
            ],
            False
        )]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_stealth_rock_gives_damage_instruction(self):
        self.state.self.side_conditions[constants.STEALTH_ROCK] = 1
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                    (
                        constants.MUTATOR_DAMAGE,
                        attacker,
                        27.75  # 1/8th of rattata's 222 maxhp is 27.75 damage
                    ),
                ]
        ,
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_toxicspikes_causes_poison(self):
        self.state.self.side_conditions[constants.TOXIC_SPIKES] = 1
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                    (
                        constants.MUTATOR_APPLY_STATUS,
                        attacker,
                        constants.POISON,
                    ),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_poison_switch_into_toxicspikes_clears_the_spikes(self):
        self.state.self.side_conditions[constants.TOXIC_SPIKES] = 1
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        self.state.self.reserve[switch_pokemon_name].types = ['poison']

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                    (
                        constants.MUTATOR_SIDE_END,
                        attacker,
                        constants.TOXIC_SPIKES,
                        1
                    ),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_poison_switch_into_two_toxicspikes_clears_the_spikes(self):
        self.state.self.side_conditions[constants.TOXIC_SPIKES] = 2
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        self.state.self.reserve[switch_pokemon_name].types = ['poison']

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                    (
                        constants.MUTATOR_SIDE_END,
                        attacker,
                        constants.TOXIC_SPIKES,
                        2
                    ),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_flying_poison_doesnt_clear_toxic_spikes(self):
        self.state.self.side_conditions[constants.TOXIC_SPIKES] = 2
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        self.state.self.reserve[switch_pokemon_name].types = ['poison', 'flying']

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_double_toxicspikes_causes_toxic(self):
        self.state.self.side_conditions[constants.TOXIC_SPIKES] = 2
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                    (
                        constants.MUTATOR_APPLY_STATUS,
                        attacker,
                        constants.TOXIC,
                    ),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_flying_immune_to_toxicspikes(self):
        self.state.self.side_conditions[constants.TOXIC_SPIKES] = 2
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        self.state.self.reserve[switch_pokemon_name].types = ['flying']

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_stick_web_drops_speed(self):
        self.state.self.side_conditions[constants.STICKY_WEB] = 1
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                    (
                        constants.MUTATOR_UNBOOST,
                        attacker,
                        constants.SPEED,
                        1
                    ),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_levitate_ability_does_not_cause_sticky_web_effect(self):
        self.state.self.side_conditions[constants.STICKY_WEB] = 1
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        self.state.self.reserve[switch_pokemon_name].ability = 'levitate'

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_airballoon_item_does_not_cause_sticky_web_effect(self):
        self.state.self.side_conditions[constants.STICKY_WEB] = 1
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        self.state.self.reserve[switch_pokemon_name].item = 'airballoon'

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_flying_switch_into_sticky_web_does_not_drop_speed(self):
        self.state.self.side_conditions[constants.STICKY_WEB] = 1
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        self.state.self.reserve[switch_pokemon_name].types = ['flying']

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'pikachu', 'rattata'),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_stealth_rock_with_1hp_gives_damage_instruction_of_1hp(self):
        self.state.self.side_conditions[constants.STEALTH_ROCK] = 1
        self.state.self.reserve["rattata"].hp = 1
        attacker = constants.SELF
        switch_pokemon_name = "rattata"

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (
                        constants.MUTATOR_SWITCH,
                        attacker,
                        self.state.self.active.id,
                        switch_pokemon_name
                    ),
                    (
                        constants.MUTATOR_DAMAGE,
                        attacker,
                        1
                    ),
                ],
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_stealth_rock_as_flying_does_more_damage(self):
        self.state.self.side_conditions[constants.STEALTH_ROCK] = 1
        attacker = constants.SELF
        switch_pokemon_name = "pidgey"

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (
                        constants.MUTATOR_SWITCH,
                        attacker,
                        self.state.self.active.id,
                        switch_pokemon_name
                    ),
                    (
                        constants.MUTATOR_DAMAGE,
                        attacker,
                        60.5  # 1/4 of pidgey's 242 max hp is 60.5
                    ),
                ]
                ,
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_three_spikes_as_flying_does_nothing(self):
        self.state.self.side_conditions[constants.SPIKES] = 3
        attacker = constants.SELF
        switch_pokemon_name = "pidgey"

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (
                        constants.MUTATOR_SWITCH,
                        attacker,
                        self.state.self.active.id,
                        switch_pokemon_name
                    )
                ]
                ,
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_volatile_status_is_removed_on_switch_out(self):
        self.state.self.active.volatile_status = {"leechseed"}
        attacker = constants.SELF
        switch_pokemon_name = "pidgey"

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (
                        constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                        constants.SELF,
                        "leechseed"
                    ),
                    (
                        constants.MUTATOR_SWITCH,
                        attacker,
                        self.state.self.active.id,
                        switch_pokemon_name
                    )
                ]
                ,
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_count_is_reset_if_it_exists_on_switch_out(self):
        self.state.self.side_conditions[constants.TOXIC_COUNT] = 2
        attacker = constants.SELF
        switch_pokemon_name = "pidgey"

        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (
                        constants.MUTATOR_SIDE_END,
                        constants.SELF,
                        constants.TOXIC_COUNT,
                        2
                    ),
                    (
                        constants.MUTATOR_SWITCH,
                        attacker,
                        self.state.self.active.id,
                        switch_pokemon_name
                    )
                ]
                ,
                False
            )
        ]

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)


class TestGetStateFromHealingMoves(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_returns_one_state_with_health_recovered(self):
        self.state.self.active.hp = 50  # this ensures the entire 1/3 * maxhp is in the instruction
        attacker = constants.SELF
        move = {
            constants.TARGET: constants.SELF,
            constants.HEAL: [1, 3],
            constants.HEAL_TARGET: constants.SELF
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        heal_instruction = (
            constants.MUTATOR_HEAL,
            attacker,
            1/3 * self.state.self.active.maxhp
        )

        expected_instructions = [
            TransposeInstruction(1.0, [heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_healing_does_not_exceed_max_health(self):
        self.state.self.active.hp = self.state.self.active.maxhp
        attacker = constants.SELF
        move = {
            constants.TARGET: constants.SELF,
            constants.HEAL: [1, 1],
            constants.HEAL_TARGET: constants.SELF
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        heal_instruction = (
            constants.MUTATOR_HEAL,
            attacker,
            0
        )

        expected_instructions = [
            TransposeInstruction(1.0, [heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_negative_healing(self):
        attacker = constants.SELF
        move = {
            constants.TARGET: constants.NORMAL,
            constants.HEAL: [-1, 2],
            constants.HEAL_TARGET: constants.SELF
        }

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        heal_instruction = (
            constants.MUTATOR_HEAL,
            constants.SELF,
            -1 / 2 * self.state.opponent.active.maxhp
        )

        expected_instructions = [
            TransposeInstruction(1.0, [heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_state_does_not_change(self):
        attacker = constants.SELF
        move = {
            constants.TARGET: constants.SELF,
            constants.HEAL: [1, 3],
            constants.HEAL_TARGET: constants.SELF
        }

        self.previous_instruction.frozen = True

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetStateFromVolatileStatus(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_returns_one_state_with_volatile_status_set(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_volatile_status(mutator, volatile_status, attacker, target, self.previous_instruction)

        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.SELF,
            volatile_status
        )

        expected_instructions = [
            TransposeInstruction(1.0, [instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_state_is_unaffected(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        self.previous_instruction.frozen = True

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_volatile_status(mutator, volatile_status, attacker, target, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_does_not_alter_pre_existing_volatile_status(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        self.state.self.active.volatile_status.add('confusion')

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_volatile_status(mutator, volatile_status, attacker, target, self.previous_instruction)

        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.SELF,
            volatile_status
        )

        expected_instructions = [
            TransposeInstruction(1.0, [instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_does_not_apply_duplicate_status(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        self.state.self.active.volatile_status.add(volatile_status)

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_volatile_status(mutator, volatile_status, attacker, target, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_does_not_apply_status_if_substitute_is_active_on_pokemon(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        self.state.self.active.volatile_status.add('substitute')

        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_volatile_status(mutator, volatile_status, attacker, target, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetStateFromStatusDamage(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False
        )
        self.state_generator = InstructionGenerator()
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_poison_does_one_eigth_damage(self):
        side = constants.SELF
        self.state.self.active.status = constants.POISON
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_status_damage(mutator, side, self.previous_instruction)

        instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            self.state.self.active.maxhp * 0.125
        )

        expected_instructions = [
            TransposeInstruction(1.0, [instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_does_one_sixteenth_damage_when_toxic_count_is_zero_and_gives_toxic_count_instruction(self):
        side = constants.SELF
        self.state.self.active.status = constants.TOXIC
        self.state.self.side_conditions[constants.TOXIC_COUNT] = 0
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_status_damage(mutator, side, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            int(self.state.self.active.maxhp / 16)
        )

        toxic_count_instruction = (
            constants.MUTATOR_SIDE_START,
            side,
            constants.TOXIC_COUNT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [toxic_count_instruction, damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_does_one_eighth_damage_when_toxic_count_is_one_and_gives_toxic_count_instruction(self):
        side = constants.SELF
        self.state.self.active.status = constants.TOXIC
        self.state.self.side_conditions[constants.TOXIC_COUNT] = 1
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_status_damage(mutator, side, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            int(self.state.self.active.maxhp / 8)
        )

        toxic_count_instruction = (
            constants.MUTATOR_SIDE_START,
            side,
            constants.TOXIC_COUNT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [toxic_count_instruction, damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_does_one_quarter_damage_when_toxic_count_is_3_and_gives_toxic_count_instruction(self):
        side = constants.SELF
        self.state.self.active.status = constants.TOXIC
        self.state.self.side_conditions[constants.TOXIC_COUNT] = 3
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_status_damage(mutator, side, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            int(self.state.self.active.maxhp / 4)
        )

        toxic_count_instruction = (
            constants.MUTATOR_SIDE_START,
            side,
            constants.TOXIC_COUNT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [toxic_count_instruction, damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_poison_only_does_one_damage_if_that_is_all_it_has(self):
        side = constants.SELF
        self.state.self.active.status = constants.POISON
        self.state.self.active.hp = 1
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_status_damage(mutator, side, self.previous_instruction)

        instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_leech_seed_saps_health(self):
        side = constants.SELF
        self.state.self.active.volatile_status.add(constants.LEECH_SEED)
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 100
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 50
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_status_damage(mutator, side, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.SELF,
            12
        )
        heal_instruction = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            12
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_leech_seed_only_saps_1_when_pokemon_has_1_hp(self):
        side = constants.SELF
        self.state.self.active.volatile_status.add(constants.LEECH_SEED)
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 1
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 50
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_status_damage(mutator, side, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.SELF,
            1
        )
        heal_instruction = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_leech_seed_does_not_overheal(self):
        side = constants.SELF
        self.state.self.active.volatile_status.add(constants.LEECH_SEED)
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 100
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 99
        mutator = StateMutator(self.state)
        instructions = self.state_generator.get_state_from_status_damage(mutator, side, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.SELF,
            12
        )
        heal_instruction = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)


if __name__ == '__main__':
    unittest.main()
