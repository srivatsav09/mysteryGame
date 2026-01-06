"""Interactive map visualization for locations"""
import streamlit as st
from models.world import WorldState
from models.location import Location


class MapVisualizer:
    """Creates an interactive map of game locations"""

    # Map layout coordinates (x, y) for each location
    LOCATION_POSITIONS = {
        "crime_scene": (400, 100),      # Top center
        "police_station": (100, 250),   # Left middle
        "forensics_lab": (100, 400),    # Left bottom
        "suspects_apartment": (700, 250), # Right middle
        "office_building": (700, 400),   # Right bottom
    }

    # Icons for different location categories
    LOCATION_ICONS = {
        "crime_scene": "🔪",
        "official": "🏛️",
        "private": "🏠",
        "public": "🏢",
        "general": "📍"
    }

    # Colors for location states
    STATE_COLORS = {
        "locked": "#666666",      # Gray
        "available": "#4CAF50",   # Green
        "active": "#ff4d4d",      # Red (current)
        "searched": "#2196F3",    # Blue
        "completed": "#9C27B0"    # Purple
    }

    @staticmethod
    def generate_map_svg(world: WorldState, width: int = 800, height: int = 500) -> str:
        """Generate SVG map of the game world"""

        player = world.player
        current_location_id = player.current_location

        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<filter id="glow">',
            '<feGaussianBlur stdDeviation="3" result="coloredBlur"/>',
            '<feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            '</filter>',
            '</defs>',
            f'<rect width="{width}" height="{height}" fill="#0a0a0a"/>',  # Dark background
        ]

        # Draw connections first (so they're behind nodes)
        for loc_id, location in world.locations.items():
            if loc_id not in MapVisualizer.LOCATION_POSITIONS:
                continue

            x1, y1 = MapVisualizer.LOCATION_POSITIONS[loc_id]

            for connected_id in location.connections:
                if connected_id not in MapVisualizer.LOCATION_POSITIONS:
                    continue

                x2, y2 = MapVisualizer.LOCATION_POSITIONS[connected_id]

                # Check if connection is available
                can_travel, _ = location.can_travel_to(connected_id, player, world)

                line_color = "#4CAF50" if can_travel else "#666666"
                line_width = 3 if can_travel else 1
                dash_array = "" if can_travel else "5,5"

                svg_parts.append(
                    f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                    f'stroke="{line_color}" stroke-width="{line_width}" '
                    f'stroke-dasharray="{dash_array}" opacity="0.6"/>'
                )

        # Draw location nodes
        for loc_id, location in world.locations.items():
            if loc_id not in MapVisualizer.LOCATION_POSITIONS:
                continue

            x, y = MapVisualizer.LOCATION_POSITIONS[loc_id]

            # Determine state
            if loc_id == current_location_id:
                state = "active"
            elif location.visited:
                state = "searched" if location.search_count > 0 else "available"
            else:
                state = "available"

            node_color = MapVisualizer.STATE_COLORS.get(state, "#4CAF50")

            # Get icon
            icon = MapVisualizer.LOCATION_ICONS.get(
                location.category,
                MapVisualizer.LOCATION_ICONS["general"]
            )

            # Draw glow for current location
            if loc_id == current_location_id:
                svg_parts.append(
                    f'<circle cx="{x}" cy="{y}" r="45" fill="{node_color}" '
                    f'opacity="0.3" filter="url(#glow)"/>'
                )

            # Draw node circle
            svg_parts.append(
                f'<circle cx="{x}" cy="{y}" r="35" fill="{node_color}" '
                f'stroke="#ffffff" stroke-width="2"/>'
            )

            # Draw icon
            svg_parts.append(
                f'<text x="{x}" y="{y + 10}" font-size="30" text-anchor="middle" '
                f'fill="#ffffff">{icon}</text>'
            )

            # Draw location name
            svg_parts.append(
                f'<text x="{x}" y="{y + 60}" font-size="14" text-anchor="middle" '
                f'fill="#ffffff" font-family="Arial">{location.name}</text>'
            )

            # Draw indicators
            indicators = []

            # NPCs present
            npcs_here = world.get_npcs_at_location(loc_id)
            if npcs_here:
                indicators.append(f"👥 {len(npcs_here)}")

            # Items/clues available
            items_available = len(location.get_available_items())
            clues_available = len(location.get_available_clues())
            if items_available + clues_available > 0:
                indicators.append(f"🔍 {items_available + clues_available}")

            # Draw indicators
            if indicators:
                indicator_text = " ".join(indicators)
                svg_parts.append(
                    f'<text x="{x}" y="{y + 75}" font-size="12" text-anchor="middle" '
                    f'fill="#ffa500">{indicator_text}</text>'
                )

        # Add legend
        legend_x = 20
        legend_y = height - 120
        svg_parts.append(
            f'<rect x="{legend_x - 5}" y="{legend_y - 5}" width="200" height="115" '
            f'fill="#1a1a1a" stroke="#333" stroke-width="1" rx="5"/>'
        )
        svg_parts.append(
            f'<text x="{legend_x + 5}" y="{legend_y + 15}" font-size="12" '
            f'fill="#ffffff" font-weight="bold">Legend:</text>'
        )

        legend_items = [
            (MapVisualizer.STATE_COLORS["active"], "Current Location"),
            (MapVisualizer.STATE_COLORS["searched"], "Searched"),
            ("#666666", "Locked/Unknown"),
        ]

        for i, (color, label) in enumerate(legend_items):
            item_y = legend_y + 35 + (i * 25)
            svg_parts.append(f'<circle cx="{legend_x + 10}" cy="{item_y}" r="6" fill="{color}"/>')
            svg_parts.append(
                f'<text x="{legend_x + 25}" y="{item_y + 5}" font-size="11" fill="#ffffff">{label}</text>'
            )

        svg_parts.append('</svg>')

        return ''.join(svg_parts)

    @staticmethod
    def render_map(world: WorldState):
        """Render the interactive map in Streamlit"""

        st.markdown("### 🗺️ Investigation Map")

        # Generate and display SVG
        svg_map = MapVisualizer.generate_map_svg(world)
        st.markdown(svg_map, unsafe_allow_html=True)

        # Location quick info
        current_loc = world.get_current_location()
        if current_loc:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Current Location:**")
                st.markdown(f"📍 {current_loc.name}")

            with col2:
                st.markdown("**Connected Locations:**")
                for conn_id in current_loc.connections:
                    conn_loc = world.get_location(conn_id)
                    if conn_loc:
                        can_travel, _ = current_loc.can_travel_to(conn_id, world.player, world)
                        status = "✅" if can_travel else "🔒"
                        st.markdown(f"{status} {conn_loc.name}")

            with col3:
                st.markdown("**Exploration:**")
                visited = len(world.player.locations_visited)
                total = len(world.locations)
                st.markdown(f"Visited: {visited}/{total}")
                st.progress(visited / total)

    @staticmethod
    def render_mini_map(world: WorldState, width: int = 300, height: int = 200):
        """Render a smaller version of the map for sidebar"""

        # Simplified map for sidebar
        current_loc = world.get_current_location()

        st.markdown("**🗺️ Map**")

        if current_loc:
            # Show current location and connected locations
            st.markdown(f"📍 **{current_loc.name}**")

            if current_loc.connections:
                st.markdown("**Go to:**")
                for conn_id in current_loc.connections:
                    conn_loc = world.get_location(conn_id)
                    if conn_loc:
                        can_travel, msg = current_loc.can_travel_to(conn_id, world.player, world)
                        if can_travel:
                            status = "🟢"
                        else:
                            status = "🔴"

                        visited_mark = "✓" if conn_id in world.player.locations_visited else ""
                        st.markdown(f"{status} {conn_loc.name} {visited_mark}")
