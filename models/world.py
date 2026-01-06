"""World state model - Container for entire game state"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .player import Player
from .location import Location
from .npc import NPC
from .item import Item, Clue
from .quest import Quest


@dataclass
class WorldState:
    """Complete game world state"""
    # Core entities
    player: Player
    locations: Dict[str, Location] = field(default_factory=dict)
    npcs: Dict[str, NPC] = field(default_factory=dict)
    items: Dict[str, Item] = field(default_factory=dict)
    clues: Dict[str, Clue] = field(default_factory=dict)
    quests: Dict[str, Quest] = field(default_factory=dict)

    # World state
    current_time: int = 480  # Minutes since midnight (8:00 AM start)
    current_day: int = 1
    weather: str = "clear"

    # Game state
    game_started: bool = False
    game_over: bool = False
    ending_type: Optional[str] = None  # "good", "bad", "neutral"

    # Narrative tracking
    story_beats: List[str] = field(default_factory=list)  # Major story events
    conversation_history: List[dict] = field(default_factory=list)  # Full dialogue history

    def get_location(self, location_id: str) -> Optional[Location]:
        """Get location by ID"""
        return self.locations.get(location_id)

    def get_current_location(self) -> Optional[Location]:
        """Get player's current location"""
        return self.get_location(self.player.current_location)

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get NPC by ID"""
        return self.npcs.get(npc_id)

    def get_npcs_at_location(self, location_id: str) -> List[NPC]:
        """Get all NPCs at a location"""
        return [npc for npc in self.npcs.values() if npc.current_location == location_id]

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get item by ID"""
        return self.items.get(item_id)

    def get_clue(self, clue_id: str) -> Optional[Clue]:
        """Get clue by ID"""
        return self.clues.get(clue_id)

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get quest by ID"""
        return self.quests.get(quest_id)

    def get_active_quests(self) -> List[Quest]:
        """Get all active quests"""
        return [q for q in self.quests.values() if q.status.value == "active"]

    def get_available_quests(self) -> List[Quest]:
        """Get quests that can be started"""
        return [
            q for q in self.quests.values()
            if q.status.value == "available" and q.is_unlocked(self.player)
        ]

    def advance_time(self, minutes: int):
        """Advance game time"""
        self.current_time += minutes
        if self.current_time >= 1440:  # New day
            self.current_time -= 1440
            self.current_day += 1

    def get_time_string(self) -> str:
        """Get formatted time string"""
        hours = self.current_time // 60
        minutes = self.current_time % 60
        period = "AM" if hours < 12 else "PM"
        display_hours = hours if hours <= 12 else hours - 12
        if display_hours == 0:
            display_hours = 12
        return f"{display_hours}:{minutes:02d} {period}"

    def add_story_beat(self, beat: str):
        """Record major story event"""
        self.story_beats.append(beat)

    def to_dict(self) -> dict:
        """Serialize entire world state to dictionary"""
        return {
            "player": self.player.to_dict(),
            "locations": {loc_id: loc.to_dict() for loc_id, loc in self.locations.items()},
            "npcs": {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()},
            "items": {item_id: item.to_dict() for item_id, item in self.items.items()},
            "clues": {clue_id: clue.to_dict() for clue_id, clue in self.clues.items()},
            "quests": {quest_id: quest.to_dict() for quest_id, quest in self.quests.items()},
            "current_time": self.current_time,
            "current_day": self.current_day,
            "weather": self.weather,
            "game_started": self.game_started,
            "game_over": self.game_over,
            "ending_type": self.ending_type,
            "story_beats": self.story_beats,
            "conversation_history": self.conversation_history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WorldState':
        """Deserialize from dictionary"""
        from .player import Player
        from .location import Location
        from .npc import NPC
        from .item import Item, Clue
        from .quest import Quest

        world = cls(
            player=Player.from_dict(data["player"]),
            current_time=data.get("current_time", 480),
            current_day=data.get("current_day", 1),
            weather=data.get("weather", "clear"),
            game_started=data.get("game_started", False),
            game_over=data.get("game_over", False),
            ending_type=data.get("ending_type"),
            story_beats=data.get("story_beats", []),
            conversation_history=data.get("conversation_history", []),
        )

        # Reconstruct locations
        for loc_id, loc_data in data.get("locations", {}).items():
            world.locations[loc_id] = Location.from_dict(loc_data)

        # Reconstruct NPCs
        for npc_id, npc_data in data.get("npcs", {}).items():
            world.npcs[npc_id] = NPC.from_dict(npc_data)

        # Reconstruct items
        for item_id, item_data in data.get("items", {}).items():
            world.items[item_id] = Item.from_dict(item_data)

        # Reconstruct clues
        for clue_id, clue_data in data.get("clues", {}).items():
            world.clues[clue_id] = Clue.from_dict(clue_data)

        # Reconstruct quests
        for quest_id, quest_data in data.get("quests", {}).items():
            world.quests[quest_id] = Quest.from_dict(quest_data)

        return world
