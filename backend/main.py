"""
Filename: main.py
Main module to solve the soccer scheduling problem.
Provides a generate_schedule function to be called from other modules.
"""

from ortools.sat.python import cp_model
from collections import defaultdict
import cProfile
import pstats
from utils import ( time_str_to_block, blocks_to_time_str, get_capacity_and_allowed, build_fields_by_id, find_top_field_and_cost)
from typing import List, Optional, Dict, Set
from objectives import add_adjacency_objective
from models.field import Field
from models.constraint import Constraint
from pydantic import BaseModel
from test import fieldConflicts 

class GenerateScheduleRequest(BaseModel):
    fields: List[Field]
    constraints: List[Constraint]
    weekday_objective: bool

def generate_schedule(request: GenerateScheduleRequest) -> Optional[List[Dict]]:
    profiler = cProfile.Profile()
    profiler.enable()

    # Build field objects and organize them
    fields_by_id, top_fields = build_fields_by_id(request.fields)
    # Build ancestor map: ancestor_map[field_id] = {set of its ancestor_ids}
    ancestor_map: Dict[int, Set[int]] = defaultdict(set)
    for fid_child, field_obj_child in fields_by_id.items():
        current_parent_id = field_obj_child.parent_field_id
        while current_parent_id is not None:
            ancestor_map[fid_child].add(current_parent_id)
            parent_obj = fields_by_id.get(current_parent_id)
            if parent_obj:
                current_parent_id = parent_obj.parent_field_id
            else:
                break

    # Build subfield resources and capacities
    resource_ids_by_top = defaultdict(list)
    capacity_by_id = {}
    for res_id, res_obj in fields_by_id.items():
        top_id, cap = find_top_field_and_cost(res_id, fields_by_id)
        capacity_by_id[res_id] = cap
        resource_ids_by_top[top_id].append(res_id)
    possible_days = list(range(7))
    top_field_ids = list(resource_ids_by_top.keys())

    # Process all constraints and convert them to session requirements
    all_sessions = []
    session_index = 0
    for c in request.constraints:
        if c.field_id is not None:
            top_f_id, sub_cost = find_top_field_and_cost(c.field_id, fields_by_id)
            final_cost = sub_cost
            forced_top_field = top_f_id
        else:
            final_cost = int(c.required_cost) if c.required_cost else 1000
            forced_top_field = None

        all_sessions.append(
            (
                session_index,
                c.team_id,
                forced_top_field,
                final_cost,
                c.length,
                c.field_id,
                c.start_time,
                c.day_of_week
            )
        )
        session_index += 1

    num_sessions = len(all_sessions)

    idx_to_day = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}

    # Build field information including capacity, allowed demand types, and time windows
    field_info = {}
    for f in top_fields:
        total_cap, allowed_demands, max_splits = get_capacity_and_allowed(f)
        day_windows = {}
        for day_enum, avail in f.availability.items():
            start_block = time_str_to_block(avail.start_time)
            end_block = time_str_to_block(avail.end_time)
            try:
                d_idx = list(idx_to_day.values()).index(day_enum.value)
            except ValueError:
                print(f"Warning: Invalid day '{day_enum.value}' in field {f.field_id} availability. Skipping.")
                continue
            day_windows[d_idx] = (start_block, end_block)

        field_info[f.field_id] = {
            'total_cap': total_cap,
            'allowed_demands': allowed_demands,
            'max_splits': max_splits,
            'day_windows': day_windows
        }

    # Collect all possible start/end times across all fields
    all_starts = []
    all_ends = []
    for f in top_fields:
        if f.field_id in field_info:
            for (start_blk, end_blk) in field_info[f.field_id]['day_windows'].values():
                all_starts.append(start_blk)
                all_ends.append(end_blk)
        else:
             print(f"Warning: Field {f.field_id} not found in field_info during availability check.")

    if not all_starts:
        print("No field availability found across all fields. No feasible solution possible.")
        profiler.disable()
        return None

    model = cp_model.CpModel()

    # --- Create Variables --- 
    presence_var = {}
    start_var_main = {}
    end_var_main = {}
    interval_var_main = {}
    demands_capacity_main = {}
    demands_splits_main = {}
    session_presence_vars = [[] for _ in range(num_sessions)]

    # Iterate through each session and create potential assignment variables
    for s in range(num_sessions):
        (
            sid, team_id, forced_field, req_capacity, length_15,
            req_field_id, c_start_time, c_day_of_week
        ) = all_sessions[s]
        duration_main = length_15

        if forced_field:
            possible_top_fields = [f for f in top_fields if f.field_id == forced_field]
            if not possible_top_fields:
                 print(f"Warning: Forced field {forced_field} for session {sid} not found in top_fields list.")
                 continue
        else:
            possible_top_fields = top_fields

        # Generate assignment on subfields matching required capacity
        for f_obj in possible_top_fields:
            top_id = f_obj.field_id
            fi = field_info.get(top_id)
            if not fi or req_capacity not in fi['allowed_demands']:
                continue
            for res_id in resource_ids_by_top[top_id]:
                if capacity_by_id.get(res_id) != req_capacity:
                    continue
                for d in possible_days:
                    if d not in fi['day_windows']:
                        continue
                    ws, we = fi['day_windows'][d]
                    if we - ws < duration_main:
                        continue
                    pres = model.NewBoolVar(f'pres_s{sid}_r{res_id}_d{d}')
                    presence_var[(s, res_id, d)] = pres
                    session_presence_vars[s].append(pres)
                    s_var = model.NewIntVar(ws, we - duration_main, f'start_s{sid}_r{res_id}_d{d}')
                    e_var = model.NewIntVar(ws + duration_main, we, f'end_s{sid}_r{res_id}_d{d}')
                    interval = model.NewOptionalIntervalVar(s_var, duration_main, e_var, pres, f'interval_s{sid}_r{res_id}_d{d}')
                    start_var_main[(s, res_id, d)] = s_var
                    end_var_main[(s, res_id, d)] = e_var
                    interval_var_main[(s, res_id, d)] = interval
                    demands_capacity_main[(s, res_id, d)] = req_capacity
                    # enforce fixed start if specified
                    if c_start_time is not None:
                        fb = time_str_to_block(c_start_time)
                        if ws <= fb <= we - duration_main:
                            model.Add(s_var == fb).OnlyEnforceIf(pres)
                        else:
                            model.Add(pres == 0)
                            print(f"Warning: Fixed start {c_start_time} for session {sid} on res {res_id} day {d} outside [{blocks_to_time_str(ws)}, {blocks_to_time_str(we-duration_main)}]")

    # Ensure each session is assigned exactly once
    for s in range(num_sessions):
        if session_presence_vars[s]:
             model.AddExactlyOne(session_presence_vars[s])
        else:
             print(f"Error: Session {s} (Team {all_sessions[s][1]}) has no possible field/day assignments based on constraints and availability. Problem is infeasible.")
             profiler.disable()
             return None

    # Capacity on top-level and no overlap on each subfield per day
    for top_id, fi in field_info.items():
        cap = fi['total_cap']
        for d in fi['day_windows']:
            ints_top, demands_top = [], []
            intervals_by_res_id = defaultdict(list)
            for res_id_under_top in resource_ids_by_top[top_id]:
                for s_idx in range(num_sessions):
                    key = (s_idx, res_id_under_top, d)
                    if key in interval_var_main:
                        iv = interval_var_main[key]
                        intervals_by_res_id[res_id_under_top].append(iv)
                        ints_top.append(iv)
                        demands_top.append(demands_capacity_main[key])
            # no overlap on same resource
            for specific_intervals in intervals_by_res_id.values():
                if specific_intervals:
                    model.AddNoOverlap(specific_intervals)
            # no overlap for ancestor-descendant resources
            res_ids = list(intervals_by_res_id.keys())
            for i in range(len(res_ids)):
                for j in range(i+1, len(res_ids)):
                    ra, rb = res_ids[i], res_ids[j]
                    if ra in ancestor_map.get(rb, set()) or rb in ancestor_map.get(ra, set()):
                        combined = intervals_by_res_id[ra] + intervals_by_res_id[rb]
                        if combined:
                            model.AddNoOverlap(combined)
            # cumulative capacity constraint
            if ints_top:
                model.AddCumulative(ints_top, demands_top, cap)

    # Add constraint that teams can only have one session per day
    team_sessions = defaultdict(list)
    for s, session_data in enumerate(all_sessions):
        team_id = session_data[1]
        team_sessions[team_id].append(s)

    for team_id, sess_list in team_sessions.items():
        for d in range(7):
            bools_for_that_day = [presence_var[k] for k in presence_var if k[0] in sess_list and k[2] == d]
            if bools_for_that_day:
                model.Add(sum(bools_for_that_day) <= 1)

    # Add objective function based on request type
    if request.weekday_objective:
        add_adjacency_objective(model, team_sessions, presence_var, top_field_ids)
    else:
        pass

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Process solution if found
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        solution_type = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE (not optimal)"
        print(f"Found a {solution_type} solution!")
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats(10)

        # Extract solution and format for return
        solution = []
        for s in range(num_sessions):
            session_data = all_sessions[s]
            sid, team_id, _, req_capacity, _, req_field_id, _, _ = session_data

            chosen_day = None
            chosen_field = None
            assigned_start_main = None
            assigned_end_main = None

            for (sess_id, res_id, d) in presence_var:
                if sess_id == s and solver.Value(presence_var[(sess_id, res_id, d)]) == 1:
                    chosen_field = res_id
                    chosen_day = d
                    assigned_start_main = solver.Value(start_var_main[(sess_id, res_id, d)])
                    assigned_end_main = solver.Value(end_var_main[(sess_id, res_id, d)])
                    break

            if chosen_field is None or chosen_day is None:
                 print(f"Error: No assignment found for session {sid} (Team {team_id}) in the solution. This indicates an issue.")
                 continue

            start_str_main = blocks_to_time_str(assigned_start_main)
            end_str_main   = blocks_to_time_str(assigned_end_main)
            day_str = idx_to_day.get(chosen_day, "UnknownDay")

            main_session = {
                "session_id": sid,
                "team_id": team_id,
                "day_of_week": day_str,
                "start_time": start_str_main,
                "end_time": end_str_main,
                "field_id": chosen_field,
                "required_cost": req_capacity,
                "required_field": req_field_id,
            }
            solution.append(main_session)

        # Subfield assignment integrated; solution intervals reflect subfield picks

        # run conflict detection on generated solution
        field_list = list(fields_by_id.values())
        fieldConflicts(solution, field_list)
        return solution

    else:
        status_str = solver.StatusName(status)
        print(f"No feasible solution found. Solver status: {status_str}")
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats(10)
        return None
