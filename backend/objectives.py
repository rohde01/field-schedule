# filename: objectives.py

from typing import Dict, List, Tuple
from ortools.sat.python import cp_model

def add_adjacency_objective(
    model: cp_model.CpModel,
    team_sessions: Dict[int, List[int]],
    presence_var: Dict[Tuple[int, int, int], cp_model.IntVar],
    top_field_ids: List[int]
) -> None:
    """
    Adds an objective to minimize, for each team, its longest chain of
    back-to-back training days. I.e., if a team has sessions on consecutive 
    days, we count them as part of the same chain. The objective is to minimize 
    the sum of these 'longest chains' across all teams.
    
    Args:
        model: The CP-SAT model instance
        team_sessions: Dictionary mapping team IDs to a list of their session IDs
        presence_var: Dictionary mapping (session_id, field_id, day) -> BoolVar
                      that is 1 if session `session_id` is assigned to field `field_id`
                      on day `day`.
        top_field_ids: List of top-level field IDs to consider
    """

    NUM_DAYS = 7

    has_session = {}
    for t_id, sess_list in team_sessions.items():
        for d in range(NUM_DAYS):
            day_bools = []
            for s in sess_list:
                for f_id in top_field_ids:
                    if (s, f_id, d) in presence_var:
                        day_bools.append(presence_var[(s, f_id, d)])
            
            var = model.NewIntVar(0, 1, f'has_session_t{t_id}_d{d}')
            model.Add(var == sum(day_bools))
            
            has_session[(t_id, d)] = var

    chain = {}
    for t_id in team_sessions:
        for d in range(NUM_DAYS):
            chain[(t_id, d)] = model.NewIntVar(0, NUM_DAYS, f'chain_t{t_id}_d{d}')

    for t_id in team_sessions:
        model.Add(chain[(t_id, 0)] == has_session[(t_id, 0)])

        for d in range(1, NUM_DAYS):
            model.Add(chain[(t_id, d)] <= chain[(t_id, d-1)] + 1)
            model.Add(chain[(t_id, d)] <= has_session[(t_id, d)] * NUM_DAYS)
            model.Add(
                chain[(t_id, d)] >= chain[(t_id, d-1)] + has_session[(t_id, d)] - NUM_DAYS * (1 - has_session[(t_id, d)])
            )
    chain_max = {}
    for t_id in team_sessions:
        chain_max[t_id] = model.NewIntVar(0, NUM_DAYS, f'chain_max_t{t_id}')
        for d in range(NUM_DAYS):
            model.Add(chain_max[t_id] >= chain[(t_id, d)])
    model.Minimize(sum(chain_max[t_id] for t_id in team_sessions))
