"""Sample mystery scenario: The Penthouse Murder"""
from models.world import WorldState
from models.player import Player, PlayerStats
from models.location import Location, LocationRequirement
from models.npc import NPC, NPCRole
from models.item import Item, Clue, ItemType
from models.quest import Quest, QuestObjective, QuestStatus, ObjectiveType


def create_sample_mystery() -> WorldState:
    """Create a sample murder mystery scenario"""

    # Create player
    player = Player(
        name="Detective",
        stats=PlayerStats(
            investigation=7,
            persuasion=6,
            perception=6,
            intuition=5,
            physical=5
        ),
        current_location="crime_scene"
    )

    # Create world
    world = WorldState(player=player)

    # ========== LOCATIONS ==========

    # Crime Scene - Luxury Penthouse
    crime_scene = Location(
        id="crime_scene",
        name="Luxury Penthouse",
        description="A lavish penthouse apartment on the 42nd floor. A body lies on the marble floor near the balcony. The room shows signs of a struggle - overturned furniture, broken glass. The victim is Marcus Blackwell, a wealthy tech CEO.",
        category="crime_scene",
        npcs_present=["officer_chen", "forensic_tech"],
        items_available=["wine_glass", "phone"],
        clues_available=["broken_window", "wine_residue", "phone_messages"],
        connections=["police_station", "suspects_apartment", "office_building"]
    )

    # Police Station
    police_station = Location(
        id="police_station",
        name="Police Headquarters",
        description="A busy metropolitan police station. The evidence room and interrogation rooms are available. Your desk is covered with case files.",
        category="official",
        npcs_present=["chief_brooks"],
        items_available=["case_file"],
        clues_available=["background_check"],
        connections=["crime_scene", "forensics_lab", "suspects_apartment"]
    )

    # Suspect's Apartment
    suspects_apartment = Location(
        id="suspects_apartment",
        name="Sarah's Apartment",
        description="A modest downtown apartment. Sarah Chen, the victim's business partner, lives here. The place is tidy but there's tension in the air.",
        category="private",
        npcs_present=["suspect_sarah"],
        items_available=["business_contract"],
        clues_available=["alibi_note", "partnership_dispute"],
        connections=["police_station", "crime_scene", "office_building"]
    )

    # Office Building
    office_building = Location(
        id="office_building",
        name="TechCorp Headquarters",
        description="The sleek glass building where Marcus ran his company. His office on the 20th floor holds many secrets.",
        category="public",
        npcs_present=["secretary_james"],
        items_available=["company_records"],
        clues_available=["financial_records", "threatening_email"],
        connections=["crime_scene", "suspects_apartment"]
    )

    # Forensics Lab (locked initially)
    forensics_lab = Location(
        id="forensics_lab",
        name="Forensics Laboratory",
        description="A state-of-the-art forensics lab. The team is analyzing evidence from the crime scene.",
        category="official",
        npcs_present=["forensic_expert"],
        items_available=[],
        clues_available=["toxicology_report", "fingerprint_match"],
        connections=["police_station"]
    )

    # Add connection requirement for forensics lab
    police_station.add_connection(
        "forensics_lab",
        requirement=LocationRequirement(requires_clue="wine_residue")
    )

    world.locations = {
        "crime_scene": crime_scene,
        "police_station": police_station,
        "suspects_apartment": suspects_apartment,
        "office_building": office_building,
        "forensics_lab": forensics_lab
    }

    # ========== NPCs ==========

    # Officer Chen - Ally at crime scene
    officer_chen = NPC(
        id="officer_chen",
        name="Officer Chen",
        description="A competent patrol officer who was first on the scene. Eager to help with the investigation.",
        role=NPCRole.ALLY,
        current_location="crime_scene",
        personality_traits=["helpful", "observant", "professional"],
        trust_level=60,
        knows_clues={"broken_window", "initial_timeline"},
        will_share_clues={"initial_timeline"}
    )

    # Chief Brooks - Authority figure
    chief_brooks = NPC(
        id="chief_brooks",
        name="Chief Brooks",
        description="Your demanding but fair police chief. Wants this high-profile case solved quickly.",
        role=NPCRole.AUTHORITY,
        current_location="police_station",
        personality_traits=["stern", "experienced", "impatient"],
        trust_level=50,
        gives_quests=["solve_murder"]
    )

    # Sarah Chen - Primary Suspect
    suspect_sarah = NPC(
        id="suspect_sarah",
        name="Sarah Chen",
        description="Marcus's business partner and rumored romantic interest. She seems nervous and defensive.",
        role=NPCRole.SUSPECT,
        current_location="suspects_apartment",
        personality_traits=["intelligent", "defensive", "secretive"],
        secrets=["was_at_scene", "argued_about_money", "loved_victim"],
        trust_level=20,
        knows_clues={"partnership_dispute", "alibi_note", "secret_relationship"},
        will_share_clues={"alibi_note"}
    )

    # James Park - Secretary/Witness
    secretary_james = NPC(
        id="secretary_james",
        name="James Park",
        description="Marcus's executive secretary. Has worked with him for 5 years and knows everyone's secrets.",
        role=NPCRole.WITNESS,
        current_location="office_building",
        personality_traits=["professional", "observant", "loyal"],
        secrets=["knows_about_embezzlement", "saw_suspicious_visitor"],
        trust_level=40,
        knows_clues={"threatening_email", "financial_records", "visitor_log"},
        will_share_clues={"threatening_email"}
    )

    # Forensic Tech
    forensic_tech = NPC(
        id="forensic_tech",
        name="Dr. Martinez",
        description="Lead forensic technician. Methodical and precise in her work.",
        role=NPCRole.ALLY,
        current_location="crime_scene",
        personality_traits=["analytical", "precise", "helpful"],
        trust_level=70,
        knows_clues={"wine_residue", "time_of_death"},
        will_share_clues={"wine_residue", "time_of_death"}
    )

    # Forensic Expert (at lab)
    forensic_expert = NPC(
        id="forensic_expert",
        name="Dr. Kim",
        description="Expert forensic pathologist. Can provide detailed analysis of evidence.",
        role=NPCRole.INFORMANT,
        current_location="forensics_lab",
        personality_traits=["expert", "thorough", "scientific"],
        trust_level=80,
        knows_clues={"toxicology_report", "fingerprint_match", "cause_of_death"},
        will_share_clues={"toxicology_report", "fingerprint_match", "cause_of_death"}
    )

    world.npcs = {
        "officer_chen": officer_chen,
        "chief_brooks": chief_brooks,
        "suspect_sarah": suspect_sarah,
        "secretary_james": secretary_james,
        "forensic_tech": forensic_tech,
        "forensic_expert": forensic_expert
    }

    # ========== ITEMS ==========

    wine_glass = Item(
        id="wine_glass",
        name="Wine Glass",
        description="An expensive crystal wine glass with red wine residue. Found near the victim.",
        item_type=ItemType.EVIDENCE,
        is_clue=True,
        found_at="crime_scene",
        tags=["evidence", "glass", "fingerprints"]
    )

    phone = Item(
        id="phone",
        name="Victim's Phone",
        description="Marcus Blackwell's smartphone. Unlocked and shows recent messages.",
        item_type=ItemType.EVIDENCE,
        is_clue=True,
        found_at="crime_scene",
        tags=["evidence", "digital", "communications"]
    )

    case_file = Item(
        id="case_file",
        name="Case File",
        description="Official case file with initial reports and witness statements.",
        item_type=ItemType.DOCUMENT,
        found_at="police_station",
        tags=["document", "official"]
    )

    business_contract = Item(
        id="business_contract",
        name="Partnership Contract",
        description="Legal documents outlining the business partnership between Marcus and Sarah.",
        item_type=ItemType.DOCUMENT,
        found_at="suspects_apartment",
        tags=["document", "legal", "financial"]
    )

    company_records = Item(
        id="company_records",
        name="Financial Records",
        description="Company financial statements showing recent transactions.",
        item_type=ItemType.DOCUMENT,
        found_at="office_building",
        tags=["document", "financial", "confidential"]
    )

    world.items = {
        "wine_glass": wine_glass,
        "phone": phone,
        "case_file": case_file,
        "business_contract": business_contract,
        "company_records": company_records
    }

    # ========== CLUES ==========

    broken_window = Clue(
        id="broken_window",
        title="Broken Balcony Window",
        description="The balcony window is shattered from the inside, not outside. Glass shards are scattered on the balcony.",
        category="physical",
        found_at="crime_scene",
        importance=4,
        related_npcs=["officer_chen"],
        related_clues=["struggle_evidence"]
    )

    wine_residue = Clue(
        id="wine_residue",
        title="Wine Residue Analysis",
        description="The wine glass contains traces of sedatives. Someone drugged Marcus before the confrontation.",
        category="forensic",
        found_at="crime_scene",
        requires_stat="investigation",
        requires_stat_level=5,
        importance=5,
        related_clues=["toxicology_report"],
        unlocks_dialogue=["confront_about_drugging"]
    )

    phone_messages = Clue(
        id="phone_messages",
        title="Threatening Messages",
        description="Recent text messages show heated arguments about money and betrayal.",
        category="digital",
        found_at="crime_scene",
        importance=3,
        related_npcs=["suspect_sarah"],
        related_clues=["partnership_dispute"]
    )

    alibi_note = Clue(
        id="alibi_note",
        title="Sarah's Alibi",
        description="Sarah claims she was at a restaurant during the murder. Receipt shows 8:00 PM - 10:30 PM.",
        category="testimony",
        found_at="suspects_apartment",
        importance=3,
        related_npcs=["suspect_sarah"],
        contradicts_clues=["time_of_death"]
    )

    partnership_dispute = Clue(
        id="partnership_dispute",
        title="Business Dispute",
        description="Documents show Sarah and Marcus were fighting over company control. Sarah was being forced out.",
        category="document",
        found_at="suspects_apartment",
        importance=4,
        related_npcs=["suspect_sarah", "secretary_james"],
        related_clues=["financial_records"]
    )

    background_check = Clue(
        id="background_check",
        title="Background Information",
        description="Marcus Blackwell, 45, CEO of TechCorp. No criminal record. Divorced 2 years ago. Estimated worth: $50 million.",
        category="testimony",
        found_at="police_station",
        importance=2
    )

    financial_records = Clue(
        id="financial_records",
        title="Suspicious Transactions",
        description="Large sums were being moved to offshore accounts. Someone was embezzling.",
        category="document",
        found_at="office_building",
        requires_stat="investigation",
        requires_stat_level=6,
        importance=5,
        related_npcs=["secretary_james", "suspect_sarah"],
        unlocks_dialogue=["confront_about_embezzlement"]
    )

    threatening_email = Clue(
        id="threatening_email",
        title="Threatening Email",
        description="An email sent to Marcus last week: 'You'll pay for what you've done. This isn't over.'",
        category="digital",
        found_at="office_building",
        importance=3,
        related_clues=["phone_messages"]
    )

    toxicology_report = Clue(
        id="toxicology_report",
        title="Toxicology Report",
        description="Victim had high levels of sedatives in his system. He was drugged 30-45 minutes before death.",
        category="forensic",
        found_at="forensics_lab",
        importance=5,
        related_clues=["wine_residue"],
        unlocks_dialogue=["final_confrontation"]
    )

    fingerprint_match = Clue(
        id="fingerprint_match",
        title="Fingerprint Analysis",
        description="Fingerprints on the wine glass match Sarah Chen. She was definitely at the scene.",
        category="forensic",
        found_at="forensics_lab",
        importance=5,
        related_npcs=["suspect_sarah"],
        contradicts_clues=["alibi_note"],
        unlocks_dialogue=["final_confrontation"]
    )

    world.clues = {
        "broken_window": broken_window,
        "wine_residue": wine_residue,
        "phone_messages": phone_messages,
        "alibi_note": alibi_note,
        "partnership_dispute": partnership_dispute,
        "background_check": background_check,
        "financial_records": financial_records,
        "threatening_email": threatening_email,
        "toxicology_report": toxicology_report,
        "fingerprint_match": fingerprint_match
    }

    # ========== QUESTS ==========

    # Main quest
    solve_murder = Quest(
        id="solve_murder",
        title="Solve the Penthouse Murder",
        description="Investigate Marcus Blackwell's murder and identify the killer.",
        category="main",
        status=QuestStatus.ACTIVE,
        given_by="chief_brooks",
        reward_reputation=50
    )

    # Add objectives
    obj1 = QuestObjective(
        id="examine_crime_scene",
        description="Thoroughly examine the crime scene",
        objective_type=ObjectiveType.GO_TO_LOCATION,
        target_id="crime_scene"
    )

    obj2 = QuestObjective(
        id="collect_evidence",
        description="Collect at least 3 pieces of evidence",
        objective_type=ObjectiveType.COLLECT_ITEM,
        quantity=3,
        requires_objectives=["examine_crime_scene"]
    )

    obj3 = QuestObjective(
        id="interview_suspect",
        description="Interview Sarah Chen",
        objective_type=ObjectiveType.TALK_TO_NPC,
        target_id="suspect_sarah",
        requires_objectives=["examine_crime_scene"]
    )

    obj4 = QuestObjective(
        id="get_forensics",
        description="Get forensic analysis from the lab",
        objective_type=ObjectiveType.FIND_CLUE,
        target_id="toxicology_report",
        requires_objectives=["collect_evidence"]
    )

    obj5 = QuestObjective(
        id="final_deduction",
        description="Confront the killer with evidence",
        objective_type=ObjectiveType.CONFRONT_NPC,
        target_id="suspect_sarah",
        requires_objectives=["get_forensics", "interview_suspect"]
    )

    solve_murder.add_objective(obj1)
    solve_murder.add_objective(obj2)
    solve_murder.add_objective(obj3)
    solve_murder.add_objective(obj4)
    solve_murder.add_objective(obj5)

    world.quests = {
        "solve_murder": solve_murder
    }

    # Mark the game as started
    world.game_started = True

    return world
