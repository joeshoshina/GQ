"""
Mini-Adventures Framework for GuildQuest.

Provides extensible framework for creating short, self-contained adventures with
consistent UI integration and game mechanics.

Key components:
- BaseAdventure (base_adventure.py): Abstract base class defining adventure lifecycle
	- start(): Initialize adventure (create context, set up board)
	- handle_input(player_index, direction): Process player action
	- update(): Advance game state (time, physics, etc.)
	- get_state(): Return current game state as Mapping (immutable dict-like)
	- is_complete(): Check if game has ended
	- reset(session_id): Reset adventure for new play session

- Strategy Pattern (strategies/): Pluggable game mechanics
	- MovementStrategy (movement.py): How players move (GridMovement implementation)
	- TimeStrategy (time_strategy.py): Time advancement (TurnBasedTime implementation)
	- WinConditionStrategy (win_condition.py): Victory conditions (RelicCountWin implementation)

- AdventureContext (context.py): Dependency container for strategies
	- Provides move_player(), advance_time(), check_winner() methods
	- Decouples adventure logic from specific strategy implementations

- RelicRaceAdventure (relic_hunt.py): Concrete implementation (relic collection game)

Design rationale:
- Framework enables easy creation of new adventures without modifying core
- Strategy pattern allows plugging different movement/time/win mechanics
- Base classes enforce consistent interface for UI integration
- All game state returned as Mapping to prevent accidental mutation from UI
- Created __init__.py during Phase 5 audit to ensure proper package discovery
"""
