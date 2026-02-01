"""
Extract entities, FOIA targets, and relationships from UAPGerb transcript
"""
import re
import csv
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict

# High-priority entities to extract from transcript
ENTITIES_TO_EXTRACT = {
    # Government Agencies
    'NRO': {
        'display_name': 'National Reconnaissance Office',
        'normalized_name': 'NRO',
        'entity_type': 'Government Agency',
        'description': 'National Reconnaissance Office - runs America\'s spy satellites, IMT and SIGINT primarily',
        'aliases': 'NRO'
    },
    'NGA': {
        'display_name': 'National Geospatial-Intelligence Agency',
        'normalized_name': 'NGA',
        'entity_type': 'Government Agency',
        'description': 'National Geospatial-Intelligence Agency - combat support agency',
        'aliases': 'NGA'
    },
    'DIA': {
        'display_name': 'Defense Intelligence Agency',
        'normalized_name': 'DIA',
        'entity_type': 'Government Agency',
        'description': 'Defense Intelligence Agency',
        'aliases': 'DIA'
    },
    'CIA DS&T': {
        'display_name': 'CIA Directorate of Science and Technology',
        'normalized_name': 'CIA DS&T',
        'entity_type': 'Government Agency',
        'description': 'CIA Directorate of Science and Technology - legacy program administrator',
        'aliases': 'CIA DS&T, DS&T'
    },
    'DOE': {
        'display_name': 'Department of Energy',
        'normalized_name': 'DOE',
        'entity_type': 'Government Agency',
        'description': 'Department of Energy - holds classification systems for UFO legacy programs',
        'aliases': 'DOE, Department of Energy'
    },
    'DOE OICI': {
        'display_name': 'DOE Office of Intelligence and Counter Intelligence',
        'normalized_name': 'DOE OICI',
        'entity_type': 'Government Agency',
        'description': 'DOE Office of Intelligence and Counter Intelligence - program protection for legacy programs',
        'aliases': 'DOE OICI, OICI'
    },
    'DOE NEST': {
        'display_name': 'DOE Nuclear Emergency Support Team',
        'normalized_name': 'DOE NEST',
        'entity_type': 'Government Agency',
        'description': 'DOE Nuclear Emergency Support Team - rapid reaction responses to CBRNE events, crash retrieval operations',
        'aliases': 'DOE NEST, NEST'
    },
    'DARPA SID': {
        'display_name': 'DARPA Security and Intelligence Directorate',
        'normalized_name': 'DARPA SID',
        'entity_type': 'Government Agency',
        'description': 'DARPA Security and Intelligence Directorate - program protection for special access programs',
        'aliases': 'DARPA SID, DARPA Security and Intelligence Directorate'
    },
    'NSA': {
        'display_name': 'National Security Agency',
        'normalized_name': 'NSA',
        'entity_type': 'Government Agency',
        'description': 'National Security Agency',
        'aliases': 'NSA'
    },
    'OGA': {
        'display_name': 'Office of Global Access',
        'normalized_name': 'OGA',
        'entity_type': 'Government Agency',
        'description': 'CIA Office of Global Access - created 2003 under DS&T for foreign UFO crash retrievals',
        'aliases': 'OGA, Office of Global Access'
    },
    'DDNI ATNF': {
        'display_name': 'Deputy Director for National Intelligence for Acquisition Technology and Facilities',
        'normalized_name': 'DDNI ATNF',
        'entity_type': 'Government Agency',
        'description': 'Deputy Director for National Intelligence for Acquisition Technology and Facilities - oversight over NRO acquisitions',
        'aliases': 'DDNI ATNF'
    },
    'OUSD': {
        'display_name': 'Office of Under Secretary of Defense for Acquisition and Sustainment',
        'normalized_name': 'OUSD',
        'entity_type': 'Government Agency',
        'description': 'Office of Under Secretary of Defense for Acquisition and Sustainment - previously OUSDAT, holds records to special carveout programs',
        'aliases': 'OUSD, OUSDAT'
    },
    'AARO': {
        'display_name': 'All-domain Anomaly Resolution Office',
        'normalized_name': 'AARO',
        'entity_type': 'Government Agency',
        'description': 'All-domain Anomaly Resolution Office - established to investigate UAP',
        'aliases': 'AARO'
    },
    # FFRDCs
    'MITER Corporation': {
        'display_name': 'MITER Corporation',
        'normalized_name': 'MITER',
        'entity_type': 'Research Institution',
        'description': 'MITER Corporation - FFRDC, most overlooked entity in UFO legacy programs, deals with naval programs and USOs',
        'aliases': 'MITER, MITER Corporation'
    },
    'Battel Memorial Institute': {
        'display_name': 'Battel Memorial Institute',
        'normalized_name': 'Battel',
        'entity_type': 'Research Institution',
        'description': 'Battel Memorial Institute - FFRDC, manages numerous institutions and DOE national labs',
        'aliases': 'Battel, Battel Memorial Institute'
    },
    'Sandia National Laboratories': {
        'display_name': 'Sandia National Laboratories',
        'normalized_name': 'Sandia',
        'entity_type': 'Research Institution',
        'description': 'Sandia National Laboratories - DOE NNSA National Lab, Project Twinkle, Z division, experimental weapons testing',
        'aliases': 'Sandia, Sandia Labs, Sandia National Lab'
    },
    'Lawrence Livermore National Laboratory': {
        'display_name': 'Lawrence Livermore National Laboratory',
        'normalized_name': 'Lawrence Livermore',
        'entity_type': 'Research Institution',
        'description': 'Lawrence Livermore National Laboratory - DOE NNSA National Lab',
        'aliases': 'Lawrence Livermore, LLNL, Livermore'
    },
    'Oak Ridge National Laboratory': {
        'display_name': 'Oak Ridge National Laboratory',
        'normalized_name': 'Oak Ridge',
        'entity_type': 'Research Institution',
        'description': 'Oak Ridge National Laboratory - DOE NNSA National Lab, housed under Y12 complex',
        'aliases': 'Oak Ridge, ORNL, Y12'
    },
    'Los Alamos National Laboratory': {
        'display_name': 'Los Alamos National Laboratory',
        'normalized_name': 'Los Alamos',
        'entity_type': 'Research Institution',
        'description': 'Los Alamos National Laboratory - DOE NNSA National Lab, Z division',
        'aliases': 'Los Alamos, LANL'
    },
    'Y12 Complex': {
        'display_name': 'Y12 National Security Complex',
        'normalized_name': 'Y12',
        'entity_type': 'Facility',
        'description': 'Y12 National Security Complex - houses Oak Ridge National Laboratory, alleged UFO legacy program for craft skin analysis',
        'aliases': 'Y12, Y12 Complex'
    },
    'IDA': {
        'display_name': 'Institute for Defense Analyses',
        'normalized_name': 'IDA',
        'entity_type': 'Research Institution',
        'description': 'Institute for Defense Analyses - FFRDC, Harold Malmgren worked there as cover for NSC',
        'aliases': 'IDA, Institute for Defense Analyses'
    },
    'Aerospace Corporation': {
        'display_name': 'Aerospace Corporation',
        'normalized_name': 'Aerospace Corporation',
        'entity_type': 'Research Institution',
        'description': 'Aerospace Corporation - FFRDC established 1959-1960',
        'aliases': 'Aerospace Corporation'
    },
    # Contractors
    'Lockheed Martin': {
        'display_name': 'Lockheed Martin',
        'normalized_name': 'Lockheed Martin',
        'entity_type': 'Corporation',
        'description': 'Lockheed Martin - defense industrial base prime contractor, Kona Blue program involvement',
        'aliases': 'Lockheed Martin, Lockheed'
    },
    'Northrop Grumman': {
        'display_name': 'Northrop Grumman',
        'normalized_name': 'Northrop Grumman',
        'entity_type': 'Corporation',
        'description': 'Northrop Grumman - defense industrial base prime contractor, acquired BDM, TRW, Teledyne Ryan',
        'aliases': 'Northrop Grumman, Northrop'
    },
    'Raytheon': {
        'display_name': 'Raytheon',
        'normalized_name': 'Raytheon',
        'entity_type': 'Corporation',
        'description': 'Raytheon - defense contractor, especially with US Army',
        'aliases': 'Raytheon'
    },
    'EG&G': {
        'display_name': 'EG&G',
        'normalized_name': 'EG&G',
        'entity_type': 'Corporation',
        'description': 'EG&G - now part of Amentum, hired Bob Lazar, alleged to house craft at Area 51 adjacent sites',
        'aliases': 'EG&G, EG&NG, Amentum'
    },
    'Bigelow Aerospace Advanced Space Studies': {
        'display_name': 'Bigelow Aerospace Advanced Space Studies',
        'normalized_name': 'BAASS',
        'entity_type': 'Corporation',
        'description': 'Bigelow Aerospace Advanced Space Studies - Kona Blue program participant',
        'aliases': 'BAASS, Bigelow Aerospace'
    },
    # Programs
    'Immaculate Constellation': {
        'display_name': 'Immaculate Constellation',
        'normalized_name': 'Immaculate Constellation',
        'entity_type': 'Program',
        'description': 'USAP program began 2017, utilized US intelligence platforms to monitor non-human craft and ARVs',
        'aliases': 'Immaculate Constellation, IM Con'
    },
    'Kona Blue': {
        'display_name': 'Kona Blue',
        'normalized_name': 'Kona Blue',
        'entity_type': 'Program',
        'description': 'Failed prospective special access program (2010) - DHS sponsored USAP for Lockheed Martin to divulge craft materials',
        'aliases': 'Kona Blue'
    },
    'Project Preserve Destiny': {
        'display_name': 'Project Preserve Destiny',
        'normalized_name': 'Project Preserve Destiny',
        'entity_type': 'Program',
        'description': 'NSA program involving telepathic downloads, Dan Sherman testimony',
        'aliases': 'Project Preserve Destiny'
    },
    'Project Looking Glass': {
        'display_name': 'Project Looking Glass',
        'normalized_name': 'Project Looking Glass',
        'entity_type': 'Program',
        'description': 'Manipulation of timelines, mentioned in Bob Lazar briefing',
        'aliases': 'Project Looking Glass, Looking Glass'
    },
    'Project Twinkle': {
        'display_name': 'Project Twinkle',
        'normalized_name': 'Project Twinkle',
        'entity_type': 'Program',
        'description': 'Sandia-based Z division investigation into green fireballs over New Mexico (1949-1951)',
        'aliases': 'Project Twinkle'
    },
    'Advanced Theoretical Physics Working Group': {
        'display_name': 'Advanced Theoretical Physics Working Group',
        'normalized_name': 'Advanced Theoretical Physics Working Group',
        'entity_type': 'Program',
        'description': 'Physics group held at BDM International in 1985 at their MLAN facility',
        'aliases': 'Advanced Theoretical Physics Working Group, ATPWG'
    },
    # Facilities
    'Area 51': {
        'display_name': 'Area 51',
        'normalized_name': 'Area 51',
        'entity_type': 'Facility',
        'description': 'Groom Lake, Nevada - classified test location, houses S4, alleged UFO testing and storage',
        'aliases': 'Area 51, Groom Lake'
    },
    'S4': {
        'display_name': 'S4',
        'normalized_name': 'S4',
        'entity_type': 'Facility',
        'description': 'Area 51 adjacent site, Papoose Lake, alleged craft storage facility',
        'aliases': 'S4, Papoose Lake'
    },
    'Nevada Test and Training Range': {
        'display_name': 'Nevada Test and Training Range',
        'normalized_name': 'NTR',
        'entity_type': 'Facility',
        'description': 'Major range and test facility base, houses Area 51, Tonopah Test Range, numbered areas',
        'aliases': 'NTR, Nevada Test and Training Range'
    },
    'Tonopah Test Range': {
        'display_name': 'Tonopah Test Range',
        'normalized_name': 'TTR',
        'entity_type': 'Facility',
        'description': 'Also known as Area 52, managed by Sandia, DOE experimental weapons testing range',
        'aliases': 'TTR, Tonopah Test Range, Area 52'
    },
    'Edwards Air Force Base': {
        'display_name': 'Edwards Air Force Base',
        'normalized_name': 'Edwards AFB',
        'entity_type': 'Facility',
        'description': 'Edwards 412 Test Wing - major range and test facility base, operates manned flights at Area 51, ARV testing',
        'aliases': 'Edwards AFB, Edwards, Edwards 412 Test Wing'
    },
    'Dugway Proving Ground': {
        'display_name': 'Dugway Proving Ground',
        'normalized_name': 'Dugway',
        'entity_type': 'Facility',
        'description': 'Utah test range, houses Utah Test and Training Range and West Desert Test Center, alleged biologics storage',
        'aliases': 'Dugway, Dugway Proving Ground, Area 52'
    },
    'Wright-Patterson Air Force Base': {
        'display_name': 'Wright-Patterson Air Force Base',
        'normalized_name': 'Wright-Patterson AFB',
        'entity_type': 'Facility',
        'description': 'Alleged historical storage of Roswell materials and biologics',
        'aliases': 'Wright-Patterson, Wright-Patterson AFB, Wright Field'
    },
    'Pine Gap': {
        'display_name': 'Pine Gap',
        'normalized_name': 'Pine Gap',
        'entity_type': 'Facility',
        'description': 'Australia - NRO Program B ground element, Australia\'s Area 51',
        'aliases': 'Pine Gap, Pine Gap Australia'
    },
    'Fort Detrick': {
        'display_name': 'Fort Detrick',
        'normalized_name': 'Fort Detrick',
        'entity_type': 'Facility',
        'description': 'Maryland - alleged biologics storage facility, Battel biological programs',
        'aliases': 'Fort Detrick'
    },
    # Key Individuals (mentioned but may not add as entities - context for relationships)
}

