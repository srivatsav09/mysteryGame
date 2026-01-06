"""Unit tests for WorldState model"""
import pytest
from models.world import WorldState
from models.player import Player
from models.location import Location
from models.npc import NPC, NPCRole
from models.item import Item, ItemType, Clue
from models.quest import Quest, QuestStatus


class TestWorldState:
    """Test WorldState class"""

    def test_world_creation(self):
        """Test creating a world state"""
        player = Player(name="Detective")
        world = WorldState(player=player)

        assert world.player.name == "Detective"
        assert len(world.locations) == 0
        assert world.current_time == 480  # 8:00 AM
        assert world.current_day == 1
        assert world.game_started is False

    def test_get_location(self):
        """Test getting location by ID"""
        player = Player(name="Test")
        world = WorldState(player=player)

        location = Location(id="crime_scene", name="Crime Scene", description="Test")
        world.locations["crime_scene"] = location

        retrieved = world.get_location("crime_scene")
        assert retrieved is not None
        assert retrieved.id == "crime_scene"

        # Non-existent location
        assert world.get_location("nonexistent") is None

    def test_get_current_location(self):
        """Test getting player's current location"""
        player = Player(name="Test")
        world = WorldState(player=player)

        location = Location(id="crime_scene", name="Crime Scene", description="Test")
        world.locations["crime_scene"] = location
        player.current_location = "crime_scene"

        current = world.get_current_location()
        assert current is not None
        assert current.id == "crime_scene"

    def test_get_npc(self):
        """Test getting NPC by ID"""
        player = Player(name="Test")
        world = WorldState(player=player)

        npc = NPC(id="witness", name="Witness", description="Test", role=NPCRole.WITNESS)
        world.npcs["witness"] = npc

        retrieved = world.get_npc("witness")
        assert retrieved is not None
        assert retrieved.id == "witness"

    def test_get_npcs_at_location(self):
        """Test getting NPCs at a specific location"""
        player = Player(name="Test")
        world = WorldState(player=player)

        npc1 = NPC(id="npc1", name="NPC1", description="Test", role=NPCRole.WITNESS)
        npc1.current_location = "cafe"

        npc2 = NPC(id="npc2", name="NPC2", description="Test", role=NPCRole.SUSPECT)
        npc2.current_location = "cafe"

        npc3 = NPC(id="npc3", name="NPC3", description="Test", role=NPCRole.ALLY)
        npc3.current_location = "station"

        world.npcs["npc1"] = npc1
        world.npcs["npc2"] = npc2
        world.npcs["npc3"] = npc3

        npcs_at_cafe = world.get_npcs_at_location("cafe")
        assert len(npcs_at_cafe) == 2
        assert all(npc.current_location == "cafe" for npc in npcs_at_cafe)

    def test_get_item_and_clue(self):
        """Test getting items and clues"""
        player = Player(name="Test")
        world = WorldState(player=player)

        item = Item(id="knife", name="Knife", description="Test", item_type=ItemType.EVIDENCE)
        clue = Clue(id="fingerprint", title="Fingerprint", description="Test", category="physical", found_at="scene")

        world.items["knife"] = item
        world.clues["fingerprint"] = clue

        assert world.get_item("knife") is not None
        assert world.get_clue("fingerprint") is not None

    def test_get_quests(self):
        """Test getting quests"""
        player = Player(name="Test")
        world = WorldState(player=player)

        quest1 = Quest(id="q1", title="Quest 1", description="Test", status=QuestStatus.ACTIVE)
        quest2 = Quest(id="q2", title="Quest 2", description="Test", status=QuestStatus.COMPLETED)
        quest3 = Quest(id="q3", title="Quest 3", description="Test", status=QuestStatus.AVAILABLE)

        world.quests["q1"] = quest1
        world.quests["q2"] = quest2
        world.quests["q3"] = quest3

        # Get active quests
        active = world.get_active_quests()
        assert len(active) == 1
        assert active[0].id == "q1"

    def test_advance_time(self):
        """Test advancing game time"""
        player = Player(name="Test")
        world = WorldState(player=player)

        world.current_time = 480  # 8:00 AM
        world.advance_time(60)  # Add 1 hour
        assert world.current_time == 540  # 9:00 AM

        # Test day rollover
        world.current_time = 1400  # 11:20 PM
        world.advance_time(60)  # Add 1 hour
        assert world.current_day == 2
        assert world.current_time == 20  # 12:20 AM

    def test_get_time_string(self):
        """Test time formatting"""
        player = Player(name="Test")
        world = WorldState(player=player)

        world.current_time = 480  # 8:00 AM
        assert world.get_time_string() == "8:00 AM"

        world.current_time = 720  # 12:00 PM
        assert world.get_time_string() == "12:00 PM"

        world.current_time = 900  # 3:00 PM
        assert world.get_time_string() == "3:00 PM"

        world.current_time = 1380  # 11:00 PM
        assert world.get_time_string() == "11:00 PM"

    def test_story_beats(self):
        """Test story beat tracking"""
        player = Player(name="Test")
        world = WorldState(player=player)

        world.add_story_beat("Found the murder weapon")
        world.add_story_beat("Interrogated the suspect")

        assert len(world.story_beats) == 2
        assert "Found the murder weapon" in world.story_beats

    def test_world_serialization(self):
        """Test world state serialization"""
        player = Player(name="Detective Smith")
        world = WorldState(player=player)

        # Add some entities
        location = Location(id="scene", name="Scene", description="Test")
        npc = NPC(id="witness", name="Witness", description="Test", role=NPCRole.WITNESS)
        item = Item(id="knife", name="Knife", description="Test", item_type=ItemType.EVIDENCE)
        clue = Clue(id="blood", title="Blood", description="Test", category="physical", found_at="scene")
        quest = Quest(id="solve", title="Solve", description="Test")

        world.locations["scene"] = location
        world.npcs["witness"] = npc
        world.items["knife"] = item
        world.clues["blood"] = clue
        world.quests["solve"] = quest

        world.advance_time(120)
        world.add_story_beat("Investigation started")

        # Serialize
        data = world.to_dict()
        assert data["player"]["name"] == "Detective Smith"
        assert "scene" in data["locations"]
        assert "witness" in data["npcs"]
        assert data["current_time"] == 600
        assert "Investigation started" in data["story_beats"]

        # Deserialize
        restored = WorldState.from_dict(data)
        assert restored.player.name == "Detective Smith"
        assert "scene" in restored.locations
        assert "witness" in restored.npcs
        assert restored.current_time == 600
        assert "Investigation started" in restored.story_beats

    def test_game_state_flags(self):
        """Test game state flags"""
        player = Player(name="Test")
        world = WorldState(player=player)

        assert world.game_started is False
        assert world.game_over is False
        assert world.ending_type is None

        world.game_started = True
        world.game_over = True
        world.ending_type = "good"

        assert world.game_started is True
        assert world.game_over is True
        assert world.ending_type == "good"
