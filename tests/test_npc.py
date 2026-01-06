"""Unit tests for NPC model"""
import pytest
from models.npc import NPC, NPCRole, Mood, NPCMemory


class TestNPCMemory:
    """Test NPCMemory class"""

    def test_memory_creation(self):
        """Test creating NPC memory"""
        memory = NPCMemory()
        assert memory.times_talked == 0
        assert len(memory.topics_discussed) == 0
        assert memory.lies_told == 0


class TestNPC:
    """Test NPC class"""

    def test_npc_creation(self):
        """Test creating an NPC"""
        npc = NPC(
            id="detective_chen",
            name="Detective Chen",
            description="A seasoned detective",
            role=NPCRole.ALLY
        )
        assert npc.id == "detective_chen"
        assert npc.role == NPCRole.ALLY
        assert npc.trust_level == 50
        assert npc.mood == Mood.NEUTRAL
        assert npc.relationship_status == "stranger"

    def test_npc_with_personality(self):
        """Test NPC with personality traits"""
        npc = NPC(
            id="suspect_1",
            name="John Doe",
            description="Nervous accountant",
            role=NPCRole.SUSPECT,
            personality_traits=["nervous", "secretive", "intelligent"],
            secrets=["embezzled_money", "affair"]
        )
        assert "nervous" in npc.personality_traits
        assert "embezzled_money" in npc.secrets

    def test_modify_trust(self):
        """Test modifying trust level"""
        npc = NPC(
            id="witness",
            name="Jane Smith",
            description="A witness",
            role=NPCRole.WITNESS
        )

        initial_trust = npc.trust_level
        npc.modify_trust(20)
        assert npc.trust_level == initial_trust + 20

        # Test clamping
        npc.modify_trust(100)
        assert npc.trust_level == 100

        npc.modify_trust(-200)
        assert npc.trust_level == 0

    def test_relationship_status_updates(self):
        """Test relationship status changes with trust"""
        npc = NPC(id="npc", name="Test", description="Test", role=NPCRole.NEUTRAL)

        npc.trust_level = 85
        npc._update_relationship_status()
        assert npc.relationship_status == "friend"

        npc.trust_level = 55
        npc._update_relationship_status()
        assert npc.relationship_status == "acquaintance"

        npc.trust_level = 15
        npc._update_relationship_status()
        assert npc.relationship_status == "enemy"

    def test_mood_updates(self):
        """Test mood changes with trust"""
        npc = NPC(id="npc", name="Test", description="Test", role=NPCRole.NEUTRAL)

        npc.trust_level = 75
        npc._update_mood()
        assert npc.mood == Mood.FRIENDLY

        npc.trust_level = 45
        npc._update_mood()
        assert npc.mood == Mood.NEUTRAL

        npc.trust_level = 15
        npc._update_mood()
        assert npc.mood == Mood.HOSTILE

    def test_talk_to(self):
        """Test conversation tracking"""
        npc = NPC(id="npc", name="Test", description="Test", role=NPCRole.WITNESS)

        assert npc.memory.times_talked == 0

        npc.talk_to("whereabouts")
        assert npc.memory.times_talked == 1
        assert "whereabouts" in npc.memory.topics_discussed
        assert npc.memory.last_interaction == "whereabouts"

        npc.talk_to("alibi")
        assert npc.memory.times_talked == 2
        assert "alibi" in npc.memory.topics_discussed

    def test_show_clue(self):
        """Test showing clues to NPC"""
        npc = NPC(id="npc", name="Test", description="Test", role=NPCRole.SUSPECT)

        npc.show_clue("fingerprint")
        assert "fingerprint" in npc.memory.clues_shown

    def test_share_clue(self):
        """Test NPC sharing clues"""
        npc = NPC(
            id="informant",
            name="Informant",
            description="Test",
            role=NPCRole.INFORMANT,
            knows_clues={"secret_location", "witness_identity"},
            will_share_clues={"secret_location"}
        )

        # Cannot share if trust too low
        npc.trust_level = 20
        can_share = npc.can_share_clue("secret_location")
        assert can_share is False

        # Can share if trust high enough
        npc.trust_level = 50
        can_share = npc.can_share_clue("secret_location")
        assert can_share is True

        # Share clue
        shared = npc.share_clue("secret_location")
        assert shared is True
        assert "secret_location" not in npc.will_share_clues

    def test_npc_schedule(self):
        """Test NPC schedule system"""
        npc = NPC(
            id="npc",
            name="Test",
            description="Test",
            role=NPCRole.NEUTRAL,
            schedule={
                "morning": "home",
                "afternoon": "office",
                "evening": "bar"
            }
        )
        assert npc.schedule["morning"] == "home"
        assert npc.schedule["evening"] == "bar"

    def test_move_to(self):
        """Test moving NPC to location"""
        npc = NPC(id="npc", name="Test", description="Test", role=NPCRole.NEUTRAL)

        npc.move_to("downtown")
        assert npc.current_location == "downtown"

    def test_npc_relationships(self):
        """Test NPC relationships with other NPCs"""
        npc = NPC(
            id="npc1",
            name="Test",
            description="Test",
            role=NPCRole.NEUTRAL,
            relationships={"npc2": 80, "npc3": -20}
        )
        assert npc.relationships["npc2"] == 80
        assert npc.relationships["npc3"] == -20

    def test_quest_giving(self):
        """Test NPCs giving quests"""
        npc = NPC(
            id="police_chief",
            name="Chief",
            description="Test",
            role=NPCRole.AUTHORITY,
            gives_quests=["investigate_murder", "find_witness"]
        )
        assert "investigate_murder" in npc.gives_quests

    def test_npc_serialization(self):
        """Test NPC serialization"""
        npc = NPC(
            id="witness",
            name="Witness",
            description="Test",
            role=NPCRole.WITNESS,
            personality_traits=["nervous"],
            secrets=["saw_killer"]
        )
        npc.modify_trust(20)
        npc.talk_to("what_you_saw")

        # Serialize
        data = npc.to_dict()
        assert data["id"] == "witness"
        assert data["trust_level"] == 70
        assert "nervous" in data["personality_traits"]

        # Deserialize
        restored = NPC.from_dict(data)
        assert restored.id == npc.id
        assert restored.trust_level == npc.trust_level
        assert restored.memory.times_talked == 1
        assert "what_you_saw" in restored.memory.topics_discussed
