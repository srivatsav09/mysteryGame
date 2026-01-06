"""Mystery Game v3 - AI-Enhanced with Interactive Map"""
import streamlit as st
from config.sample_mystery import create_sample_mystery
from game_engine.ai_enhanced_engine import AIEnhancedGameEngine
from ui.map_visualizer import MapVisualizer


# Page config
st.set_page_config(
    page_title="Mystery Detective Game - AI Enhanced",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if "world" not in st.session_state:
    st.session_state.world = create_sample_mystery()
    st.session_state.engine = AIEnhancedGameEngine(st.session_state.world, use_ai=True)
    st.session_state.narrative_history = []
    st.session_state.show_map = True

world = st.session_state.world
engine = st.session_state.engine
player = world.player


def reset_game():
    """Reset the game to initial state"""
    st.session_state.world = create_sample_mystery()
    st.session_state.engine = AIEnhancedGameEngine(st.session_state.world, use_ai=True)
    st.session_state.narrative_history = []


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
    .narrative-box {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
        margin: 10px 0;
        font-size: 15px;
        line-height: 1.6;
    }
    .clue-box {
        background-color: #2a1a1a;
        padding: 10px;
        border-left: 3px solid #ffa500;
        border-radius: 5px;
        margin: 5px 0;
    }
    .action-button {
        margin: 3px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🔍 Mystery Detective Game")
    st.markdown("### The Penthouse Murder - AI Enhanced")

with col2:
    if st.button("🗺️ Toggle Map" if not st.session_state.show_map else "🗺️ Hide Map"):
        st.session_state.show_map = not st.session_state.show_map
        st.rerun()

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
        📍 Locations: {game_stats['locations_visited']}/{len(world.locations)}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Mini map in sidebar
        MapVisualizer.render_mini_map(world)

        st.markdown("---")

        # Inventory
        st.markdown("### 📦 Inventory")
        if player.inventory:
            for item_id in player.inventory:
                item = world.get_item(item_id)
                if item:
                    with st.expander(f"📦 {item.name}"):
                        st.markdown(f"*{item.item_type.value}*")
                        st.text(item.description)
        else:
            st.text("(empty)")

        # Clues
        st.markdown("### 🔍 Clues Found")
        if player.clues_found:
            for clue_id in player.clues_found:
                clue = world.get_clue(clue_id)
                if clue:
                    with st.expander(f"{'⭐' * clue.importance} {clue.title}"):
                        st.markdown(f"*Category: {clue.category}*")
                        st.text(clue.description)
                        if clue.related_npcs:
                            st.markdown("**Related to:**")
                            for npc_id in clue.related_npcs:
                                npc = world.get_npc(npc_id)
                                if npc:
                                    st.text(f"- {npc.name}")
        else:
            st.text("No clues yet")

        st.markdown("---")

        if st.button("🔄 Reset Game", use_container_width=True):
            reset_game()
            st.rerun()

    # Main content layout
    if st.session_state.show_map:
        # Show map at top
        MapVisualizer.render_map(world)
        st.markdown("---")

    # Content columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("## 📖 Investigation")

        # Show latest narrative
        if st.session_state.narrative_history:
            latest = st.session_state.narrative_history[-1]
            st.markdown(f"""
            <div class="narrative-box">
            {latest}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Start your investigation by examining the crime scene.")

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
                cols = st.columns(1)
                for action in action_types["examine"]:
                    if cols[0].button(f"🔍 {action['text']}", key=action["id"], use_container_width=True):
                        with st.spinner("Examining..."):
                            narrative, discoveries = engine.perform_action(action["id"])
                            st.session_state.narrative_history.append(narrative)
                            st.rerun()

            # Display talk actions
            if action_types["talk"]:
                st.markdown("**💬 Talk:**")
                for action in action_types["talk"]:
                    npc = world.get_npc(action["target"])
                    trust_indicator = "🟢" if npc.trust_level >= 60 else "🟡" if npc.trust_level >= 30 else "🔴"
                    button_text = f"{trust_indicator} {action['text']} ({npc.mood.value})"

                    if st.button(button_text, key=action["id"], use_container_width=True):
                        with st.spinner(f"Talking to {npc.name}..."):
                            narrative, discoveries = engine.perform_action(action["id"])
                            st.session_state.narrative_history.append(narrative)
                            st.rerun()

            # Display search actions
            if action_types["search"]:
                st.markdown("**🔍 Search:**")
                for action in action_types["search"]:
                    if st.button(f"🔎 {action['text']}", key=action["id"], use_container_width=True):
                        with st.spinner("Searching..."):
                            narrative, discoveries = engine.perform_action(action["id"])
                            st.session_state.narrative_history.append(narrative)
                            if discoveries:
                                st.success(f"Found {len(discoveries)} item(s)!")
                            st.rerun()

            # Display travel actions
            if action_types["travel"]:
                st.markdown("**🚗 Travel:**")
                for action in action_types["travel"]:
                    if st.button(f"🗺️ {action['text']}", key=action["id"], use_container_width=True):
                        with st.spinner("Traveling..."):
                            narrative, discoveries = engine.perform_action(action["id"])
                            st.session_state.narrative_history.append(narrative)
                            st.rerun()

    with col2:
        st.markdown("## 📚 Case Notes")

        # Active quest
        main_quest = world.get_quest("solve_murder")
        if main_quest:
            st.markdown(f"### 📋 {main_quest.title}")
            progress = main_quest.get_progress_percentage()
            st.progress(progress / 100)
            st.text(f"{progress:.0f}% Complete")

            st.markdown("#### Current Objectives")
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
                    st.success("✅ All objectives complete!")
                else:
                    st.info("Complete previous objectives to unlock more.")

            # Show completed objectives
            if main_quest.completed_objectives:
                with st.expander(f"✅ Completed ({len(main_quest.completed_objectives)})"):
                    for obj_id in main_quest.completed_objectives:
                        obj = main_quest.objectives.get(obj_id)
                        if obj:
                            st.text(f"✓ {obj.description}")

        # NPCs met
        if player.npcs_met:
            st.markdown("### 👥 People Met")
            for npc_id in player.npcs_met:
                npc = world.get_npc(npc_id)
                if npc:
                    trust_bar = "🟢" * (npc.trust_level // 20) + "⚪" * (5 - (npc.trust_level // 20))
                    with st.expander(f"{npc.name} - {npc.role.value}"):
                        st.text(f"Trust: {trust_bar}")
                        st.text(f"Mood: {npc.mood.value}")
                        st.text(f"Talked: {npc.memory.times_talked} times")

        # Investigation tips
        st.markdown("### 💡 Detective Tips")
        st.markdown("""
        <div class="clue-box">
        • Talk to everyone - NPCs remember conversations<br>
        • Search thoroughly - items may require high Investigation<br>
        • Build trust - helpful NPCs share more info<br>
        • Check the map - some areas are locked<br>
        • Follow the quest objectives<br>
        • Connect the clues - who, what, when, where, why
        </div>
        """, unsafe_allow_html=True)

        # AI Status
        if engine.use_ai:
            st.markdown("### 🤖 AI Status")
            st.success("✅ AI Narratives Active")
            st.caption("Powered by Groq Llama3-70B")
        else:
            st.warning("⚠️ Using Static Narratives")

        # History
        if len(st.session_state.narrative_history) > 1:
            with st.expander(f"📜 Investigation History ({len(st.session_state.narrative_history)} steps)"):
                for i, narrative in enumerate(reversed(st.session_state.narrative_history[:-1])):
                    st.markdown(f"**Step {len(st.session_state.narrative_history) - i - 1}**")
                    st.markdown(narrative[:200] + "..." if len(narrative) > 200 else narrative)
                    st.markdown("---")