FOIA_TARGETS = [
    {
        'agency': 'NRO',
        'record_request': 'NRO Program B records, consolidation of reconnaissance activities between NRO and CIA DS&T, ground element at Pine Gap Australia (1982-1989)',
        'timeframe': '1982-1989',
        'relevance': 'Direct connection to UFO legacy programs and crash retrieval operations',
        'notes': 'Mentioned in transcript - R. Everett Heinman was NRO Program B director. Bobby Ray Inman referenced Program B in connection with crash retrieval.'
    },
    {
        'agency': 'NRO',
        'record_request': '1994-1995 Senate and GAO audit records for misappropriation of funds, specifically carryover funds (~$3.2 billion)',
        'timeframe': '1994-1995',
        'relevance': 'Demonstrates funding mechanisms for legacy programs through misappropriated funds',
        'notes': 'Transcript mentions NRO and NGA underwent audit for enormous misappropriation of funds. NRO was only declassified in 1992.'
    },
    {
        'agency': 'CIA DS&T',
        'record_request': 'Office of Global Access (OGA) creation and operational records (2003+), foreign UFO crash retrieval operations',
        'timeframe': '2003-present',
        'relevance': 'OGA is logistics/combat support agency for foreign crash retrievals',
        'notes': 'Created under DS&T in 2003. First director was Doug Wolfe. Coordinates with DOE NEST and US Army 160th SOAR for retrievals.'
    },
    {
        'agency': 'CIA DS&T',
        'record_request': 'Kona Blue program records - decision to block Lockheed Martin material transfer to Bigelow Aerospace (2010)',
        'timeframe': '2010',
        'relevance': 'Shows CIA DS&T blocking technology transfer, Glenn Gaffney involvement',
        'notes': 'Failed USAP program. Glenn Gaffney (CIA DS&T deputy director) blocked technology transfer. AARO Historical Report Volume 1 references.'
    },
    {
        'agency': 'DOE OICI',
        'record_request': 'Classification controls and oversight for UFO legacy programs under 1954 Atomic Energy Agreement, special nuclear materials classification',
        'timeframe': '1954-present',
        'relevance': 'DOE holds classification systems that govern UFO legacy programs',
        'notes': 'Authority derived from 1954 Atomic Energy Agreement. Includes special nuclear materials, TFNI, and FII classifications.'
    },
    {
        'agency': 'DOE NEST',
        'record_request': 'Rapid reaction retrieval team records, foreign and domestic crash retrieval operations, private jet operations',
        'timeframe': '1990s-present',
        'relevance': 'DOE NEST responsible for rapid reaction responses to CBRNE events and UFO crash retrievals',
        'notes': 'DOE NNSA support team. Has private jets. Coordinates with CIA OGA for retrievals. Operates under 1954 Atomic Energy Agreement authority.'
    },
    {
        'agency': 'DARPA SID',
        'record_request': 'Program protection strategies for special access programs, insider threat management for legacy programs',
        'timeframe': '1980s-present',
        'relevance': 'DARPA SID responsible for program protection for most classified SAPs',
        'notes': 'Security and Intelligence Directorate - program protection structure for special access programs.'
    },
    {
        'agency': 'MITER Corporation',
        'record_request': 'FFRDC contracts related to UFO legacy programs, anti-gravity conferences, naval program involvement, USO-related work',
        'timeframe': '1960s-present',
        'relevance': 'MITER is emphasized as most overlooked but crucial entity in legacy programs',
        'notes': 'Government-owned contractor-operated FFRDC. Numerous high-level personnel connections (Paul Kaminsky, Don Meyer, Donald Kerr).'
    },
    {
        'agency': 'OUSD',
        'record_request': 'Special carveout holdover programs referenced in Wilson-Davis notes, permanent SAPO oversight committee records',
        'timeframe': '1990s-2000s',
        'relevance': 'Wilson-Davis notes reference OUSDAT holding records to special carveout programs with access to legacy programs',
        'notes': 'Office of Under Secretary of Defense for Acquisition and Sustainment (formerly OUSDAT). Paul Kaminsky was director and MITER board member.'
    },
    {
        'agency': 'DDNI ATNF',
        'record_request': 'NRO acquisition oversight records, relationship with OUSD for program acquisitions',
        'timeframe': '2000s-present',
        'relevance': 'DDNI ATNF has oversight over NRO program acquisitions per GAO',
        'notes': 'Counterpart to OUSD in intelligence community. Doug Wolfe served as DDNI ATNF. Mark Moahan also held position with NRO, CIA, OGA connections.'
    },
    {
        'agency': 'Sandia National Laboratories',
        'record_request': 'Project Twinkle records (1949-1951), Z division operations, green fireball investigations, recommendations for non-disclosure',
        'timeframe': '1949-1951',
        'relevance': 'Project Twinkle concluded no natural explanation for green fireballs, Air Force recommended findings not be disclosed',
        'notes': 'Sandia-based investigation. Lincoln LaPaz conclusion that objects tracked atomic detonations intelligently. Records recommended for non-disclosure.'
    },
    {
        'agency': 'Edwards 412 Test Wing',
        'record_request': 'ARV (Alien Reproduction Vehicle) testing records, Lieutenant Colonel testimony (1998-2007), Nevada Test and Training Range operations',
        'timeframe': '1998-2007',
        'relevance': 'Direct testimony of ARV testing program at Edwards',
        'notes': 'Air Force Lieutenant Colonel claimed to run program testing alien reproduction vehicles and derivative technology. Electronics warfare group director.'
    },
    {
        'agency': 'DOE',
        'record_request': '1954 Atomic Energy Agreement records related to UFO legacy program classification, special nuclear materials applications',
        'timeframe': '1954-present',
        'relevance': '1954 agreement gave expanded powers to government-owned contractor-operated laboratories to house craft materials',
        'notes': 'Turning point when DOE FFRDCs and NNSA started to house materials. Alfred O\'Donnell stated craft moved to Area 51 adjacent site in 1954.'
    },
    {
        'agency': 'Oak Ridge National Laboratory',
        'record_request': 'Y12 Complex UFO legacy program records - craft skin analysis program, material exploitation of two recovered saucer craft',
        'timeframe': '2000s-present',
        'relevance': 'Direct testimony of program studying skin of recovered non-human saucer craft',
        'notes': 'Program under Y12 complex. MITER and Battel primary contractors. DOE OICI runs the show. Layers of craft skin like Russian nesting doll.'
    },
    {
        'agency': 'US Army',
        'record_request': '160th SOAR (Special Operations Aviation Regiment) First Battalion records - support for J-C operations, CH47 helicopter use in crash retrieval operations',
        'timeframe': '2003-present',
        'relevance': 'CIA OGA contracts 160th SOAR for helicopter support in crash retrieval operations',
        'notes': 'US Army helicopter regiment that supports J-C (Joint Special Operations Command) operations. Provides CH47 helicopters for retrievals.'
    },
]

