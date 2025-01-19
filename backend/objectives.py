"""
filename: objectives.py
description: This file contains objective functions to be used in the CP-SAT model.
"""

from typing import Dict, List, Tuple
from ortools.sat.python import cp_model

def add_adjacency_objective(
    model: cp_model.CpModel,
    team_sessions: Dict[int, List[int]],
    presence_var: Dict[Tuple[int, int, int], cp_model.IntVar],
    top_field_ids: List[int]
) -> None:
    """
    Adds the adjacency objective to minimize consecutive practice days for teams.
    
    Args:
        model: The CP-SAT model instance
        team_sessions: Dictionary mapping team IDs to their session IDs
        presence_var: Dictionary mapping (session_id, field_id, day) to presence variables
        top_field_ids: List of field IDs to consider
    """
    # Calculate has_session variables for each team and day
    has_session_var = {}
    for t_id, sess_list in team_sessions.items():
        for d in range(7):
            bools_for_that_day = []
            for s in sess_list:
                for f_id in top_field_ids:
                    if (s, f_id, d) in presence_var:
                        bools_for_that_day.append(presence_var[(s, f_id, d)])
            var = model.NewIntVar(0, 1, f'has_session_t{t_id}_d{d}')
            has_session_var[(t_id, d)] = var
            model.Add(var == sum(bools_for_that_day))

    # Create adjacency variables and constraints
    adjacency_vars = []
    for t_id, _ in team_sessions.items():
        for d in range(5):
            adj = model.NewBoolVar(f"adjacency_t{t_id}_d{d}")
            # If we have a session on day d and d+1, adjacency is 1
            model.Add(has_session_var[(t_id, d)] + has_session_var[(t_id, d+1)] == 2).OnlyEnforceIf(adj)
            model.Add(has_session_var[(t_id, d)] + has_session_var[(t_id, d+1)] < 2).OnlyEnforceIf(adj.Not())
            adjacency_vars.append(adj)

    # Set the objective to minimize the sum of adjacencies
    model.Minimize(sum(adjacency_vars))
