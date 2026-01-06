"""Item and Clue models"""
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from enum import Enum


class ItemType(Enum):
    """Types of items"""
    EVIDENCE = "evidence"      # Crime evidence
    TOOL = "tool"             # Lockpick, magnifying glass, etc.
    DOCUMENT = "document"     # Letters, files, notes
    KEY_ITEM = "key_item"     # Story-critical items
    CONSUMABLE = "consumable" # One-time use items


@dataclass
class Item:
    """Game item (tools, evidence, etc.)"""
    id: str
    name: str
    description: str
    item_type: ItemType
    is_clue: bool = False  # Whether this is also a clue

    # Properties
    can_examine: bool = True
    can_use: bool = True
    can_combine: bool = False

    # Metadata
    found_at: Optional[str] = None  # location_id where found
    tags: List[str] = field(default_factory=list)  # searchable tags

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.value,
            "is_clue": self.is_clue,
            "can_examine": self.can_examine,
            "can_use": self.can_use,
            "can_combine": self.can_combine,
            "found_at": self.found_at,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=ItemType(data["item_type"]),
            is_clue=data.get("is_clue", False),
            can_examine=data.get("can_examine", True),
            can_use=data.get("can_use", True),
            can_combine=data.get("can_combine", False),
            found_at=data.get("found_at"),
            tags=data.get("tags", []),
        )


@dataclass
class Clue:
    """Investigation clue"""
    id: str
    title: str
    description: str
    category: str  # "physical", "testimony", "forensic", "digital", etc.

    # Discovery
    found_at: str  # location_id
    requires_stat: Optional[str] = None  # stat needed to find it
    requires_stat_level: int = 0

    # Connections
    related_npcs: List[str] = field(default_factory=list)  # npc_ids
    related_clues: List[str] = field(default_factory=list)  # other clue_ids
    contradicts_clues: List[str] = field(default_factory=list)  # conflicting clues

    # Deduction
    importance: int = 1  # 1-5, how critical to solving case
    unlocks_dialogue: List[str] = field(default_factory=list)  # dialogue tree nodes

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "found_at": self.found_at,
            "requires_stat": self.requires_stat,
            "requires_stat_level": self.requires_stat_level,
            "related_npcs": self.related_npcs,
            "related_clues": self.related_clues,
            "contradicts_clues": self.contradicts_clues,
            "importance": self.importance,
            "unlocks_dialogue": self.unlocks_dialogue,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Clue':
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            category=data["category"],
            found_at=data["found_at"],
            requires_stat=data.get("requires_stat"),
            requires_stat_level=data.get("requires_stat_level", 0),
            related_npcs=data.get("related_npcs", []),
            related_clues=data.get("related_clues", []),
            contradicts_clues=data.get("contradicts_clues", []),
            importance=data.get("importance", 1),
            unlocks_dialogue=data.get("unlocks_dialogue", []),
        )
