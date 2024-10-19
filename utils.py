# Filename: utils.py
# Description: Utility functions for the scheduling algorithm.

from datetime import datetime, timedelta
from config import SESSION_LENGTH_MINUTES
from dbu_requirements import get_5_star_constraints, get_3_star_constraints_girls

def generate_time_slots(fields):
    """Generates all available time slots based on fields' availability."""
    time_slots_set = set()
    for field in fields:
        for day, times in field['availability'].items():
            start_time = datetime.strptime(times['start'], '%H:%M')
            end_time = datetime.strptime(times['end'], '%H:%M')
            current_time = start_time
            while current_time + timedelta(minutes=SESSION_LENGTH_MINUTES) <= end_time:
                time_slot = f"{day}_{current_time.strftime('%H:%M')}"
                time_slots_set.add(time_slot)
                current_time += timedelta(minutes=SESSION_LENGTH_MINUTES)
    sorted_time_slots = sorted(time_slots_set)
    time_slot_indices = {ts: idx for idx, ts in enumerate(sorted_time_slots)}
    return sorted_time_slots, time_slot_indices


def extract_subfields(fields):
    """Extracts subfields and creates necessary mappings."""
    subfields = []
    subfield_to_field = {}
    field_subfields = {}
    for field in fields:
        field_subfields[field['name']] = field['subfields']
        for sf in field['subfields']:
            subfields.append(sf)
            subfield_to_field[sf] = field['name']
    subfield_indices = {sf: idx for idx, sf in enumerate(subfields)}
    return subfields, subfield_indices, subfield_to_field, field_subfields


def filter_teams_by_constraints(teams, year_constraints):
    """Filters teams based on the available constraints."""
    valid_team_years = set(year_constraints.keys())
    return [team for team in teams if team['year'] in valid_team_years]


def build_team_constraints(filtered_teams, year_constraints):
    """Builds team-specific constraints based on the year constraints."""
    team_constraints = []
    team_constraint_to_team = []
    team_constraints_indices_per_team = [[] for _ in filtered_teams]
    for t_idx, team in enumerate(filtered_teams):
        team_year = team['year']
        constraints = year_constraints[team_year]
        for constraint in constraints:
            tc_index = len(team_constraints)
            team_constraints.append({
                'team_index': t_idx,
                'required_size': constraint['required_size'],
                'sessions_required': constraint['sessions'],
                'length': constraint['length']
            })
            team_constraint_to_team.append(t_idx)
            team_constraints_indices_per_team[t_idx].append(tc_index)
    return team_constraints, team_constraint_to_team, team_constraints_indices_per_team

def get_year_constraints():
    """Fetches and organizes constraints by team year."""
    year_constraints = {}
    # Fetch constraints for boys
    boys_constraints_list = get_5_star_constraints()
    if boys_constraints_list:
        for constraint in boys_constraints_list:
            year = constraint['year']
            year_constraints.setdefault(year, []).append(constraint)
    # Fetch constraints for girls (currently not used)
    girls_constraints_list = get_3_star_constraints_girls()
    if girls_constraints_list:
        for constraint in girls_constraints_list:
            year = constraint['year']
            year_constraints.setdefault(year, []).append(constraint)
    return year_constraints