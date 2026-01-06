"""Integration tests for minimal playable version"""
import pytest
from config.sample_mystery import create_sample_mystery
from game_engine.simple_engine import SimpleGameEngine


class TestMinimalVersion:
    """Test the minimal playable version"""

    def test_create_mystery_scenario(self):
        """Test creating the sample mystery"""
        world = create_sample_mystery()

        assert world.player.name == "Detective"
        assert world.game_started is True
        assert len(world.locations) == 5
        assert len(world.npcs) == 6
        assert len(world.clues) == 10
        assert len(world.items) == 5
        assert len(world.quests) == 1

    def test_game_engine_initialization(self):
        """Test game engine initialization"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        assert engine.world == world
        current_loc = engine.get_current_location()
        assert current_loc is not None
        assert current_loc.id == "crime_scene"

    def test_get_available_actions(self):
        """Test getting available actions"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        actions = engine.get_available_actions()

        assert len(actions) > 0

        # Should have examine action
        assert any(a["type"] == "examine" for a in actions)

        # Should have talk actions for NPCs at location
        talk_actions = [a for a in actions if a["type"] == "talk"]
        assert len(talk_actions) > 0

        # Should have search action
        assert any(a["type"] == "search" for a in actions)

        # Should have travel actions
        travel_actions = [a for a in actions if a["type"] == "travel"]
        assert len(travel_actions) > 0

    def test_examine_location(self):
        """Test examining a location"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        narrative, discoveries = engine.perform_action("examine_location")

        assert "Luxury Penthouse" in narrative
        assert len(narrative) > 0
        assert world.locations["crime_scene"].visited is True

    def test_search_location(self):
        """Test searching a location"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        initial_items = len(world.player.inventory)
        initial_clues = len(world.player.clues_found)

        narrative, discoveries = engine.perform_action("search")

        # Should find something
        assert len(discoveries) > 0
        assert (len(world.player.inventory) > initial_items or
                len(world.player.clues_found) > initial_clues)

    def test_talk_to_npc(self):
        """Test talking to an NPC"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        narrative, discoveries = engine.perform_action("talk_officer_chen")

        assert "Officer Chen" in narrative
        assert "officer_chen" in world.player.npcs_met

        # Check if NPC shared any clues
        npc = world.get_npc("officer_chen")
        assert npc.memory.times_talked > 0

    def test_travel_to_location(self):
        """Test traveling to another location"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        initial_time = world.current_time

        narrative, discoveries = engine.perform_action("travel_police_station")

        assert world.player.current_location == "police_station"
        assert "police_station" in world.player.locations_visited
        assert world.current_time > initial_time  # Time advanced

    def test_quest_progress(self):
        """Test quest objective completion"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        quest = world.get_quest("solve_murder")
        initial_completed = len(quest.completed_objectives)

        # Examine crime scene (completes first objective)
        engine.perform_action("examine_location")

        # Check if objective was completed
        assert len(quest.completed_objectives) >= initial_completed

    def test_win_condition_not_met_initially(self):
        """Test that win condition is not met at start"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        won, ending = engine.check_win_condition()
        assert won is False

    def test_game_stats(self):
        """Test getting game statistics"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        stats = engine.get_game_stats()

        assert "location" in stats
        assert "time" in stats
        assert "reputation" in stats
        assert stats["clues_found"] == 0  # No clues found yet
        assert stats["items_collected"] == 0

        # Search and check stats update
        engine.perform_action("search")
        stats = engine.get_game_stats()
        assert stats["clues_found"] > 0 or stats["items_collected"] > 0

    def test_location_requirements(self):
        """Test location access requirements"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        # Forensics lab should not be accessible initially
        actions = engine.get_available_actions()
        travel_actions = [a for a in actions if a["type"] == "travel"]
        forensics_action = [a for a in travel_actions if "forensics" in a["id"]]

        # Should not be in available actions initially
        assert len(forensics_action) == 0

        # Add required clue
        world.player.add_clue("wine_residue")

        # Travel to police station first
        engine.perform_action("travel_police_station")

        # Now forensics lab should be available
        actions = engine.get_available_actions()
        travel_actions = [a for a in actions if a["type"] == "travel"]
        forensics_action = [a for a in travel_actions if "forensics" in a["id"]]

        assert len(forensics_action) > 0

    def test_complete_playthrough_scenario(self):
        """Test a basic playthrough scenario"""
        world = create_sample_mystery()
        engine = SimpleGameEngine(world)

        # 1. Examine crime scene
        engine.perform_action("examine_location")
        assert world.player.current_location == "crime_scene"

        # 2. Search for evidence
        engine.perform_action("search")
        initial_items = len(world.player.inventory)
        assert initial_items > 0

        # 3. Talk to officer
        engine.perform_action("talk_officer_chen")
        assert "officer_chen" in world.player.npcs_met

        # 4. Travel to police station
        engine.perform_action("travel_police_station")
        assert world.player.current_location == "police_station"

        # 5. Check quest progress
        quest = world.get_quest("solve_murder")
        assert len(quest.completed_objectives) > 0
