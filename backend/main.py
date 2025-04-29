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
from assign_subfields import post_process_solution
from typing import List, Optional, Dict
from objectives import add_adjacency_objective
from models.field import Field
from models.constraint import Constraint
from pydantic import BaseModel

class GenerateScheduleRequest(BaseModel):
    fields: List[Field]
    constraints: List[Constraint]
    weekday_objective: bool

def generate_schedule(request: GenerateScheduleRequest) -> Optional[List[Dict]]:
    profiler = cProfile.Profile()
    profiler.enable()

    # Build field objects and organize them
    fields_by_id, top_fields = build_fields_by_id(request.fields)

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

        if c_day_of_week is not None:
            possible_days = [c_day_of_week]
        else:
            possible_days = range(7)

        for f_obj in possible_top_fields:
            f_id = f_obj.field_id
            if f_id not in field_info:
                print(f"Warning: Field ID {f_id} from possible_top_fields not found in field_info. Skipping assignment variables for session {sid}.")
                continue
            fi = field_info[f_id]

            if req_capacity not in fi['allowed_demands']:
                continue

            for d in possible_days:
                if d not in fi['day_windows']:
                    continue

                window_start, window_end = fi['day_windows'][d]
                if window_end - window_start < duration_main:
                    continue

                pres = model.NewBoolVar(f'pres_s{sid}_f{f_id}_d{d}')
                presence_var[(s, f_id, d)] = pres
                session_presence_vars[s].append(pres)

                s_main = model.NewIntVar(window_start, window_end - duration_main,
                                         f'start_s{sid}_f{f_id}_d{d}_main')
                e_main = model.NewIntVar(window_start + duration_main, window_end,
                                         f'end_s{sid}_f{f_id}_d{d}_main')
                interval_main = model.NewOptionalIntervalVar(
                    s_main, duration_main, e_main, pres,
                    f'interval_s{sid}_f{f_id}_d{d}_main'
                )

                start_var_main[(s, f_id, d)] = s_main
                end_var_main[(s, f_id, d)] = e_main
                interval_var_main[(s, f_id, d)] = interval_main
                demands_capacity_main[(s, f_id, d)] = req_capacity
                demands_splits_main[(s, f_id, d)] = 1

                if c_start_time is not None:
                    fixed_block = time_str_to_block(c_start_time)
                    if window_start <= fixed_block <= window_end - duration_main:
                        model.Add(s_main == fixed_block).OnlyEnforceIf(pres)
                    else:
                        model.Add(pres == 0)
                        print(f"Warning: Fixed start time {c_start_time} for session {sid} on field {f_id} day {d} is outside the allowed window [{blocks_to_time_str(window_start)}, {blocks_to_time_str(window_end - duration_main)}]. Disabling this option.")

    # Ensure each session is assigned exactly once
    for s in range(num_sessions):
        if session_presence_vars[s]:
             model.AddExactlyOne(session_presence_vars[s])
        else:
             print(f"Error: Session {s} (Team {all_sessions[s][1]}) has no possible field/day assignments based on constraints and availability. Problem is infeasible.")
             profiler.disable()
             return None

    # Add capacity and split constraints for each field and day
    top_field_ids = [f.field_id for f in top_fields]
    for f_id in top_field_ids:
        if f_id not in field_info:
            print(f"Warning: Field ID {f_id} not found in field_info during cumulative constraint setup. Skipping.")
            continue
        fi = field_info[f_id]
        cap = fi['total_cap']
        max_splits = fi['max_splits']

        for d in fi['day_windows']:
            intervals_fd = []
            cap_demands_fd = []
            split_demands_fd = []

            for s in range(num_sessions):
                if (s, f_id, d) in interval_var_main:
                    intervals_fd.append(interval_var_main[(s, f_id, d)])
                    cap_demands_fd.append(demands_capacity_main[(s, f_id, d)])
                    split_demands_fd.append(demands_splits_main[(s, f_id, d)])

            if intervals_fd:
                model.AddCumulative(intervals_fd, cap_demands_fd, cap)
                model.AddCumulative(intervals_fd, split_demands_fd, max_splits)

    # Add constraint that teams can only have one session per day
    team_sessions = defaultdict(list)
    for s, session_data in enumerate(all_sessions):
        team_id = session_data[1]
        team_sessions[team_id].append(s)

    for team_id, sess_list in team_sessions.items():
        for d in range(7):
            bools_for_that_day = []
            for s in sess_list:
                for f_id in top_field_ids:
                    if (s, f_id, d) in presence_var:
                        bools_for_that_day.append(presence_var[(s, f_id, d)])
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

            for f_id in top_field_ids:
                for d in range(7):
                    key = (s, f_id, d)
                    if key in presence_var and solver.Value(presence_var[key]) == 1:
                        chosen_field = f_id
                        chosen_day   = d
                        assigned_start_main = solver.Value(start_var_main[key])
                        assigned_end_main   = solver.Value(end_var_main[key])
                        break
                if chosen_field is not None:
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

        # Post-process to assign subfields
        solution = post_process_solution(solution, top_fields)

        return solution

    else:
        status_str = solver.StatusName(status)
        print(f"No feasible solution found. Solver status: {status_str}")
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats(10)
        return None
