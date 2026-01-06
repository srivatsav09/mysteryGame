"""Location model with graph connections"""
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class LocationState(Enum):
    """Possible states of a location"""
    LOCKED = "locked"           # Can't visit yet
    AVAILABLE = "available"     # Can visit
    ACTIVE = "active"          # Currently here
    SEARCHED = "searched"      # Thoroughly searched
    COMPLETED = "completed"    # Nothing left to do


@dataclass
class LocationRequirement:
    """Requirements to unlock/access a location"""
    requires_item: Optional[str] = None      # item_id needed
    requires_clue: Optional[str] = None      # clue_id needed
    requires_quest: Optional[str] = None     # quest_id completed
    requires_npc_trust: Optional[tuple] = None  # (npc_id, min_trust_level)

    def is_met(self, player, world_state) -> bool:
        """Check if requirements are met"""
        if self.requires_item and not player.has_item(self.requires_item):
            return False
        if self.requires_clue and self.requires_clue not in player.clues_found:
            return False
        if self.requires_quest and self.requires_quest not in player.completed_quests:
            return False
        if self.requires_npc_trust:
            npc_id, min_trust = self.requires_npc_trust
            npc = world_state.get_npc(npc_id)
            if not npc or npc.trust_level < min_trust:
                return False
        return True


@dataclass
class Location:
    """A location in the game world"""
    id: str
    name: str
    description: str

    # Graph connections
    connections: List[str] = field(default_factory=list)  # connected location_ids
    connection_requirements: Dict[str, LocationRequirement] = field(default_factory=dict)

    # State
    state: LocationState = LocationState.AVAILABLE
    visited: bool = False
    search_count: int = 0  # How many times searched

    # Available entities
    npcs_present: List[str] = field(default_factory=list)  # npc_ids at this location
    items_available: List[str] = field(default_factory=list)  # item_ids to find
    clues_available: List[str] = field(default_factory=list)  # clue_ids to discover

    # Collected/found entities
    items_taken: Set[str] = field(default_factory=set)
    clues_found: Set[str] = field(default_factory=set)

    # Time and events
    time_of_day_affects: bool = False  # Whether time changes this location
    weather_affects: bool = False      # Whether weather changes this location

    # Metadata
    category: str = "general"  # "crime_scene", "public", "private", "official"
    danger_level: int = 0      # 0-5, affects random events

    def add_connection(self, location_id: str, requirement: Optional[LocationRequirement] = None):
        """Add a connection to another location"""
        if location_id not in self.connections:
            self.connections.append(location_id)
        if requirement:
            self.connection_requirements[location_id] = requirement

    def can_travel_to(self, location_id: str, player, world_state) -> tuple[bool, str]:
        """Check if can travel to connected location"""
        if location_id not in self.connections:
            return False, "Location not connected"

        if location_id in self.connection_requirements:
            req = self.connection_requirements[location_id]
            if not req.is_met(player, world_state):
                return False, "Requirements not met"

        return True, "Can travel"

    def get_available_items(self) -> List[str]:
        """Get items not yet taken"""
        return [item for item in self.items_available if item not in self.items_taken]

    def get_available_clues(self) -> List[str]:
        """Get clues not yet found"""
        return [clue for clue in self.clues_available if clue not in self.clues_found]

    def take_item(self, item_id: str) -> bool:
        """Mark item as taken"""
        if item_id in self.items_available and item_id not in self.items_taken:
            self.items_taken.add(item_id)
            return True
        return False

    def find_clue(self, clue_id: str) -> bool:
        """Mark clue as found"""
        if clue_id in self.clues_available and clue_id not in self.clues_found:
            self.clues_found.add(clue_id)
            return True
        return False

    def visit(self):
        """Mark location as visited"""
        self.visited = True
        if self.state == LocationState.AVAILABLE:
            self.state = LocationState.ACTIVE

    def search(self):
        """Increment search count"""
        self.search_count += 1
        if len(self.get_available_clues()) == 0 and len(self.get_available_items()) == 0:
            self.state = LocationState.SEARCHED

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": self.connections,
            "state": self.state.value,
            "visited": self.visited,
            "search_count": self.search_count,
            "npcs_present": self.npcs_present,
            "items_available": self.items_available,
            "clues_available": self.clues_available,
            "items_taken": list(self.items_taken),
            "clues_found": list(self.clues_found),
            "time_of_day_affects": self.time_of_day_affects,
            "weather_affects": self.weather_affects,
            "category": self.category,
            "danger_level": self.danger_level,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Location':
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            connections=data.get("connections", []),
            state=LocationState(data.get("state", "available")),
            visited=data.get("visited", False),
            search_count=data.get("search_count", 0),
            npcs_present=data.get("npcs_present", []),
            items_available=data.get("items_available", []),
            clues_available=data.get("clues_available", []),
            items_taken=set(data.get("items_taken", [])),
            clues_found=set(data.get("clues_found", [])),
            time_of_day_affects=data.get("time_of_day_affects", False),
            weather_affects=data.get("weather_affects", False),
            category=data.get("category", "general"),
            danger_level=data.get("danger_level", 0),
        )