RELATIONSHIPS = [
    # Agency to Agency
    ('NRO', 'CIA DS&T', 'Program B Partnership', 'Consolidation of reconnaissance activities, Program B established ground element at Pine Gap'),
    ('CIA DS&T', 'OGA', 'Created', 'OGA created under DS&T in 2003, first director Doug Wolfe'),
    ('OGA', 'DOE NEST', 'Coordinates', 'OGA coordinates with DOE NEST for rapid reaction retrieval operations'),
    ('OUSD', 'DDNI ATNF', 'Two Sides of Same Coin', 'Both have oversight over NRO program acquisitions per GAO'),
    ('DOE', 'Sandia National Laboratories', 'Owns', 'Sandia is DOE NNSA National Lab'),
    ('DOE', 'Lawrence Livermore National Laboratory', 'Owns', 'Lawrence Livermore is DOE NNSA National Lab'),
    ('DOE', 'Oak Ridge National Laboratory', 'Owns', 'Oak Ridge is DOE NNSA National Lab, housed under Y12'),
    ('DOE', 'Los Alamos National Laboratory', 'Owns', 'Los Alamos is DOE NNSA National Lab'),
    ('DOE', 'DOE OICI', 'Subordinate Agency', 'DOE Office of Intelligence and Counter Intelligence'),
    ('DOE', 'DOE NEST', 'Subordinate Agency', 'DOE Nuclear Emergency Support Team, NNSA support team'),
    
    # Agency to FFRDC
    ('MITER Corporation', 'NRO', 'Contractor', 'MITER has extensive connections to NRO personnel'),
    ('MITER Corporation', 'CIA DS&T', 'Contractor', 'MITER personnel have revolving door with DS&T'),
    ('MITER Corporation', 'OUSD', 'Board Connection', 'Paul Kaminsky was OUSD director and MITER board member'),
    ('MITER Corporation', 'DDNI ATNF', 'Personnel Connection', 'Don Meyer was MITER and DDNI ATNF'),
    ('Battel Memorial Institute', 'DOE', 'Manages Labs', 'Battel manages numerous DOE national lab institutions'),
    ('Sandia National Laboratories', 'Nevada Test and Training Range', 'Manages', 'Sandia manages Tonopah Test Range on NTR'),
    
    # Agency to Contractor
    ('Lockheed Martin', 'CIA DS&T', 'Kona Blue Blocked', 'CIA DS&T blocked Lockheed material transfer to Bigelow in Kona Blue'),
    ('MITER Corporation', 'Lockheed Martin', 'Program Admin', 'FFRDCs serve as program admins for defense industrial contractors'),
    ('MITER Corporation', 'Northrop Grumman', 'Program Admin', 'FFRDCs serve as program admins for defense industrial contractors'),
    ('DOE NEST', 'Sandia National Laboratories', 'Contractor', 'Sandia designs systems for DOE NEST operations'),
    ('DOE NEST', 'Lawrence Livermore National Laboratory', 'Contractor', 'NEST comprised of contractors from national labs'),
    ('DOE NEST', 'Los Alamos National Laboratory', 'Contractor', 'NEST comprised of contractors from national labs'),
    ('DOE NEST', 'EG&G', 'Contractor', 'EG&G (now Amentum) is NEST contractor'),
    
    # Program to Agency
    ('Immaculate Constellation', 'NRO', 'Utilizes Platforms', 'Uses NRO spy satellites and overhead collection platforms'),
    ('Immaculate Constellation', 'NGA', 'Utilizes Platforms', 'Uses NGA overhead collection platforms'),
    ('Kona Blue', 'DHS', 'Sponsored', 'DHS sponsored USAP program'),
    ('Kona Blue', 'Lockheed Martin', 'Prime Contractor', 'Lockheed was prime contractor for Kona Blue'),
    ('Kona Blue', 'Bigelow Aerospace Advanced Space Studies', 'Participant', 'BAASS was intended recipient of materials'),
    ('Project Preserve Destiny', 'NSA', 'Operates', 'Project Preserve Destiny was NSA program'),
    ('Project Twinkle', 'Sandia National Laboratories', 'Based At', 'Project Twinkle was Sandia-based Z division investigation'),
    ('Advanced Theoretical Physics Working Group', 'BDM', 'Held At', '1985 physics group held at BDM MLAN facility'),
    
    # Facility to Agency
    ('Area 51', 'Edwards 412 Test Wing', 'Operated By', 'Edwards 412 Test Wing operates manned flights at Area 51'),
    ('Tonopah Test Range', 'Sandia National Laboratories', 'Managed By', 'Sandia manages TTR, DOE experimental weapons testing'),
    ('Pine Gap', 'NRO', 'Program B Ground Element', 'NRO Program B ground element established at Pine Gap'),
    ('Y12 Complex', 'Oak Ridge National Laboratory', 'Houses', 'Y12 complex houses Oak Ridge National Laboratory'),
    
    # Individual to Organization (high-level positions)
    ('Doug Wolfe', 'NRO', 'Executive Assistant', '16 years in NRO, executive assistant to director'),
    ('Doug Wolfe', 'CIA DS&T', 'Deputy Director', 'CIA DS&T deputy director'),
    ('Doug Wolfe', 'OGA', 'First Director', 'Started OGA in 2003'),
    ('Doug Wolfe', 'DDNI ATNF', 'Served As', 'DDNI ATNF with oversight over NRO acquisitions'),
    ('Donald Kerr', 'NRO', 'High Level Position', 'Mentioned in ATPWG notes for funding requests'),
    ('Donald Kerr', 'Los Alamos National Laboratory', 'Director', 'Director of Los Alamos'),
    ('Donald Kerr', 'CIA DS&T', 'Deputy Director', 'Deputy director of CIA DS&T'),
    ('Donald Kerr', 'EG&G', 'Director', 'Director of EG&G'),
    ('Paul Kaminsky', 'OUSD', 'Director', 'Director of OUSD, permanent SAPO oversight committee member'),
    ('Paul Kaminsky', 'MITER Corporation', 'Board Member', 'Board of trustee for MITER'),
    ('Glenn Gaffney', 'CIA DS&T', 'Deputy Director', 'CIA DS&T deputy director, blocked Kona Blue'),
    ('Mark Moahan', 'NRO', 'High Level Deputy Director', 'Very high level deputy director position'),
    ('Mark Moahan', 'CIA DS&T', 'Position', 'CIA DS&T connections'),
    ('Mark Moahan', 'OGA', 'Position', 'CIA OGA connections'),
    ('Mark Moahan', 'DDNI ATNF', 'Position', 'DDNI ATNF position'),
    ('Sean Kirkpatrick', 'AARO', 'Director', 'Former AARO director, turned coat and ran to Oak Ridge'),
    ('Sean Kirkpatrick', 'Oak Ridge National Laboratory', 'Intelligence Programs Director', 'Position pulled from website after leaving AARO'),
    ('Sean Kirkpatrick', 'MITER Corporation', 'Subcontractor', 'Nonlinear Solutions LLC subcontracting under MITER for US Spacecom'),
    
    # Historical/Program Relationships
    ('NRO', 'Program B', 'Operated', 'NRO Program B was consolidation of reconnaissance activities'),
    ('AFSWP', 'DITRA', 'Evolved Into', 'Armed Forces Special Weapons Project became Defense Threat Reduction Agency'),
    ('Sandia Base', 'AFSWP', 'Established At', 'AFSWP established 1947 at Sandia Base'),
    ('Los Alamos', 'Sandia Base', 'Z Division', 'Los Alamos Z division established operations at Sandia Base'),
]


