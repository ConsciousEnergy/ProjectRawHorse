#!/usr/bin/env python3
"""
Date extraction utilities for financial flows
"""
import re
from datetime import datetime, date
from typing import Optional
try:
    import dateparser
    HAS_DATEPARSER = True
except ImportError:
    HAS_DATEPARSER = False


def extract_date(text: str, reference_date: Optional[date] = None) -> Optional[date]:
    """
    Extract date from text
    Returns date object or None
    """
    if not text:
        return None
    
    # Use dateparser if available (more flexible)
    if HAS_DATEPARSER:
        try:
            parsed = dateparser.parse(text, settings={
                'RELATIVE_BASE': reference_date or datetime.now(),
                'PREFER_DATES_FROM': 'past'
            })
            if parsed:
                return parsed.date()
        except:
            pass
    
    # Pattern-based extraction
    date_patterns = [
        # Full dates: MM/DD/YYYY, DD-MM-YYYY
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', lambda m: _parse_numeric_date(m)),
        # Month name dates: January 15, 2024
        (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', lambda m: _parse_month_name_date(m)),
        # Abbreviated month: Jan 15, 2024
        (r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})', lambda m: _parse_abbrev_date(m)),
        # Year only: in 2024, during 2024
        (r'(?:in|during|on)\s+(\d{4})', lambda m: _parse_year_only(m)),
    ]
    
    for pattern, parser in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                parsed_date = parser(match)
                if parsed_date:
                    return parsed_date
            except (ValueError, AttributeError):
                continue
    
    return None


def _parse_numeric_date(match) -> Optional[date]:
    """Parse numeric date format"""
    try:
        part1, part2, year = match.groups()
        year = int(year)
        if year < 100:
            year += 2000 if year < 50 else 1900
        
        # Try MM/DD/YYYY first
        try:
            month, day = int(part1), int(part2)
            if 1 <= month <= 12 and 1 <= day <= 31:
                return date(year, month, day)
        except ValueError:
            pass
        
        # Try DD/MM/YYYY
        try:
            day, month = int(part1), int(part2)
            if 1 <= month <= 12 and 1 <= day <= 31:
                return date(year, month, day)
        except ValueError:
            pass
    except (ValueError, AttributeError):
        pass
    return None


def _parse_month_name_date(match) -> Optional[date]:
    """Parse month name date format"""
    try:
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        month_name, day, year = match.groups()
        month = month_names.get(month_name.lower())
        if month:
            return date(int(year), month, int(day))
    except (ValueError, AttributeError):
        pass
    return None


def _parse_abbrev_date(match) -> Optional[date]:
    """Parse abbreviated month date format"""
    try:
        month_abbrev = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        day, month_abbrev_str, year = match.groups()
        month = month_abbrev.get(month_abbrev_str.lower())
        if month:
            return date(int(year), month, int(day))
    except (ValueError, AttributeError):
        pass
    return None


def _parse_year_only(match) -> Optional[date]:
    """Parse year-only format (returns January 1 of that year)"""
    try:
        year = int(match.group(1))
        if 1900 <= year <= 2100:
            return date(year, 1, 1)
    except (ValueError, AttributeError):
        pass
    return None
