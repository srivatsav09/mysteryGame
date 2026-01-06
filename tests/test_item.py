"""Unit tests for Item and Clue models"""
import pytest
from models.item import Item, Clue, ItemType


class TestItem:
    """Test Item class"""

    def test_item_creation(self):
        """Test creating an item"""
        item = Item(
            id="magnifying_glass",
            name="Magnifying Glass",
            description="A detective's essential tool",
            item_type=ItemType.TOOL
        )
        assert item.id == "magnifying_glass"
        assert item.name == "Magnifying Glass"
        assert item.item_type == ItemType.TOOL
        assert item.can_examine is True

    def test_evidence_item(self):
        """Test creating evidence item"""
        item = Item(
            id="bloody_knife",
            name="Bloody Knife",
            description="A knife with blood on it",
            item_type=ItemType.EVIDENCE,
            is_clue=True,
            found_at="crime_scene"
        )
        assert item.is_clue is True
        assert item.found_at == "crime_scene"

    def test_item_tags(self):
        """Test item tags"""
        item = Item(
            id="letter",
            name="Threatening Letter",
            description="A letter with threats",
            item_type=ItemType.DOCUMENT,
            tags=["paper", "evidence", "handwritten"]
        )
        assert "paper" in item.tags
        assert len(item.tags) == 3

    def test_item_serialization(self):
        """Test item serialization"""
        item = Item(
            id="lockpick",
            name="Lockpick Set",
            description="Professional lockpicks",
            item_type=ItemType.TOOL,
            can_use=True,
            tags=["tool", "illegal"]
        )

        # Serialize
        data = item.to_dict()
        assert data["id"] == "lockpick"
        assert data["item_type"] == "tool"
        assert "tool" in data["tags"]

        # Deserialize
        restored = Item.from_dict(data)
        assert restored.id == item.id
        assert restored.item_type == item.item_type
        assert restored.tags == item.tags


class TestClue:
    """Test Clue class"""

    def test_clue_creation(self):
        """Test creating a clue"""
        clue = Clue(
            id="fingerprint",
            title="Fingerprint on Glass",
            description="A clear fingerprint found on a wine glass",
            category="physical",
            found_at="crime_scene"
        )
        assert clue.id == "fingerprint"
        assert clue.category == "physical"
        assert clue.importance == 1

    def test_clue_with_requirements(self):
        """Test clue with stat requirements"""
        clue = Clue(
            id="hidden_message",
            title="Hidden Message",
            description="A message written in invisible ink",
            category="forensic",
            found_at="victim_home",
            requires_stat="perception",
            requires_stat_level=7
        )
        assert clue.requires_stat == "perception"
        assert clue.requires_stat_level == 7

    def test_clue_relationships(self):
        """Test clue relationships with NPCs and other clues"""
        clue = Clue(
            id="alibi_discrepancy",
            title="Alibi Doesn't Match",
            description="Witness timeline doesn't align with evidence",
            category="testimony",
            found_at="police_station",
            related_npcs=["suspect_1", "witness_2"],
            related_clues=["timeline_clue"],
            contradicts_clues=["original_alibi"]
        )
        assert "suspect_1" in clue.related_npcs
        assert "timeline_clue" in clue.related_clues
        assert "original_alibi" in clue.contradicts_clues

    def test_clue_unlocks_dialogue(self):
        """Test clue unlocking dialogue options"""
        clue = Clue(
            id="murder_weapon",
            title="The Murder Weapon",
            description="A knife identified as the murder weapon",
            category="physical",
            found_at="crime_scene",
            importance=5,
            unlocks_dialogue=["confront_about_weapon", "ask_about_knife"]
        )
        assert clue.importance == 5
        assert "confront_about_weapon" in clue.unlocks_dialogue

    def test_clue_serialization(self):
        """Test clue serialization"""
        clue = Clue(
            id="test_clue",
            title="Test Clue",
            description="A test clue",
            category="physical",
            found_at="test_location",
            related_npcs=["npc1"],
            importance=3
        )

        # Serialize
        data = clue.to_dict()
        assert data["id"] == "test_clue"
        assert data["importance"] == 3

        # Deserialize
        restored = Clue.from_dict(data)
        assert restored.id == clue.id
        assert restored.importance == clue.importance
        assert "npc1" in restored.related_npcs
