"""Mystery Game v2 - Minimal Playable Version with New Models"""
import streamlit as st
from config.sample_mystery import create_sample_mystery
from game_engine.simple_engine import SimpleGameEngine


# Page config
st.set_page_config(
    page_title="Mystery Detective Game",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if "world" not in st.session_state:
    st.session_state.world = create_sample_mystery()
    st.session_state.engine = SimpleGameEngine(st.session_state.world)
    st.session_state.narrative_history = []
    st.session_state.current_action = None

world = st.session_state.world
engine = st.session_state.engine
player = world.player


def reset_game():
    """Reset the game to initial state"""
    st.session_state.world = create_sample_mystery()
    st.session_state.engine = SimpleGameEngine(st.session_state.world)
    st.session_state.narrative_history = []
    st.session_state.current_action = None


# Custom CSS
st.markdown("""
<style>
    .stat-box {
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #ff4d4d;
        margin: 5px 0;
    }
    .action-card {
        background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .action-card:hover {
        border-color: #ff4d4d;
        box-shadow: 0 0 10px rgba(255, 77, 77, 0.3);
    }
    .clue-box {
        background-color: #2a1a1a;
        padding: 10px;
        border-left: 3px solid #ffa500;
        border-radius: 5px;
        margin: 5px 0;
    }
    .narrative-box {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🔍 Mystery Detective Game")
st.markdown("### The Penthouse Murder")

# Check win condition
game_won, ending_type = engine.check_win_condition()

if game_won:
    st.balloons()
    st.success(f"## 🎉 Case Solved! ({ending_type.upper()} ENDING)")

    if ending_type == "good":
        st.markdown("""
        **Excellent work, Detective!**

        You've gathered all the critical evidence:
        - Toxicology report proving Marcus was drugged
        - Fingerprint match placing Sarah at the scene
        - Financial records showing the motive

        Sarah Chen has confessed to the murder. She drugged Marcus's wine, confronted him about being forced out of the company, and pushed him during the struggle. The broken window was from the fall.

        Your thorough investigation has brought justice for Marcus Blackwell.
        """)
    else:
        st.markdown("""
        **Case Closed... but questions remain.**

        You've completed the investigation, but some evidence gaps remain. The case will proceed to trial, but it might not be airtight.

        Consider gathering more forensic evidence next time for a stronger case.
        """)

    if st.button("🔄 Start New Case"):
        reset_game()
        st.rerun()

else:
    # Sidebar - Player Stats & Info
    with st.sidebar:
        st.markdown("## 👤 Detective Profile")

        # Stats
        st.markdown("### Skills")
        stats = player.stats
        st.markdown(f"""
        <div class="stat-box">
        🔍 Investigation: {stats.investigation}/10<br>
        💬 Persuasion: {stats.persuasion}/10<br>
        👁️ Perception: {stats.perception}/10<br>
        🧠 Intuition: {stats.intuition}/10<br>
        💪 Physical: {stats.physical}/10
        </div>
        """, unsafe_allow_html=True)

        # Reputation
        st.markdown("### Reputation")
        st.progress(player.reputation / 100)
        st.text(f"{player.reputation}/100")

        # Game stats
        game_stats = engine.get_game_stats()
        st.markdown("### Progress")
        st.markdown(f"""
        <div class="stat-box">
        ⏰ Time: {game_stats['time']}<br>
        📅 Day: {game_stats['day']}<br>
        🔍 Clues: {game_stats['clues_found']}<br>
        📦 Items: {game_stats['items_collected']}<br>
        👥 NPCs Met: {game_stats['npcs_met']}<br>
        📍 Locations: {game_stats['locations_visited']}
        </div>
        """, unsafe_allow_html=True)

        # Inventory
        st.markdown("### 📦 Inventory")
        if player.inventory:
            for item_id in player.inventory:
                item = world.get_item(item_id)
                if item:
                    st.markdown(f"- {item.name}")
        else:
            st.text("(empty)")

        # Clues
        st.markdown("### 🔍 Clues Found")
        if player.clues_found:
            for clue_id in player.clues_found:
                clue = world.get_clue(clue_id)
                if clue:
                    with st.expander(f"{'⭐' * clue.importance} {clue.title}"):
                        st.markdown(f"*{clue.category}*")
                        st.text(clue.description)
        else:
            st.text("No clues yet")

        st.markdown("---")

        # Active Quests
        st.markdown("### 📋 Active Quests")
        active_quests = world.get_active_quests()
        for quest in active_quests:
            with st.expander(f"{quest.title} - {quest.get_progress_percentage():.0f}%"):
                st.text(quest.description)
                st.markdown("**Objectives:**")
                for obj in quest.objectives.values():
                    status = "✅" if obj.completed else "⬜"
                    st.text(f"{status} {obj.description}")

        if st.button("🔄 Reset Game"):
            reset_game()
            st.rerun()

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("## 📖 Investigation")

        # Show current location
        current_loc = engine.get_current_location()
        if current_loc:
            st.markdown(f"### 📍 Current Location: {current_loc.name}")

        # Show latest narrative
        if st.session_state.narrative_history:
            latest = st.session_state.narrative_history[-1]
            st.markdown(f"""
            <div class="narrative-box">
            {latest}
            </div>
            """, unsafe_allow_html=True)

        # Available actions
        st.markdown("### 🎯 Available Actions")

        actions = engine.get_available_actions()

        if actions:
            # Group actions by type
            action_types = {
                "examine": [],
                "talk": [],
                "search": [],
                "travel": []
            }

            for action in actions:
                action_types[action["type"]].append(action)

            # Display examine actions
            if action_types["examine"]:
                st.markdown("**📋 Examine:**")
                for action in action_types["examine"]:
                    if st.button(action["text"], key=action["id"], use_container_width=True):
                        narrative, discoveries = engine.perform_action(action["id"])
                        st.session_state.narrative_history.append(narrative)
                        st.rerun()

            # Display talk actions
            if action_types["talk"]:
                st.markdown("**💬 Talk:**")
                for action in action_types["talk"]:
                    npc = world.get_npc(action["target"])
                    button_text = f"{action['text']} ({npc.mood.value})"
                    if st.button(button_text, key=action["id"], use_container_width=True):
                        narrative, discoveries = engine.perform_action(action["id"])
                        st.session_state.narrative_history.append(narrative)
                        st.rerun()

            # Display search actions
            if action_types["search"]:
                st.markdown("**🔍 Search:**")
                for action in action_types["search"]:
                    if st.button(action["text"], key=action["id"], use_container_width=True):
                        narrative, discoveries = engine.perform_action(action["id"])
                        st.session_state.narrative_history.append(narrative)
                        if discoveries:
                            st.success(f"Found {len(discoveries)} item(s)!")
                        st.rerun()

            # Display travel actions
            if action_types["travel"]:
                st.markdown("**🚗 Travel:**")
                for action in action_types["travel"]:
                    if st.button(action["text"], key=action["id"], use_container_width=True):
                        narrative, discoveries = engine.perform_action(action["id"])
                        st.session_state.narrative_history.append(narrative)
                        st.rerun()

    with col2:
        st.markdown("## 📚 Case Notes")

        # Show quest progress
        main_quest = world.get_quest("solve_murder")
        if main_quest:
            st.markdown("### Current Objectives")
            available_objectives = main_quest.get_available_objectives()

            if available_objectives:
                for obj in available_objectives:
                    st.markdown(f"""
                    <div class="clue-box">
                    🎯 {obj.description}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                completed_count = len(main_quest.completed_objectives)
                total_count = len(main_quest.objectives)
                if completed_count == total_count:
                    st.success("All objectives complete! Review your evidence.")
                else:
                    st.info("Complete previous objectives to unlock more.")

        # Show related NPCs for found clues
        if player.clues_found:
            st.markdown("### 🔗 Clue Connections")
            all_related_npcs = set()
            for clue_id in player.clues_found:
                clue = world.get_clue(clue_id)
                if clue and clue.related_npcs:
                    all_related_npcs.update(clue.related_npcs)

            if all_related_npcs:
                for npc_id in all_related_npcs:
                    npc = world.get_npc(npc_id)
                    if npc:
                        st.markdown(f"- **{npc.name}** ({npc.role.value})")

        # Investigation hints
        st.markdown("### 💡 Tips")
        st.markdown("""
        <div class="clue-box">
        • Talk to everyone at each location<br>
        • Search thoroughly for evidence<br>
        • Higher investigation skill finds more clues<br>
        • Trust levels affect what NPCs share<br>
        • Some locations require specific items/clues
        </div>
        """, unsafe_allow_html=True)

        # History
        if len(st.session_state.narrative_history) > 1:
            with st.expander("📜 Investigation History"):
                for i, narrative in enumerate(reversed(st.session_state.narrative_history[:-1])):
                    st.markdown(f"**--- Step {len(st.session_state.narrative_history) - i - 1} ---**")
                    st.markdown(narrative)
                    st.markdown("---")
