# filename: objectives.py

from typing import Dict, List, Tuple
from ortools.sat.python import cp_model

def add_adjacency_objective(
    model: cp_model.CpModel,
    team_sessions: Dict[int, List[int]],
    presence_var: Dict[Tuple[int, int, int], cp_model.IntVar],
    top_field_ids: List[int]
) -> cp_model.LinearExpr:
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
    return sum(chain_max[t_id] for t_id in team_sessions)

# Add objective to minimize year gap within each full field per day
def add_year_gap_objective(
    model: cp_model.CpModel,
    team_sessions: Dict[int, List[int]],
    presence_var: Dict[Tuple[int, int, int], cp_model.IntVar],
    resource_ids_by_top: Dict[int, List[int]],
    team_year_map: Dict[int, int]
) -> cp_model.LinearExpr:
    # Minimize differences in team years on same full field/day
    MIN_YEAR, MAX_YEAR = 4, 24
    NUM_DAYS = 7
    year_min = {}
    year_max = {}
    year_gap = {}
    # map session to its team year
    session_year = {}
    for team_id, sess_list in team_sessions.items():
        for s in sess_list:
            session_year[s] = team_year_map.get(team_id, MIN_YEAR)
    for top_id, subfields in resource_ids_by_top.items():
        for d in range(NUM_DAYS):
            y_min = model.NewIntVar(MIN_YEAR, MAX_YEAR, f'year_min_f{top_id}_d{d}')
            y_max = model.NewIntVar(MIN_YEAR, MAX_YEAR, f'year_max_f{top_id}_d{d}')
            gap = model.NewIntVar(0, MAX_YEAR - MIN_YEAR, f'year_gap_f{top_id}_d{d}')
            model.Add(gap == y_max - y_min)
            year_min[(top_id, d)] = y_min
            year_max[(top_id, d)] = y_max
            year_gap[(top_id, d)] = gap
            for (s, res_id, day), pres in presence_var.items():
                if day != d or res_id not in subfields:
                    continue
                y = session_year[s]
                # only relate min and max to active sessions
                model.Add(y_min <= y).OnlyEnforceIf(pres)
                model.Add(y_max >= y).OnlyEnforceIf(pres)
    # sum all gaps
    return sum(year_gap[(top, d)] for top in resource_ids_by_top for d in range(NUM_DAYS))