def generate_entity_id(display_name: str) -> str:
    """Generate entity ID from display name"""
    # Convert to lowercase, replace spaces and special chars with underscores
    entity_id = display_name.lower()
    entity_id = re.sub(r'[^a-z0-9]+', '_', entity_id)
    entity_id = re.sub(r'_+', '_', entity_id)
    entity_id = entity_id.strip('_')
    # Add prefix to avoid conflicts
    return f"uapgerb_{entity_id}"


def extract_entities_from_transcript() -> List[Dict]:
    """Extract entities from predefined list"""
    entities = []
    for key, info in ENTITIES_TO_EXTRACT.items():
        entity_id = generate_entity_id(info['display_name'])
        entities.append({
            'entity_id': entity_id,
            'display_name': info['display_name'],
            'normalized_name': info['normalized_name'],
            'entity_type': info['entity_type'],
            'description': info['description'],
            'aliases': info.get('aliases', ''),
            'source': 'UAPGerb Transcript 2025'
        })
    return entities


def write_entities_csv(output_path: Path):
    """Write entities to CSV file"""
    entities = extract_entities_from_transcript()
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['entity_id', 'display_name', 'normalized_name', 'entity_type', 'description', 'aliases', 'source']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entities)
    
    print(f"[OK] Written {len(entities)} entities to {output_path}")
    return len(entities)


