"""Unit tests for Player model"""
import pytest
from models.player import Player, PlayerStats


class TestPlayerStats:
    """Test PlayerStats class"""

    def test_default_stats(self):
        """Test default stat values"""
        stats = PlayerStats()
        assert stats.investigation == 5
        assert stats.persuasion == 5
        assert stats.perception == 5
        assert stats.intuition == 5
        assert stats.physical == 5

    def test_get_stat(self):
        """Test getting stat by name"""
        stats = PlayerStats(investigation=7)
        assert stats.get_stat("investigation") == 7
        assert stats.get_stat("Investigation") == 7
        assert stats.get_stat("nonexistent") == 0

    def test_modify_stat(self):
        """Test modifying stats"""
        stats = PlayerStats()
        stats.modify_stat("investigation", 3)
        assert stats.investigation == 8

    def test_modify_stat_clamping(self):
        """Test stats are clamped to 0-10"""
        stats = PlayerStats(investigation=9)
        stats.modify_stat("investigation", 5)
        assert stats.investigation == 10  # Clamped to max

        stats.modify_stat("investigation", -15)
        assert stats.investigation == 0  # Clamped to min


class TestPlayer:
    """Test Player class"""

    def test_player_creation(self):
        """Test creating a new player"""
        player = Player(name="Detective Smith")
        assert player.name == "Detective Smith"
        assert player.reputation == 50
        assert player.current_location == "crime_scene"
        assert len(player.inventory) == 0

    def test_add_item(self):
        """Test adding items to inventory"""
        player = Player(name="Test")
        player.add_item("magnifying_glass")
        assert "magnifying_glass" in player.inventory
        assert len(player.inventory) == 1

        # Adding same item again shouldn't duplicate
        player.add_item("magnifying_glass")
        assert len(player.inventory) == 1

    def test_remove_item(self):
        """Test removing items from inventory"""
        player = Player(name="Test")
        player.add_item("notebook")

        success = player.remove_item("notebook")
        assert success is True
        assert "notebook" not in player.inventory

        # Removing non-existent item
        success = player.remove_item("nonexistent")
        assert success is False

    def test_has_item(self):
        """Test checking for item in inventory"""
        player = Player(name="Test")
        player.add_item("badge")

        assert player.has_item("badge") is True
        assert player.has_item("gun") is False

    def test_add_clue(self):
        """Test adding clues"""
        player = Player(name="Test")
        player.add_clue("fingerprint")
        assert "fingerprint" in player.clues_found

        # Adding duplicate shouldn't duplicate
        player.add_clue("fingerprint")
        assert player.clues_found.count("fingerprint") == 1

    def test_visit_location(self):
        """Test visiting locations"""
        player = Player(name="Test")
        player.visit_location("police_station")

        assert player.current_location == "police_station"
        assert "police_station" in player.locations_visited

    def test_meet_npc(self):
        """Test meeting NPCs"""
        player = Player(name="Test")
        player.meet_npc("detective_chen")
        assert "detective_chen" in player.npcs_met

    def test_complete_quest(self):
        """Test completing quests"""
        player = Player(name="Test")
        player.complete_quest("tutorial_quest")
        assert "tutorial_quest" in player.completed_quests

    def test_modify_reputation(self):
        """Test reputation changes"""
        player = Player(name="Test")
        player.modify_reputation(20)
        assert player.reputation == 70

        player.modify_reputation(-100)
        assert player.reputation == 0  # Clamped to 0

        player.reputation = 90
        player.modify_reputation(20)
        assert player.reputation == 100  # Clamped to 100

    def test_serialization(self):
        """Test to_dict and from_dict"""
        player = Player(name="Detective Jones")
        player.add_item("badge")
        player.add_clue("bloodstain")
        player.visit_location("crime_scene")
        player.reputation = 75

        # Serialize
        data = player.to_dict()
        assert data["name"] == "Detective Jones"
        assert "badge" in data["inventory"]
        assert data["reputation"] == 75

        # Deserialize
        restored = Player.from_dict(data)
        assert restored.name == player.name
        assert restored.reputation == player.reputation
        assert restored.has_item("badge")
        assert "bloodstain" in restored.clues_found
