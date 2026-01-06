"""Unit tests for Quest model"""
import pytest
from models.quest import Quest, QuestObjective, QuestStatus, ObjectiveType
from models.player import Player


class TestQuestObjective:
    """Test QuestObjective class"""

    def test_objective_creation(self):
        """Test creating an objective"""
        obj = QuestObjective(
            id="find_weapon",
            description="Find the murder weapon",
            objective_type=ObjectiveType.FIND_CLUE,
            target_id="knife_clue"
        )
        assert obj.id == "find_weapon"
        assert obj.objective_type == ObjectiveType.FIND_CLUE
        assert obj.completed is False
        assert obj.progress == 0

    def test_objective_with_quantity(self):
        """Test objective with quantity requirement"""
        obj = QuestObjective(
            id="talk_to_witnesses",
            description="Talk to 3 witnesses",
            objective_type=ObjectiveType.TALK_TO_NPC,
            quantity=3
        )
        assert obj.quantity == 3

    def test_objective_dependencies(self):
        """Test objective dependencies (DAG)"""
        obj = QuestObjective(
            id="confront_suspect",
            description="Confront the suspect",
            objective_type=ObjectiveType.CONFRONT_NPC,
            requires_objectives=["find_evidence", "talk_to_witnesses"]
        )

        # Not available without dependencies
        completed = set()
        assert obj.is_available(completed) is False

        # Available when one dependency met
        completed.add("find_evidence")
        assert obj.is_available(completed) is False

        # Available when all dependencies met
        completed.add("talk_to_witnesses")
        assert obj.is_available(completed) is True

    def test_advance_progress(self):
        """Test advancing objective progress"""
        obj = QuestObjective(
            id="collect_clues",
            description="Collect 5 clues",
            objective_type=ObjectiveType.COLLECT_ITEM,
            quantity=5
        )

        # Advance progress
        completed = obj.advance_progress(2)
        assert obj.progress == 2
        assert completed is False

        # Complete objective
        completed = obj.advance_progress(3)
        assert obj.progress == 5
        assert obj.completed is True
        assert completed is True

        # Cannot exceed quantity
        obj.advance_progress(5)
        assert obj.progress == 5