def write_foia_targets_csv(output_path: Path):
    """Write FOIA targets to CSV file"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['agency', 'record_request', 'timeframe', 'relevance', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(FOIA_TARGETS)
    
    print(f"[OK] Written {len(FOIA_TARGETS)} FOIA targets to {output_path}")
    return len(FOIA_TARGETS)


def write_relationships_csv(output_path: Path):
    """Write relationships to CSV file"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['source', 'target', 'label', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rel in RELATIONSHIPS:
            writer.writerow({
                'source': rel[0],
                'target': rel[1],
                'label': rel[2],
                'notes': rel[3] if len(rel) > 3 else ''
            })
    
    print(f"[OK] Written {len(RELATIONSHIPS)} relationships to {output_path}")
    return len(RELATIONSHIPS)


def main():
    """Main extraction function"""
    project_root = Path(__file__).parent.parent.parent
    entities_dir = project_root / 'data' / 'entities'
    foia_dir = project_root / 'data' / 'foia'
    
    # Create directories if they don't exist
    entities_dir.mkdir(parents=True, exist_ok=True)
    foia_dir.mkdir(parents=True, exist_ok=True)
    
    print("Extracting entities, FOIA targets, and relationships from UAPGerb transcript...")
    print("=" * 70)
    
    # Generate CSV files
    entities_count = write_entities_csv(entities_dir / 'uap_gerb_transcript_entities.csv')
    foia_count = write_foia_targets_csv(foia_dir / 'uap_gerb_transcript_foia_targets.csv')
    relationships_count = write_relationships_csv(entities_dir / 'uap_gerb_transcript_relationships.csv')
    
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Entities: {entities_count}")
    print(f"  FOIA Targets: {foia_count}")
    print(f"  Relationships: {relationships_count}")
    print("\n[OK] Extraction complete!")


if __name__ == '__main__':
    main()
