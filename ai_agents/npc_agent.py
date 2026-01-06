"""NPC AI Agent - Generates dynamic NPC dialogue"""
import os
from typing import Optional
from langchain_groq import ChatGroq
from config.prompts import get_npc_dialogue_prompt, NPC_AGENT_SYSTEM_PROMPT
from models.npc import NPC


class NPCAgent:
    """AI agent for individual NPC dialogue"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the NPC agent"""
        if api_key is None:
            api_key = os.getenv("API_KEY")

        self.llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0.8,  # More personality variation
            groq_api_key=api_key
        )

    def generate_dialogue(self, npc: NPC, player_action: str = "Starting conversation",
                         clues_shown: list = None) -> str:
        """Generate NPC dialogue response"""

        if clues_shown is None:
            clues_shown = []

        # Prepare NPC data
        npc_data = {
            "name": npc.name,
            "role": npc.role.value,
            "description": npc.description,
            "personality_traits": npc.personality_traits,
            "trust_level": npc.trust_level,
            "mood": npc.mood.value,
            "times_talked": npc.memory.times_talked,
            "topics_discussed": list(npc.memory.topics_discussed),
            "secrets": npc.secrets,
            "shareable_clues": list(npc.will_share_clues)
        }

        context = {
            "player_action": player_action,
            "clues_shown": clues_shown
        }

        prompt = get_npc_dialogue_prompt(npc_data, context)

        messages = [
            {"role": "system", "content": NPC_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()

    def generate_reaction_to_evidence(self, npc: NPC, evidence_name: str,
                                     evidence_description: str) -> str:
        """Generate NPC reaction when shown evidence"""

        npc_data = {
            "name": npc.name,
            "role": npc.role.value,
            "description": npc.description,
            "personality_traits": npc.personality_traits,
            "trust_level": npc.trust_level,
            "mood": npc.mood.value,
            "times_talked": npc.memory.times_talked,
            "topics_discussed": list(npc.memory.topics_discussed),
            "secrets": npc.secrets,
            "shareable_clues": list(npc.will_share_clues)
        }

        context = {
            "player_action": f"Shows {evidence_name}: {evidence_description}",
            "clues_shown": [evidence_name]
        }

        prompt = get_npc_dialogue_prompt(npc_data, context)

        messages = [
            {"role": "system", "content": NPC_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()

    def generate_greeting(self, npc: NPC) -> str:
        """Generate initial greeting from NPC"""

        if npc.memory.times_talked == 0:
            player_action = "Player approaches for the first time"
        else:
            player_action = f"Player returns (talked {npc.memory.times_talked} times before)"

        return self.generate_dialogue(npc, player_action)
