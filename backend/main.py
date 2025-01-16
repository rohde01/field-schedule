"""
Filename: main.py 
Main module to solve the soccer scheduling problem.
Provides a generate_schedule function to be called from other modules.
"""

from ortools.sat.python import cp_model
from collections import defaultdict
import cProfile
import pstats
from utils import ( time_str_to_block, get_capacity_and_allowed, teams_to_constraints, SIZE_TO_CAPACITY, build_fields_by_id, find_top_field_and_cost)
from database.schedules import save_schedule
from database.fields import get_fields_by_facility
from assign_subfields import post_process_solution
from typing import List, Any, Optional

def generate_schedule(facility_id: int, team_ids: List[int], club_id: int, schedule_name: str = "Generated Schedule", constraints_list: Optional[List[Any]] = None) -> int:
    profiler = cProfile.Profile()
    profiler.enable()

    top_fields = get_fields_by_facility(facility_id)
    fields_by_id, fields = build_fields_by_id(top_fields)

    default_constraints = teams_to_constraints(team_ids)
    constraints_list = default_constraints + (constraints_list or [])

    all_sessions = []
    session_index = 0
    for c in constraints_list:
        if c.required_field is not None:
            top_f_id, sub_cost = find_top_field_and_cost(c.required_field, fields_by_id)
            final_cost = sub_cost
            forced_top_field = top_f_id
        else:
            final_cost = int(c.required_cost) if c.required_cost else 1000
            forced_top_field = None

        for _ in range(c.sessions):
            all_sessions.append(
                (
                    session_index,
                    c.team_id,
                    forced_top_field,
                    final_cost,
                    c.length,
                    c.required_field,
                    c.start_time
                )
            )
            session_index += 1

    num_sessions = len(all_sessions)
    day_to_idx = {'Mon':0,'Tue':1,'Wed':2,'Thu':3,'Fri':4,'Sat':5,'Sun':6}
    idx_to_day = {v: k for k, v in day_to_idx.items()}

    # Build the field_info for each top-level field
    field_info = {}
    for f in fields:
        total_cap, allowed_demands, max_splits = get_capacity_and_allowed(f)
        day_windows = {}
        for day, avail in f.availability.items():
            start_block = time_str_to_block(avail.start_time)
            end_block = time_str_to_block(avail.end_time)
            day_windows[day_to_idx[day]] = (start_block, end_block)
        field_info[f.field_id] = {
            'total_cap': total_cap,
            'allowed_demands': allowed_demands,
            'max_splits': max_splits,
            'day_windows': day_windows
        }

    all_starts = []
    all_ends = []
    for f in fields:
        fi = field_info[f.field_id]
        for (start_blk, end_blk) in fi['day_windows'].values():
            all_starts.append(start_blk)
            all_ends.append(end_blk)

    if not all_starts:
        print("No field availability found, no feasible solution.")
        return None

    model = cp_model.CpModel()

    # Revised variable creation: one start/end per (session, field, day)
    presence_var = {}
    start_var = {}
    end_var = {}
    session_intervals = {}
    demands_capacity = {}
    demands_splits = {}
    session_presence_vars = [[] for _ in range(num_sessions)]

    for s in range(num_sessions):
        sid, team_id, forced_field, req_capacity, length_15, req_field_id, c_start_time = all_sessions[s]
        duration = length_15

        possible_top_fields = [fields_by_id[forced_field]] if forced_field else fields

        for f in possible_top_fields:
            f_id = f.field_id
            fi = field_info[f_id]

            if req_capacity not in fi['allowed_demands']:
                continue

            for d in range(7):
                if d not in fi['day_windows']:
                    continue

                (window_start, window_end) = fi['day_windows'][d]
                if window_end - window_start < duration:
                    continue

                pres = model.NewBoolVar(f'pres_s{sid}_f{f_id}_d{d}')
                presence_var[(s, f_id, d)] = pres
                session_presence_vars[s].append(pres)

                s_var = model.NewIntVar(window_start, window_end - duration,
                                        f'start_s{sid}_f{f_id}_d{d}')
                e_var = model.NewIntVar(window_start + duration, window_end,
                                        f'end_s{sid}_f{f_id}_d{d}')

                start_var[(s, f_id, d)] = s_var
                end_var[(s, f_id, d)]   = e_var

                interval = model.NewOptionalIntervalVar(
                    s_var,
                    duration,
                    e_var,
                    pres,
                    f'interval_s{sid}_f{f_id}_d{d}'
                )
                session_intervals[(s, f_id, d)] = interval

                demands_capacity[(s, f_id, d)] = req_capacity
                demands_splits[(s, f_id, d)]   = 1

                if c_start_time is not None:
                    fixed_block = time_str_to_block(c_start_time)
                    model.Add(s_var == fixed_block).OnlyEnforceIf(pres)

    for s in range(num_sessions):
        model.AddExactlyOne(session_presence_vars[s])

    for f in fields:
        f_id = f.field_id
        fi = field_info[f_id]
        cap = fi['total_cap']
        max_splits = fi['max_splits']

        for d in range(7):
            if d not in fi['day_windows']:
                continue

            intervals_fd = []
            capacity_demands = []
            splits_demands = []
            for s in range(num_sessions):
                if (s, f_id, d) in session_intervals:
                    intervals_fd.append(session_intervals[(s, f_id, d)])
                    capacity_demands.append(demands_capacity[(s, f_id, d)])
                    splits_demands.append(demands_splits[(s, f_id, d)])

            if intervals_fd:
                model.AddCumulative(intervals_fd, capacity_demands, cap)
                model.AddCumulative(intervals_fd, splits_demands, max_splits)

    # Each team at most one session per day
    team_sessions = defaultdict(list)
    for s, (sid, team_id, forced_field, req_capacity, length_15, req_field_id, c_start_time) in enumerate(all_sessions):
        team_sessions[team_id].append(s)

    top_field_ids = [f.field_id for f in fields]
    for team_id, sess_list in team_sessions.items():
        for d in range(7):
            bools_for_that_day = []
            for s in sess_list:
                for f_id in top_field_ids:
                    if (s, f_id, d) in presence_var:
                        bools_for_that_day.append(presence_var[(s, f_id, d)])
            if bools_for_that_day:
                model.Add(sum(bools_for_that_day) <= 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("Found a feasible solution!")
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats(10)

        solution = []
        for s in range(num_sessions):
            sid, team_id, forced_field, req_capacity, length_15, req_field_id, c_start_time = all_sessions[s]
            chosen_day = None
            chosen_field = None
            assigned_start = None
            assigned_end   = None

            for f_id in top_field_ids:
                for d in range(7):
                    key = (s, f_id, d)
                    if key in presence_var and solver.Value(presence_var[key]) == 1:
                        chosen_field = f_id
                        chosen_day   = d
                        assigned_start = solver.Value(start_var[key])
                        assigned_end   = solver.Value(end_var[key])
                        break
                if chosen_field is not None:
                    break

            hh = assigned_start // 4
            mm = (assigned_start % 4) * 15
            start_str = f"{hh:02d}:{mm:02d}"

            hh_end = assigned_end // 4
            mm_end = (assigned_end % 4) * 15
            end_str = f"{hh_end:02d}:{mm_end:02d}"

            solution.append({
                "team_id": team_id,
                "day_of_week": idx_to_day[chosen_day],
                "start_time": start_str,
                "end_time": end_str,
                "field_id": chosen_field,
                "required_cost": req_capacity,
                "required_field": req_field_id
            })

        # Post-process subfield assignment (not part of main scheduling model)
        solution = post_process_solution(solution, top_fields)
        schedule_id = save_schedule(solution, club_id=club_id, facility_id=facility_id, name=schedule_name)
        print(f"Schedule saved successfully with ID: {schedule_id}")

        for sess in solution:
            print(sess)
        return solution
    else:
        print("No feasible solution found.")
        return None
