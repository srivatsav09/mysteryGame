"""AI-Enhanced Game Engine with multi-agent system"""
from typing import List, Tuple, Optional
from models.world import WorldState
from models.location import Location
from models.npc import NPC
from ai_agents.game_master import GameMasterAgent
from ai_agents.npc_agent import NPCAgent


class AIEnhancedGameEngine:
    """Game engine with AI-generated narratives"""

    def __init__(self, world: WorldState, use_ai: bool = True):
        """
        Initialize the AI-enhanced engine

        Args:
            world: Game world state
            use_ai: Whether to use AI for narrative generation (False for testing)
        """
        self.world = world
        self.use_ai = use_ai

        if use_ai:
            try:
                self.game_master = GameMasterAgent()
                self.npc_agent = NPCAgent()
            except Exception as e:
                print(f"Warning: AI initialization failed: {e}")
                print("Falling back to static narratives")
                self.use_ai = False

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
        """Examine the current location with AI-generated description"""
        location.visit()
        self.world.player.visit_location(location.id)

        if self.use_ai:
            try:
                npcs_here = self.world.get_npcs_at_location(location.id)
                npc_names = [npc.name for npc in npcs_here]

                has_items = (len(location.get_available_items()) > 0 or
                           len(location.get_available_clues()) > 0)

                narrative = self.game_master.generate_location_description(
                    location_name=location.name,
                    location_description=location.description,
                    npcs=npc_names,
                    has_items=has_items,
                    time=self.world.get_time_string(),
                    reputation=self.world.player.reputation
                )

                return f"**{location.name}**\n\n{narrative}"

            except Exception as e:
                print(f"AI generation failed: {e}")
                # Fall back to static description

        # Static fallback
        narrative = f"**{location.name}**\n\n{location.description}\n\n"

        npcs_here = self.world.get_npcs_at_location(location.id)
        if npcs_here:
            narrative += "**People here:**\n"
            for npc in npcs_here:
                narrative += f"- {npc.name}: {npc.description}\n"
            narrative += "\n"

        available_items = location.get_available_items()
        available_clues = location.get_available_clues()

        if available_items or available_clues:
            narrative += "💡 This location hasn't been fully searched yet.\n"
        elif location.search_count > 0:
            narrative += "✓ You've thoroughly searched this area.\n"

        return narrative

    def _talk_to_npc(self, npc_id: str) -> str:
        """Talk to an NPC with AI-generated dialogue"""
        npc = self.world.get_npc(npc_id)
        if not npc:
            return "That person is not here."

        # Mark NPC as met
        self.world.player.meet_npc(npc_id)
        npc.talk_to()

        narrative = f"**Conversation with {npc.name}**\n\n"

        # AI-generated dialogue
        if self.use_ai:
            try:
                dialogue = self.npc_agent.generate_dialogue(npc)
                narrative += f'"{dialogue}"\n\n'
                narrative += f"*{npc.name} seems {npc.mood.value}*\n\n"
            except Exception as e:
                print(f"AI dialogue generation failed: {e}")
                # Fall back to static

        # Share clues based on trust level
        shared_clues = []
        for clue_id in list(npc.will_share_clues):
            if npc.can_share_clue(clue_id):
                clue = self.world.get_clue(clue_id)
                if clue and npc.share_clue(clue_id):
                    self.world.player.add_clue(clue_id)
                    shared_clues.append(clue.title)

        if shared_clues:
            narrative += f"**{npc.name} shares information:**\n"
            for clue_title in shared_clues:
                narrative += f"🔍 New clue: **{clue_title}**\n"

        return narrative

    def _search_location(self, location: Location) -> Tuple[str, List[str]]:
        """Search location for items and clues"""
        location.search()
        discoveries = []

        items_found_names = []
        clues_found_names = []

        # Find items
        available_items = location.get_available_items()
        for item_id in available_items[:2]:
            item = self.world.get_item(item_id)
            if item:
                location.take_item(item_id)
                self.world.player.add_item(item_id)
                discoveries.append(f"📦 {item.name}")
                items_found_names.append(item.name)

                if item.is_clue:
                    self.world.player.add_clue(item_id)

        # Find clues
        available_clues = location.get_available_clues()
        for clue_id in available_clues[:2]:
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
                    clues_found_names.append(clue.title)

        # Generate AI narrative for search
        if self.use_ai and (items_found_names or clues_found_names):
            try:
                narrative = self.game_master.generate_search_narrative(
                    items_found=items_found_names,
                    clues_found=clues_found_names,
                    location_name=location.name,
                    time=self.world.get_time_string()
                )
                narrative = f"**Searching the area...**\n\n{narrative}"
            except Exception as e:
                print(f"AI search narrative failed: {e}")
                narrative = self._generate_static_search_narrative(
                    items_found_names, clues_found_names
                )
        else:
            narrative = self._generate_static_search_narrative(
                items_found_names, clues_found_names
            )

        # Update quest progress
        self._update_quest_progress()

        return narrative, discoveries

    def _generate_static_search_narrative(self, items_found: list, clues_found: list) -> str:
        """Generate static search narrative as fallback"""
        narrative = "**Searching the area...**\n\n"

        for item_name in items_found:
            narrative += f"Found: **{item_name}**\n"

        for clue_name in clues_found:
            narrative += f"**Clue Found: {clue_name}**\n"

        if not items_found and not clues_found:
            narrative += "You search carefully but don't find anything new.\n"

        return narrative

    def _travel_to(self, location_id: str) -> str:
        """Travel to a different location"""
        current_loc = self.get_current_location()
        target_loc = self.world.get_location(location_id)

        if not target_loc:
            return "That location doesn't exist."

        can_travel, msg = current_loc.can_travel_to(location_id, self.world.player, self.world)
        if not can_travel:
            return f"Cannot travel there: {msg}"

        # Generate AI travel narrative
        if self.use_ai:
            try:
                travel_narrative = self.game_master.generate_travel_narrative(
                    from_location=current_loc.name,
                    to_location=target_loc.name,
                    time=self.world.get_time_string()
                )
            except Exception as e:
                print(f"AI travel narrative failed: {e}")
                travel_narrative = f"You travel from {current_loc.name} to {target_loc.name}."
        else:
            travel_narrative = f"You travel from {current_loc.name} to {target_loc.name}."

        # Travel
        self.world.player.visit_location(location_id)
        target_loc.visit()
        self.world.advance_time(15)

        narrative = f"🚗 **Traveling to {target_loc.name}...**\n\n"
        narrative += f"{travel_narrative}\n\n"
        narrative += f"⏰ Time: {self.world.get_time_string()}\n\n"

        # Examine new location
        narrative += self._examine_location(target_loc)

        return narrative

    def _update_quest_progress(self):
        """Update quest objectives based on player state"""
        for quest in self.world.get_active_quests():
            for obj in quest.get_available_objectives():
                if obj.objective_type.value == "go_to_location":
                    if self.world.player.current_location == obj.target_id:
                        quest.complete_objective(obj.id)

                elif obj.objective_type.value == "collect_item":
                    if obj.target_id and self.world.player.has_item(obj.target_id):
                        quest.complete_objective(obj.id)
                    elif not obj.target_id:
                        if len(self.world.player.inventory) >= obj.quantity:
                            quest.complete_objective(obj.id)

                elif obj.objective_type.value == "find_clue":
                    if obj.target_id in self.world.player.clues_found:
                        quest.complete_objective(obj.id)

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
        main_quest = self.world.get_quest("solve_murder")
        if main_quest and main_quest.status.value == "completed":
            has_toxicology = "toxicology_report" in self.world.player.clues_found
            has_fingerprints = "fingerprint_match" in self.world.player.clues_found

            if has_toxicology and has_fingerprints:
                return True, "good"
            else:
                return True, "neutral"

        return False, ""
