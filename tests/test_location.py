"""Unit tests for Location model"""
import pytest
from models.location import Location, LocationState, LocationRequirement
from models.player import Player


class TestLocationRequirement:
    """Test LocationRequirement class"""

    def test_no_requirements(self):
        """Test requirement with no conditions"""
        req = LocationRequirement()
        player = Player(name="Test")
        world_state = None  # Not needed for this test

        assert req.is_met(player, world_state) is True

    def test_item_requirement(self):
        """Test item requirement"""
        req = LocationRequirement(requires_item="key")
        player = Player(name="Test")
        world_state = None

        assert req.is_met(player, world_state) is False

        player.add_item("key")
        assert req.is_met(player, world_state) is True

    def test_clue_requirement(self):
        """Test clue requirement"""
        req = LocationRequirement(requires_clue="address_clue")
        player = Player(name="Test")
        world_state = None

        assert req.is_met(player, world_state) is False

        player.add_clue("address_clue")
        assert req.is_met(player, world_state) is True

    def test_quest_requirement(self):
        """Test quest requirement"""
        req = LocationRequirement(requires_quest="intro_quest")
        player = Player(name="Test")
        world_state = None

        assert req.is_met(player, world_state) is False

        player.complete_quest("intro_quest")
        assert req.is_met(player, world_state) is True


class TestLocation:
    """Test Location class"""

    def test_location_creation(self):
        """Test creating a location"""
        location = Location(
            id="crime_scene",
            name="Luxury Apartment",
            description="A high-rise apartment with a broken window",
            category="crime_scene"
        )
        assert location.id == "crime_scene"
        assert location.name == "Luxury Apartment"
        assert location.state == LocationState.AVAILABLE
        assert location.visited is False

    def test_location_connections(self):
        """Test location graph connections"""
        location = Location(id="crime_scene", name="Crime Scene", description="Test")

        location.add_connection("police_station")
        location.add_connection("suspects_home")

        assert "police_station" in location.connections
        assert "suspects_home" in location.connections
        assert len(location.connections) == 2

    def test_connection_with_requirement(self):
        """Test connection with requirement"""
        location = Location(id="lab", name="Lab", description="Test")
        req = LocationRequirement(requires_item="lab_pass")

        location.add_connection("restricted_area", requirement=req)

        assert "restricted_area" in location.connections
        assert "restricted_area" in location.connection_requirements

    def test_can_travel_to(self):
        """Test travel validation"""
        location = Location(id="station", name="Station", description="Test")
        location.add_connection("downtown")

        player = Player(name="Test")
        world_state = None

        # Can travel to connected location
        can_travel, msg = location.can_travel_to("downtown", player, world_state)
        assert can_travel is True

        # Cannot travel to unconnected location
        can_travel, msg = location.can_travel_to("unknown", player, world_state)
        assert can_travel is False

    def test_can_travel_with_requirement(self):
        """Test travel with requirements"""
        location = Location(id="entrance", name="Entrance", description="Test")
        req = LocationRequirement(requires_item="keycard")
        location.add_connection("vault", requirement=req)

        player = Player(name="Test")
        world_state = None

        # Cannot travel without keycard
        can_travel, msg = location.can_travel_to("vault", player, world_state)
        assert can_travel is False

        # Can travel with keycard
        player.add_item("keycard")
        can_travel, msg = location.can_travel_to("vault", player, world_state)
        assert can_travel is True

    def test_items_and_clues(self):
        """Test managing items and clues at location"""
        location = Location(
            id="room",
            name="Room",
            description="Test",
            items_available=["knife", "note"],
            clues_available=["bloodstain", "footprint"]
        )

        # Check available items
        assert len(location.get_available_items()) == 2
        assert "knife" in location.get_available_items()

        # Take item
        success = location.take_item("knife")
        assert success is True
        assert len(location.get_available_items()) == 1
        assert "knife" not in location.get_available_items()

        # Check available clues
        assert len(location.get_available_clues()) == 2

        # Find clue
        success = location.find_clue("bloodstain")
        assert success is True
        assert len(location.get_available_clues()) == 1

    def test_visit_location(self):
        """Test visiting a location"""
        location = Location(id="park", name="Park", description="Test")
        assert location.visited is False

        location.visit()
        assert location.visited is True
        assert location.state == LocationState.ACTIVE

    def test_search_location(self):
        """Test searching a location"""
        location = Location(id="office", name="Office", description="Test")
        assert location.search_count == 0

        location.search()
        assert location.search_count == 1

        # Location with no items/clues becomes searched
        location.search()
        assert location.state == LocationState.SEARCHED

    def test_npcs_at_location(self):
        """Test NPCs present at location"""
        location = Location(
            id="cafe",
            name="Cafe",
            description="Test",
            npcs_present=["barista", "customer_1", "customer_2"]
        )
        assert len(location.npcs_present) == 3
        assert "barista" in location.npcs_present

    def test_location_serialization(self):
        """Test location serialization"""
        location = Location(
            id="library",
            name="Public Library",
            description="A quiet library",
            connections=["downtown", "university"],
            items_available=["book"],
            clues_available=["note"]
        )
        location.visit()
        location.take_item("book")

        # Serialize
        data = location.to_dict()
        assert data["id"] == "library"
        assert "downtown" in data["connections"]
        assert data["visited"] is True

        # Deserialize
        restored = Location.from_dict(data)
        assert restored.id == location.id
        assert restored.visited is True
        assert "downtown" in restored.connections
        assert "book" in restored.items_taken
