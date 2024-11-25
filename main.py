"""
Filename: main.py 
Main module to solve the soccer scheduling problem.
Provides a generate_schedule function to be called from other modules.
"""

import cProfile
import pstats
from typing import List, Dict, Any, Optional
from ortools.sat.python import cp_model
from collections import defaultdict
from database.teams import get_teams_by_ids
from database.fields import get_fields
from database.constraints import get_constraints
from database.schedules import save_schedule
from utils import (
    build_time_slots,
    get_subfields,
    get_size_to_combos,
    get_subfield_availability,
    get_subfield_areas,
    get_cost_to_combos,
    get_field_costs,
    get_field_to_smallest_subfields,
)
from model import create_variables
from constraints import (
    add_no_overlapping_sessions_constraints,
    add_no_double_booking_constraints,
    add_field_availability_constraints,
    add_team_day_constraints,
    add_allowed_assignments_constraints,
)
from objectives import add_objective_function

def add_objectives(model: cp_model.CpModel, teams: List[Any], interval_vars: Dict[int, Any], time_slots: Dict[str, List[str]], day_name_to_index: Dict[str, int]) -> None:
    """
    Adds an objective function to the model to minimize penalties for undesirable scheduling patterns
    and reward desirable ones.
    """
    add_objective_function(model, teams, interval_vars, time_slots, day_name_to_index)


def add_constraints(model: cp_model.CpModel, teams: List[Any], constraints: Dict[int, List[Any]], time_slots: Dict[str, List[str]], size_to_combos: Dict[Any, Any],
                    interval_vars: Dict[int, Any], assigned_fields: Dict[int, Any], subfield_areas: Dict[str, List[str]], subfield_availability: Dict[str, Dict[str, List[bool]]], global_time_slots: List[Any]) -> None:
    """
    Adds various constraints to the model.
    """
    add_no_overlapping_sessions_constraints(model, teams, interval_vars)
    add_no_double_booking_constraints(model, teams, interval_vars, assigned_fields, subfield_areas, global_time_slots)
    add_field_availability_constraints(model, interval_vars, assigned_fields, subfield_availability, global_time_slots)
    add_team_day_constraints(model, interval_vars)
    add_allowed_assignments_constraints(model, interval_vars)

def solve_model(model: cp_model.CpModel) -> Any:
    """
    Solves the CP-SAT model.
    """
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    return solver, status

def generate_schedule(facility_id: int, team_ids: List[int], constraints_list: Optional[List[Any]] = None) -> int:
    """
    Generates a schedule based on the provided facility_id, team_ids, and constraints_list.
    Returns the schedule_id if successful.
    """
    profiler = cProfile.Profile()
    profiler.enable()

    constraints: Dict[int, List[Any]] = defaultdict(list)
    if constraints_list:
        for constraint in constraints_list:
            constraints[constraint.team_id].append(constraint)
    else:
        constraints_list = get_constraints()
        for constraint in constraints_list:
            constraints.setdefault(constraint.team_id, []).append(constraint)

    # Fetch teams
    teams = get_teams_by_ids(team_ids)
    if not teams:
        raise ValueError("No teams found for the given team IDs")

    # Fetch fields
    fields = get_fields(facility_id)
    if not fields:
        raise ValueError("No fields found for the given facility ID")

    # Build field mappings
    field_name_to_id: Dict[str, int] = {}
    for field in fields:
        field_name_to_id[field.name] = field.field_id
        for half_subfield in field.half_subfields:
            field_name_to_id[half_subfield.name] = half_subfield.field_id
        for quarter_subfield in field.quarter_subfields:
            field_name_to_id[quarter_subfield.name] = quarter_subfield.field_id

    time_slots, all_days = build_time_slots(fields)
    all_subfields = get_subfields(fields)
    subfield_availability = get_subfield_availability(fields, time_slots, all_subfields)
    size_to_combos = get_size_to_combos(fields)
    subfield_areas = get_subfield_areas(fields)
    field_costs = get_field_costs()
    cost_to_combos = get_cost_to_combos(fields, field_costs)
    field_to_smallest_subfields, smallest_subfields_list = get_field_to_smallest_subfields(fields)

    parent_field_names = set()
    for field in fields:
        parent_field_names.add(field.name)
    parent_field_name_to_id = {name: idx for idx, name in enumerate(parent_field_names)}
    parent_field_id_to_name = {idx: name for name, idx in parent_field_name_to_id.items()}

    model = cp_model.CpModel()

    # Create variables
    interval_vars, assigned_fields, global_time_slots, day_name_to_index = create_variables(
        model, teams, constraints, time_slots, size_to_combos, cost_to_combos, parent_field_name_to_id, fields
    )

    # Add constraints
    add_constraints(model, teams, constraints, time_slots, size_to_combos,
                    interval_vars, assigned_fields, subfield_areas, subfield_availability, global_time_slots)

    # Add objectives
    add_objectives(model, teams, interval_vars, time_slots, day_name_to_index)

    # Solve the model
    solver, status = solve_model(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # Save the schedule
        schedule_id = save_schedule(solver, teams, interval_vars, field_name_to_id, club_id=1, constraints_list=constraints_list)
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats(10)
        return schedule_id
    else:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats(10)
        raise ValueError('No feasible solution found.')