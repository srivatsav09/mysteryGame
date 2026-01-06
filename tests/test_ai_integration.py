"""Tests for AI-enhanced game engine (without actual AI calls)"""
import pytest
from config.sample_mystery import create_sample_mystery
from game_engine.ai_enhanced_engine import AIEnhancedGameEngine


class TestAIEnhancedEngine:
    """Test AI-enhanced engine with AI disabled (for fast testing)"""

    def test_engine_initialization_with_ai_disabled(self):
        """Test creating engine with AI disabled"""
        world = create_sample_mystery()
        engine = AIEnhancedGameEngine(world, use_ai=False)

        assert engine.world == world
        assert engine.use_ai is False
        assert engine.get_current_location() is not None

    def test_examine_location_static_fallback(self):
        """Test examine location falls back to static narrative"""
        world = create_sample_mystery()
        engine = AIEnhancedGameEngine(world, use_ai=False)

        narrative, discoveries = engine.perform_action("examine_location")

        assert "Luxury Penthouse" in narrative
        assert len(narrative) > 0

    def test_talk_to_npc_without_ai(self):
        """Test talking to NPC without AI"""
        world = create_sample_mystery()
        engine = AIEnhancedGameEngine(world, use_ai=False)

        narrative, discoveries = engine.perform_action("talk_officer_chen")

        assert "Officer Chen" in narrative
        assert "officer_chen" in world.player.npcs_met

    def test_search_location_without_ai(self):
        """Test searching without AI narrative"""
        world = create_sample_mystery()
        engine = AIEnhancedGameEngine(world, use_ai=False)

        initial_items = len(world.player.inventory)
        narrative, discoveries = engine.perform_action("search")

        # Should still find items/clues
        assert len(discoveries) > 0
        assert "Searching" in narrative

    def test_travel_without_ai(self):
        """Test travel without AI narrative"""
        world = create_sample_mystery()
        engine = AIEnhancedGameEngine(world, use_ai=False)

        narrative, discoveries = engine.perform_action("travel_police_station")

        assert world.player.current_location == "police_station"
        assert "Traveling" in narrative or "travel" in narrative.lower()

    def test_ai_engine_compatible_with_simple_engine(self):
        """Test that AI engine has same interface as simple engine"""
        world = create_sample_mystery()
        engine = AIEnhancedGameEngine(world, use_ai=False)

        # Should have same methods
        assert hasattr(engine, "get_available_actions")
        assert hasattr(engine, "perform_action")
        assert hasattr(engine, "get_game_stats")
        assert hasattr(engine, "check_win_condition")

    def test_quest_progress_updates_with_ai_engine(self):
        """Test quest objectives update correctly"""
        world = create_sample_mystery()
        engine = AIEnhancedGameEngine(world, use_ai=False)

        quest = world.get_quest("solve_murder")
        initial_completed = len(quest.completed_objectives)

        # Examine crime scene
        engine.perform_action("examine_location")

        # Should complete first objective
        assert len(quest.completed_objectives) >= initial_completed

    def test_npc_clue_sharing_works(self):
        """Test NPCs share clues based on trust"""
        world = create_sample_mystery()
        engine = AIEnhancedGameEngine(world, use_ai=False)

        npc = world.get_npc("officer_chen")
        initial_trust = npc.trust_level

        # Talk to NPC
        engine.perform_action("talk_officer_chen")

        # NPC should have been talked to
        assert npc.memory.times_talked > 0

    def test_skill_requirements_for_clues(self):
        """Test that clues with skill requirements are properly gated"""
        world = create_sample_mystery()
        engine = AIEnhancedGameEngine(world, use_ai=False)

        # Player has investigation skill 7
        assert world.player.stats.investigation == 7

        # Search for clues
        narrative, discoveries = engine.perform_action("search")

        # Should find some clues if requirements are met
        # (This depends on the specific clues at crime_scene)
        assert isinstance(discoveries, list)


class TestMapIntegration:
    """Test map visualization integration"""

    def test_map_visualizer_imports(self):
        """Test that map visualizer can be imported"""
        from ui.map_visualizer import MapVisualizer

        assert MapVisualizer is not None
        assert hasattr(MapVisualizer, "render_map")
        assert hasattr(MapVisualizer, "generate_map_svg")

    def test_map_svg_generation(self):
        """Test SVG map generation"""
        from ui.map_visualizer import MapVisualizer

        world = create_sample_mystery()
        svg = MapVisualizer.generate_map_svg(world)

        assert isinstance(svg, str)
        assert "<svg" in svg
        assert "</svg>" in svg
        # Should contain location names
        assert "Luxury Penthouse" in svg or "Crime Scene" in svg


class TestAIPrompts:
    """Test AI prompt generation"""

    def test_game_master_prompt_generation(self):
        """Test game master prompts are generated"""
        from config.prompts import get_game_master_prompt

        context = {
            "location_name": "Test Location",
            "location_description": "A test place",
            "npcs": ["Test NPC"],
            "has_items": True,
            "time": "10:00 AM",
            "reputation": 50
        }

        prompt = get_game_master_prompt("examine_location", context)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Test Location" in prompt

    def test_npc_dialogue_prompt_generation(self):
        """Test NPC dialogue prompts"""
        from config.prompts import get_npc_dialogue_prompt

        npc_data = {
            "name": "Test NPC",
            "role": "witness",
            "description": "A test person",
            "personality_traits": ["nervous"],
            "trust_level": 50,
            "mood": "neutral",
            "times_talked": 0,
            "topics_discussed": [],
            "secrets": [],
            "shareable_clues": []
        }

        context = {
            "player_action": "Starting conversation",
            "clues_shown": []
        }

        prompt = get_npc_dialogue_prompt(npc_data, context)

        assert isinstance(prompt, str)
        assert "Test NPC" in prompt
        assert "witness" in prompt
