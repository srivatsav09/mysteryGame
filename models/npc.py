"""NPC model with personality, memory, and relationships"""
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class NPCRole(Enum):
    """NPC roles in the mystery"""
    SUSPECT = "suspect"
    WITNESS = "witness"
    ALLY = "ally"
    VICTIM = "victim"
    INFORMANT = "informant"
    AUTHORITY = "authority"
    NEUTRAL = "neutral"


class Mood(Enum):
    """Current emotional state"""
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    SUSPICIOUS = "suspicious"
    HOSTILE = "hostile"
    SCARED = "scared"
    GUILTY = "guilty"
    HELPFUL = "helpful"


@dataclass
class DialogueOption:
    """A dialogue choice in conversation tree"""
    id: str
    text: str
    requires_clue: Optional[str] = None
    requires_stat: Optional[str] = None
    requires_stat_level: int = 0
    trust_change: int = 0
    reveals_clue: Optional[str] = None
    unlocks_dialogue: List[str] = field(default_factory=list)
    one_time: bool = False
    used: bool = False


@dataclass
class NPCMemory:
    """What NPC remembers about interactions"""
    times_talked: int = 0
    topics_discussed: Set[str] = field(default_factory=set)
    clues_shown: Set[str] = field(default_factory=set)
    lies_told: int = 0  # Player lied to them
    promises_made: List[str] = field(default_factory=list)
    promises_kept: int = 0
    promises_broken: int = 0
    last_interaction: Optional[str] = None  # Last thing discussed


@dataclass
class NPC:
    """Non-player character"""
    id: str
    name: str
    description: str
    role: NPCRole

    # Personality
    personality_traits: List[str] = field(default_factory=list)  # "nervous", "arrogant", etc.
    secrets: List[str] = field(default_factory=list)  # What they're hiding

    # Location
    current_location: str = "unknown"
    schedule: Dict[str, str] = field(default_factory=dict)  # {time_period: location_id}

    # Relationship with player
    trust_level: int = 50  # 0-100
    mood: Mood = Mood.NEUTRAL
    relationship_status: str = "stranger"  # stranger, acquaintance, friend, enemy

    # Memory and state
    memory: NPCMemory = field(default_factory=NPCMemory)
    knows_clues: Set[str] = field(default_factory=set)  # clue_ids they know about
    will_share_clues: Set[str] = field(default_factory=set)  # clues they'll reveal

    # Dialogue
    available_dialogues: List[str] = field(default_factory=list)  # dialogue_ids available
    completed_dialogues: Set[str] = field(default_factory=set)  # dialogue_ids finished

    # Quest giving
    gives_quests: List[str] = field(default_factory=list)  # quest_ids they can give

    # Relationships with other NPCs
    relationships: Dict[str, int] = field(default_factory=dict)  # {npc_id: relationship_score}

    def modify_trust(self, amount: int):
        """Change trust level (clamped 0-100)"""
        self.trust_level = max(0, min(100, self.trust_level + amount))
        self._update_relationship_status()
        self._update_mood()

    def _update_relationship_status(self):
        """Update relationship status based on trust"""
        if self.trust_level >= 80:
            self.relationship_status = "friend"
        elif self.trust_level >= 50:
            self.relationship_status = "acquaintance"
        elif self.trust_level >= 20:
            self.relationship_status = "stranger"
        else:
            self.relationship_status = "enemy"

    def _update_mood(self):
        """Update mood based on trust and role"""
        if self.trust_level >= 70:
            self.mood = Mood.FRIENDLY
        elif self.trust_level >= 40:
            self.mood = Mood.NEUTRAL
        elif self.trust_level >= 20:
            self.mood = Mood.SUSPICIOUS
        else:
            self.mood = Mood.HOSTILE

    def talk_to(self, topic: Optional[str] = None):
        """Record conversation"""
        self.memory.times_talked += 1
        if topic:
            self.memory.topics_discussed.add(topic)
            self.memory.last_interaction = topic

    def show_clue(self, clue_id: str):
        """Player shows them a clue"""
        self.memory.clues_shown.add(clue_id)

    def can_share_clue(self, clue_id: str) -> bool:
        """Check if NPC will share a clue"""
        return clue_id in self.will_share_clues and self.trust_level >= 30

    def share_clue(self, clue_id: str) -> bool:
        """NPC shares a clue with player"""
        if self.can_share_clue(clue_id):
            self.will_share_clues.remove(clue_id)
            return True
        return False

    def move_to(self, location_id: str):
        """Move NPC to location"""
        self.current_location = location_id

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "role": self.role.value,
            "personality_traits": self.personality_traits,
            "secrets": self.secrets,
            "current_location": self.current_location,
            "schedule": self.schedule,
            "trust_level": self.trust_level,
            "mood": self.mood.value,
            "relationship_status": self.relationship_status,
            "memory": {
                "times_talked": self.memory.times_talked,
                "topics_discussed": list(self.memory.topics_discussed),
                "clues_shown": list(self.memory.clues_shown),
                "lies_told": self.memory.lies_told,
                "promises_made": self.memory.promises_made,
                "promises_kept": self.memory.promises_kept,
                "promises_broken": self.memory.promises_broken,
                "last_interaction": self.memory.last_interaction,
            },
            "knows_clues": list(self.knows_clues),
            "will_share_clues": list(self.will_share_clues),
            "available_dialogues": self.available_dialogues,
            "completed_dialogues": list(self.completed_dialogues),
            "gives_quests": self.gives_quests,
            "relationships": self.relationships,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NPC':
        """Deserialize from dictionary"""
        memory_data = data.get("memory", {})
        memory = NPCMemory(
            times_talked=memory_data.get("times_talked", 0),
            topics_discussed=set(memory_data.get("topics_discussed", [])),
            clues_shown=set(memory_data.get("clues_shown", [])),
            lies_told=memory_data.get("lies_told", 0),
            promises_made=memory_data.get("promises_made", []),
            promises_kept=memory_data.get("promises_kept", 0),
            promises_broken=memory_data.get("promises_broken", 0),
            last_interaction=memory_data.get("last_interaction"),
        )

        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            role=NPCRole(data["role"]),
            personality_traits=data.get("personality_traits", []),
            secrets=data.get("secrets", []),
            current_location=data.get("current_location", "unknown"),
            schedule=data.get("schedule", {}),
            trust_level=data.get("trust_level", 50),
            mood=Mood(data.get("mood", "neutral")),
            relationship_status=data.get("relationship_status", "stranger"),
            memory=memory,
            knows_clues=set(data.get("knows_clues", [])),
            will_share_clues=set(data.get("will_share_clues", [])),
            available_dialogues=data.get("available_dialogues", []),
            completed_dialogues=set(data.get("completed_dialogues", [])),
            gives_quests=data.get("gives_quests", []),
            relationships=data.get("relationships", {}),
        )