class TestQuest:
    """Test Quest class"""

    def test_quest_creation(self):
        """Test creating a quest"""
        quest = Quest(
            id="solve_murder",
            title="Solve the Murder",
            description="Find who killed the victim",
            category="main"
        )
        assert quest.id == "solve_murder"
        assert quest.status == QuestStatus.LOCKED
        assert len(quest.objectives) == 0

    def test_add_objectives(self):
        """Test adding objectives to quest"""
        quest = Quest(id="test", title="Test", description="Test")

        obj1 = QuestObjective(
            id="obj1",
            description="First objective",
            objective_type=ObjectiveType.GO_TO_LOCATION,
            target_id="crime_scene"
        )
        obj2 = QuestObjective(
            id="obj2",
            description="Second objective",
            objective_type=ObjectiveType.FIND_CLUE,
            target_id="clue1"
        )

        quest.add_objective(obj1)
        quest.add_objective(obj2)

        assert len(quest.objectives) == 2
        assert "obj1" in quest.objectives

    def test_get_available_objectives(self):
        """Test getting available objectives"""
        quest = Quest(id="test", title="Test", description="Test")

        # Create dependency chain: obj1 -> obj2 -> obj3
        obj1 = QuestObjective(
            id="obj1",
            description="First",
            objective_type=ObjectiveType.GO_TO_LOCATION
        )
        obj2 = QuestObjective(
            id="obj2",
            description="Second",
            objective_type=ObjectiveType.FIND_CLUE,
            requires_objectives=["obj1"]
        )
        obj3 = QuestObjective(
            id="obj3",
            description="Third",
            objective_type=ObjectiveType.TALK_TO_NPC,
            requires_objectives=["obj2"]
        )

        quest.add_objective(obj1)
        quest.add_objective(obj2)
        quest.add_objective(obj3)

        # Only obj1 available initially
        available = quest.get_available_objectives()
        assert len(available) == 1
        assert available[0].id == "obj1"

        # Complete obj1, now obj2 available
        quest.complete_objective("obj1")
        available = quest.get_available_objectives()
        assert len(available) == 1
        assert available[0].id == "obj2"

    def test_complete_objective(self):
        """Test completing objectives"""
        quest = Quest(id="test", title="Test", description="Test")

        obj = QuestObjective(
            id="obj1",
            description="Test",
            objective_type=ObjectiveType.FIND_CLUE
        )
        quest.add_objective(obj)

        success = quest.complete_objective("obj1")
        assert success is True  # Quest completes when all objectives done
        assert "obj1" in quest.completed_objectives
        assert quest.objectives["obj1"].completed is True
        assert quest.status == QuestStatus.COMPLETED

    def test_quest_completion(self):
        """Test quest completion when all objectives done"""
        quest = Quest(id="test", title="Test", description="Test")

        obj1 = QuestObjective(id="obj1", description="Test", objective_type=ObjectiveType.FIND_CLUE)
        obj2 = QuestObjective(id="obj2", description="Test", objective_type=ObjectiveType.TALK_TO_NPC)

        quest.add_objective(obj1)
        quest.add_objective(obj2)

        quest.complete_objective("obj1")
        assert quest.status != QuestStatus.COMPLETED

        quest.complete_objective("obj2")
        assert quest.status == QuestStatus.COMPLETED

    def test_quest_unlock_requirements(self):
        """Test quest unlock requirements"""
        quest = Quest(
            id="advanced_quest",
            title="Advanced Quest",
            description="Test",
            requires_quests=["tutorial_quest"],
            requires_clues=["important_clue"],
            requires_location="police_station"
        )

        player = Player(name="Test")

        # Not unlocked initially
        assert quest.is_unlocked(player) is False

        # Add requirements
        player.complete_quest("tutorial_quest")
        assert quest.is_unlocked(player) is False

        player.add_clue("important_clue")
        assert quest.is_unlocked(player) is False

        player.visit_location("police_station")
        assert quest.is_unlocked(player) is True

    def test_start_quest(self):
        """Test starting a quest"""
        quest = Quest(id="test", title="Test", description="Test", status=QuestStatus.AVAILABLE)

        quest.start()
        assert quest.status == QuestStatus.ACTIVE

    def test_quest_rewards(self):
        """Test quest rewards"""
        quest = Quest(
            id="quest",
            title="Quest",
            description="Test",
            reward_reputation=25,
            reward_items=["badge", "key"],
            unlocks_locations=["secret_room"],
            unlocks_npcs=["informant"]
        )

        assert quest.reward_reputation == 25
        assert "badge" in quest.reward_items
        assert "secret_room" in quest.unlocks_locations

    def test_quest_giver(self):
        """Test quest giver"""
        quest = Quest(
            id="quest",
            title="Quest",
            description="Test",
            given_by="detective_chen"
        )
        assert quest.given_by == "detective_chen"

    def test_progress_percentage(self):
        """Test quest progress calculation"""
        quest = Quest(id="test", title="Test", description="Test")

        obj1 = QuestObjective(id="obj1", description="Test", objective_type=ObjectiveType.FIND_CLUE)
        obj2 = QuestObjective(id="obj2", description="Test", objective_type=ObjectiveType.TALK_TO_NPC)
        obj3 = QuestObjective(id="obj3", description="Test", objective_type=ObjectiveType.GO_TO_LOCATION)

        quest.add_objective(obj1)
        quest.add_objective(obj2)
        quest.add_objective(obj3)

        assert quest.get_progress_percentage() == 0.0

        quest.complete_objective("obj1")
        assert quest.get_progress_percentage() == pytest.approx(33.33, rel=0.1)

        quest.complete_objective("obj2")
        assert quest.get_progress_percentage() == pytest.approx(66.66, rel=0.1)

        quest.complete_objective("obj3")
        assert quest.get_progress_percentage() == 100.0

    def test_quest_serialization(self):
        """Test quest serialization"""
        quest = Quest(
            id="murder_case",
            title="Solve Murder",
            description="Find the killer",
            category="main"
        )

        obj = QuestObjective(
            id="find_weapon",
            description="Find weapon",
            objective_type=ObjectiveType.FIND_CLUE
        )
        quest.add_objective(obj)
        quest.status = QuestStatus.ACTIVE

        # Serialize
        data = quest.to_dict()
        assert data["id"] == "murder_case"
        assert data["status"] == "active"
        assert "find_weapon" in data["objectives"]

        # Deserialize
        restored = Quest.from_dict(data)
        assert restored.id == quest.id
        assert restored.status == quest.status
        assert "find_weapon" in restored.objectives
