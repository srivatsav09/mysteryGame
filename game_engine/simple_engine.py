"""Simple game engine for minimal playable version"""
from typing import List, Tuple, Optional
from models.world import WorldState
from models.location import Location
from models.npc import NPC
from models.item import Item, Clue


class SimpleGameEngine:
    """Manages game state and actions for the minimal version"""

    def __init__(self, world: WorldState):
        self.world = world

    def get_current_location(self) -> Optional[Location]:
        """Get player's current location"""
        return self.world.get_current_location()

    def get_available_actions(self) -> List[dict]:
        """Get list of available actions at current location"""
        actions = []
        location = self.get_current_location()
        if not location:
            return actions

        # Examine location (always available)
        actions.append({
            "id": "examine_location",
            "text": f"Examine {location.name}",
            "type": "examine"
        })

        # Talk to NPCs
        npcs_here = self.world.get_npcs_at_location(location.id)
        for npc in npcs_here:
            actions.append({
                "id": f"talk_{npc.id}",
                "text": f"Talk to {npc.name}",
                "type": "talk",
                "target": npc.id
            })

        # Search for items/clues
        available_items = location.get_available_items()
        available_clues = location.get_available_clues()

        if available_items or available_clues:
            actions.append({
                "id": "search",
                "text": "Search for evidence",
                "type": "search"
            })

        # Travel to connected locations
        for conn_id in location.connections:
            conn_loc = self.world.get_location(conn_id)
            if conn_loc:
                can_travel, msg = location.can_travel_to(conn_id, self.world.player, self.world)
                if can_travel:
                    actions.append({
                        "id": f"travel_{conn_id}",
                        "text": f"Travel to {conn_loc.name}",
                        "type": "travel",
                        "target": conn_id
                    })

        return actions

    def perform_action(self, action_id: str) -> Tuple[str, List[str]]:
        """
        Perform an action and return (narrative, discoveries)
        narrative: String describing what happened
        discoveries: List of items/clues found
        """
        location = self.get_current_location()
        discoveries = []
        narrative = ""

        if action_id == "examine_location":
            narrative = self._examine_location(location)

        elif action_id.startswith("talk_"):
            npc_id = action_id.replace("talk_", "")
            narrative = self._talk_to_npc(npc_id)

        elif action_id == "search":
            narrative, discoveries = self._search_location(location)

        elif action_id.startswith("travel_"):
            target_loc_id = action_id.replace("travel_", "")
            narrative = self._travel_to(target_loc_id)

        else:
            narrative = "Unknown action."

        return narrative, discoveries

    def _examine_location(self, location: Location) -> str:
        """Examine the current location"""
        location.visit()
        self.world.player.visit_location(location.id)

        narrative = f"**{location.name}**\n\n{location.description}\n\n"

        # Show NPCs present
        npcs_here = self.world.get_npcs_at_location(location.id)
        if npcs_here:
            narrative += "**People here:**\n"
            for npc in npcs_here:
                narrative += f"- {npc.name}: {npc.description}\n"
            narrative += "\n"

        # Show search status
        available_items = location.get_available_items()
        available_clues = location.get_available_clues()

        if available_items or available_clues:
            narrative += "💡 This location hasn't been fully searched yet.\n"
        elif location.search_count > 0:
            narrative += "✓ You've thoroughly searched this area.\n"

        return narrative

    def _talk_to_npc(self, npc_id: str) -> str:
        """Talk to an NPC"""
        npc = self.world.get_npc(npc_id)
        if not npc:
            return "That person is not here."

        # Mark NPC as met
        self.world.player.meet_npc(npc_id)
        npc.talk_to()

        narrative = f"**Conversation with {npc.name}**\n\n"
        narrative += f"*{npc.description}*\n\n"

        # Share clues based on trust level
        shared_clues = []
        for clue_id in list(npc.will_share_clues):
            if npc.can_share_clue(clue_id):
                clue = self.world.get_clue(clue_id)
                if clue and npc.share_clue(clue_id):
                    self.world.player.add_clue(clue_id)
                    shared_clues.append(clue.title)

        if shared_clues:
            narrative += f"{npc.name} shares some information:\n"
            for clue_title in shared_clues:
                narrative += f"🔍 New clue: **{clue_title}**\n"
        else:
            narrative += f"{npc.name} is {npc.mood.value}. "
            if npc.trust_level < 30:
                narrative += "They seem reluctant to talk."
            elif npc.trust_level < 60:
                narrative += "They're cooperative but guarded."
            else:
                narrative += "They're willing to help."

        return narrative

    def _search_location(self, location: Location) -> Tuple[str, List[str]]:
        """Search location for items and clues"""
        location.search()
        discoveries = []
        narrative = "**Searching the area...**\n\n"

        # Find items
        available_items = location.get_available_items()
        for item_id in available_items[:2]:  # Max 2 items per search
            item = self.world.get_item(item_id)
            if item:
                location.take_item(item_id)
                self.world.player.add_item(item_id)
                discoveries.append(f"📦 {item.name}")
                narrative += f"Found: **{item.name}**\n{item.description}\n\n"

                # If item is also a clue
                if item.is_clue:
                    self.world.player.add_clue(item_id)

        # Find clues
        available_clues = location.get_available_clues()
        for clue_id in available_clues[:2]:  # Max 2 clues per search
            clue = self.world.get_clue(clue_id)
            if clue:
                # Check if player has required stat
                can_find = True
                if clue.requires_stat:
                    stat_value = self.world.player.stats.get_stat(clue.requires_stat)
                    can_find = stat_value >= clue.requires_stat_level

                if can_find:
                    location.find_clue(clue_id)
                    self.world.player.add_clue(clue_id)
                    discoveries.append(f"🔍 {clue.title}")
                    narrative += f"**Clue Found: {clue.title}**\n{clue.description}\n\n"
                else:
                    narrative += f"💭 You sense there's something here, but you need higher {clue.requires_stat} to find it.\n\n"

        if not discoveries:
            narrative += "You search carefully but don't find anything new.\n"

        # Update quest progress
        self._update_quest_progress()

        return narrative, discoveries

    def _travel_to(self, location_id: str) -> str:
        """Travel to a different location"""
        current_loc = self.get_current_location()
        target_loc = self.world.get_location(location_id)

        if not target_loc:
            return "That location doesn't exist."

        # Check if can travel
        can_travel, msg = current_loc.can_travel_to(location_id, self.world.player, self.world)
        if not can_travel:
            return f"Cannot travel there: {msg}"

        # Travel
        self.world.player.visit_location(location_id)
        target_loc.visit()

        # Advance time
        self.world.advance_time(15)  # 15 minutes per travel

        narrative = f"🚗 **Traveling to {target_loc.name}...**\n\n"
        narrative += self._examine_location(target_loc)
        narrative += f"\n⏰ Time: {self.world.get_time_string()}\n"

        return narrative

    def _update_quest_progress(self):
        """Update quest objectives based on player state"""
        for quest in self.world.get_active_quests():
            # Check location objectives
            for obj in quest.get_available_objectives():
                if obj.objective_type.value == "go_to_location":
                    if self.world.player.current_location == obj.target_id:
                        quest.complete_objective(obj.id)

                # Check collect item objectives
                elif obj.objective_type.value == "collect_item":
                    if obj.target_id and self.world.player.has_item(obj.target_id):
                        quest.complete_objective(obj.id)
                    # Or check quantity
                    elif not obj.target_id:
                        if len(self.world.player.inventory) >= obj.quantity:
                            quest.complete_objective(obj.id)

                # Check find clue objectives
                elif obj.objective_type.value == "find_clue":
                    if obj.target_id in self.world.player.clues_found:
                        quest.complete_objective(obj.id)

                # Check talk to NPC objectives
                elif obj.objective_type.value == "talk_to_npc":
                    if obj.target_id in self.world.player.npcs_met:
                        quest.complete_objective(obj.id)

    def get_game_stats(self) -> dict:
        """Get current game statistics"""
        return {
            "location": self.get_current_location().name if self.get_current_location() else "Unknown",
            "time": self.world.get_time_string(),
            "day": self.world.current_day,
            "reputation": self.world.player.reputation,
            "clues_found": len(self.world.player.clues_found),
            "items_collected": len(self.world.player.inventory),
            "locations_visited": len(self.world.player.locations_visited),
            "npcs_met": len(self.world.player.npcs_met)
        }

    def check_win_condition(self) -> Tuple[bool, str]:
        """Check if player has won the game"""
        # Check if main quest is complete
        main_quest = self.world.get_quest("solve_murder")
        if main_quest and main_quest.status.value == "completed":
            # Check if player has key evidence
            has_toxicology = "toxicology_report" in self.world.player.clues_found
            has_fingerprints = "fingerprint_match" in self.world.player.clues_found

            if has_toxicology and has_fingerprints:
                return True, "good"  # Good ending - solid evidence
            else:
                return True, "neutral"  # Neutral ending - quest done but missing evidence

        return False, ""
