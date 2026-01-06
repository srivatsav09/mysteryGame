"""Player model with stats, inventory, and skills"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PlayerStats:
    """Detective skills and attributes"""
    investigation: int = 5  # Finding and analyzing clues
    persuasion: int = 5     # Convincing NPCs, interrogation
    perception: int = 5     # Noticing details, awareness
    intuition: int = 5      # Making deductions, hunches
    physical: int = 5       # Chasing, fighting, athleticism

    def get_stat(self, stat_name: str) -> int:
        """Get stat value by name"""
        return getattr(self, stat_name.lower(), 0)

    def modify_stat(self, stat_name: str, amount: int):
        """Modify a stat by amount"""
        current = self.get_stat(stat_name)
        setattr(self, stat_name.lower(), max(0, min(10, current + amount)))


@dataclass
class Player:
    """Main player character"""
    name: str
    stats: PlayerStats = field(default_factory=PlayerStats)
    inventory: List[str] = field(default_factory=list)  # item IDs
    current_location: str = "crime_scene"
    reputation: int = 50  # 0-100, affects NPC interactions

    # Tracking
    clues_found: List[str] = field(default_factory=list)  # clue IDs
    locations_visited: List[str] = field(default_factory=list)
    npcs_met: List[str] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)

    # Meta
    game_time: int = 0  # in-game minutes elapsed
    playtime: int = 0   # real-world seconds played
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_item(self, item_id: str):
        """Add item to inventory"""
        if item_id not in self.inventory:
            self.inventory.append(item_id)

    def remove_item(self, item_id: str) -> bool:
        """Remove item from inventory, returns success"""
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            return True
        return False

    def has_item(self, item_id: str) -> bool:
        """Check if player has item"""
        return item_id in self.inventory

    def add_clue(self, clue_id: str):
        """Add clue to case notes"""
        if clue_id not in self.clues_found:
            self.clues_found.append(clue_id)

    def visit_location(self, location_id: str):
        """Mark location as visited"""
        self.current_location = location_id
        if location_id not in self.locations_visited:
            self.locations_visited.append(location_id)

    def meet_npc(self, npc_id: str):
        """Mark NPC as met"""
        if npc_id not in self.npcs_met:
            self.npcs_met.append(npc_id)

    def complete_quest(self, quest_id: str):
        """Mark quest as completed"""
        if quest_id not in self.completed_quests:
            self.completed_quests.append(quest_id)

    def modify_reputation(self, amount: int):
        """Change reputation (clamped 0-100)"""
        self.reputation = max(0, min(100, self.reputation + amount))

    def to_dict(self) -> dict:
        """Serialize to dictionary for saving"""
        return {
            "name": self.name,
            "stats": {
                "investigation": self.stats.investigation,
                "persuasion": self.stats.persuasion,
                "perception": self.stats.perception,
                "intuition": self.stats.intuition,
                "physical": self.stats.physical,
            },
            "inventory": self.inventory,
            "current_location": self.current_location,
            "reputation": self.reputation,
            "clues_found": self.clues_found,
            "locations_visited": self.locations_visited,
            "npcs_met": self.npcs_met,
            "completed_quests": self.completed_quests,
            "game_time": self.game_time,
            "playtime": self.playtime,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Deserialize from dictionary"""
        stats = PlayerStats(**data.get("stats", {}))
        return cls(
            name=data["name"],
            stats=stats,
            inventory=data.get("inventory", []),
            current_location=data.get("current_location", "crime_scene"),
            reputation=data.get("reputation", 50),
            clues_found=data.get("clues_found", []),
            locations_visited=data.get("locations_visited", []),
            npcs_met=data.get("npcs_met", []),
            completed_quests=data.get("completed_quests", []),
            game_time=data.get("game_time", 0),
            playtime=data.get("playtime", 0),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )
