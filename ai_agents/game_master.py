"""Game Master AI Agent - Main storyteller"""
import os
from typing import Optional
from langchain_groq import ChatGroq
from config.prompts import get_game_master_prompt, GAME_MASTER_SYSTEM_PROMPT


class GameMasterAgent:
    """AI agent that generates narrative descriptions"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Game Master agent"""
        if api_key is None:
            api_key = os.getenv("API_KEY")

        self.llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0.7,  # More creative for storytelling
            groq_api_key=api_key
        )

    def generate_location_description(self, location_name: str, location_description: str,
                                      npcs: list, has_items: bool, time: str, reputation: int) -> str:
        """Generate atmospheric location description"""

        context = {
            "location_name": location_name,
            "location_description": location_description,
            "npcs": npcs,
            "has_items": has_items,
            "time": time,
            "reputation": reputation
        }

        prompt = get_game_master_prompt("examine_location", context)

        messages = [
            {"role": "system", "content": GAME_MASTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()

    def generate_search_narrative(self, items_found: list, clues_found: list,
                                  location_name: str, time: str) -> str:
        """Generate narrative for search results"""

        context = {
            "location_name": location_name,
            "items_found": items_found,
            "clues_found": clues_found,
            "time": time
        }

        prompt = get_game_master_prompt("search_location", context)

        messages = [
            {"role": "system", "content": GAME_MASTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()

    def generate_travel_narrative(self, from_location: str, to_location: str,
                                  time: str, method: str = "driving") -> str:
        """Generate travel transition narrative"""

        context = {
            "from_location": from_location,
            "to_location": to_location,
            "time": time,
            "method": method
        }

        prompt = get_game_master_prompt("travel", context)

        messages = [
            {"role": "system", "content": GAME_MASTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()

    def generate_custom_narrative(self, situation: str, context: dict) -> str:
        """Generate custom narrative for any situation"""

        prompt = f"""
{GAME_MASTER_SYSTEM_PROMPT}

Situation: {situation}

Context:
{chr(10).join(f"- {k}: {v}" for k, v in context.items())}

Generate an appropriate narrative response (2-3 sentences).
"""

        messages = [
            {"role": "system", "content": GAME_MASTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()
