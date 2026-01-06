"""Quest/Investigation model with dependency graph"""
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class QuestStatus(Enum):
    """Quest completion status"""
    LOCKED = "locked"          # Not available yet
    AVAILABLE = "available"    # Can start
    ACTIVE = "active"         # Currently pursuing
    COMPLETED = "completed"   # Finished
    FAILED = "failed"         # Failed (optional)


class ObjectiveType(Enum):
    """Types of quest objectives"""
    FIND_CLUE = "find_clue"
    TALK_TO_NPC = "talk_to_npc"
    GO_TO_LOCATION = "go_to_location"
    COLLECT_ITEM = "collect_item"
    CONFRONT_NPC = "confront_npc"
    SOLVE_PUZZLE = "solve_puzzle"
    MAKE_DEDUCTION = "make_deduction"


@dataclass
class QuestObjective:
    """Individual quest objective"""
    id: str
    description: str
    objective_type: ObjectiveType

    # Requirements
    target_id: Optional[str] = None  # clue_id, npc_id, location_id, or item_id
    quantity: int = 1

    # State
    completed: bool = False
    progress: int = 0

    # Dependencies (DAG structure)
    requires_objectives: List[str] = field(default_factory=list)  # objective_ids

    def is_available(self, completed_objectives: Set[str]) -> bool:
        """Check if objective is available based on dependencies"""
        return all(req in completed_objectives for req in self.requires_objectives)

    def advance_progress(self, amount: int = 1) -> bool:
        """Advance objective progress, returns True if completed"""
        self.progress = min(self.quantity, self.progress + amount)
        if self.progress >= self.quantity:
            self.completed = True
            return True
        return False


@dataclass
class Quest:
    """Investigation or quest"""
    id: str
    title: str
    description: str
    category: str = "main"  # main, side, tutorial

    # Status
    status: QuestStatus = QuestStatus.LOCKED

    # Objectives (can have dependencies - DAG)
    objectives: Dict[str, QuestObjective] = field(default_factory=dict)
    completed_objectives: Set[str] = field(default_factory=set)

    # Requirements to unlock
    requires_quests: List[str] = field(default_factory=list)  # quest_ids
    requires_clues: List[str] = field(default_factory=list)   # clue_ids
    requires_location: Optional[str] = None

    # Rewards
    reward_reputation: int = 0
    reward_items: List[str] = field(default_factory=list)
    unlocks_locations: List[str] = field(default_factory=list)
    unlocks_npcs: List[str] = field(default_factory=list)

    # Giver
    given_by: Optional[str] = None  # npc_id

    def add_objective(self, objective: QuestObjective):
        """Add objective to quest"""
        self.objectives[objective.id] = objective

    def get_available_objectives(self) -> List[QuestObjective]:
        """Get objectives that can be worked on"""
        return [
            obj for obj in self.objectives.values()
            if not obj.completed and obj.is_available(self.completed_objectives)
        ]

    def complete_objective(self, objective_id: str) -> bool:
        """Mark objective as completed"""
        if objective_id in self.objectives and not self.objectives[objective_id].completed:
            self.objectives[objective_id].completed = True
            self.completed_objectives.add(objective_id)

            # Check if all objectives complete
            if all(obj.completed for obj in self.objectives.values()):
                self.status = QuestStatus.COMPLETED
                return True
        return False

    def is_unlocked(self, player) -> bool:
        """Check if quest can be started"""
        # Check quest dependencies
        if not all(quest_id in player.completed_quests for quest_id in self.requires_quests):
            return False

        # Check clue dependencies
        if not all(clue_id in player.clues_found for clue_id in self.requires_clues):
            return False

        # Check location requirement
        if self.requires_location and player.current_location != self.requires_location:
            return False

        return True

    def start(self):
        """Start the quest"""
        if self.status == QuestStatus.AVAILABLE:
            self.status = QuestStatus.ACTIVE

    def complete(self):
        """Complete the quest"""
        self.status = QuestStatus.COMPLETED

    def fail(self):
        """Fail the quest"""
        self.status = QuestStatus.FAILED

    def get_progress_percentage(self) -> float:
        """Get completion percentage"""
        if not self.objectives:
            return 0.0
        completed = len(self.completed_objectives)
        total = len(self.objectives)
        return (completed / total) * 100

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "status": self.status.value,
            "objectives": {
                obj_id: {
                    "id": obj.id,
                    "description": obj.description,
                    "objective_type": obj.objective_type.value,
                    "target_id": obj.target_id,
                    "quantity": obj.quantity,
                    "completed": obj.completed,
                    "progress": obj.progress,
                    "requires_objectives": obj.requires_objectives,
                }
                for obj_id, obj in self.objectives.items()
            },
            "completed_objectives": list(self.completed_objectives),
            "requires_quests": self.requires_quests,
            "requires_clues": self.requires_clues,
            "requires_location": self.requires_location,
            "reward_reputation": self.reward_reputation,
            "reward_items": self.reward_items,
            "unlocks_locations": self.unlocks_locations,
            "unlocks_npcs": self.unlocks_npcs,
            "given_by": self.given_by,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Quest':
        """Deserialize from dictionary"""
        quest = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            category=data.get("category", "main"),
            status=QuestStatus(data.get("status", "locked")),
            completed_objectives=set(data.get("completed_objectives", [])),
            requires_quests=data.get("requires_quests", []),
            requires_clues=data.get("requires_clues", []),
            requires_location=data.get("requires_location"),
            reward_reputation=data.get("reward_reputation", 0),
            reward_items=data.get("reward_items", []),
            unlocks_locations=data.get("unlocks_locations", []),
            unlocks_npcs=data.get("unlocks_npcs", []),
            given_by=data.get("given_by"),
        )

        # Reconstruct objectives
        for obj_id, obj_data in data.get("objectives", {}).items():
            objective = QuestObjective(
                id=obj_data["id"],
                description=obj_data["description"],
                objective_type=ObjectiveType(obj_data["objective_type"]),
                target_id=obj_data.get("target_id"),
                quantity=obj_data.get("quantity", 1),
                completed=obj_data.get("completed", False),
                progress=obj_data.get("progress", 0),
                requires_objectives=obj_data.get("requires_objectives", []),
            )
            quest.objectives[obj_id] = objective

        return quest
