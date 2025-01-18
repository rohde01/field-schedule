"""
Filename: main.py
Main module to solve the soccer scheduling problem.
Provides a generate_schedule function to be called from other modules.
"""

from ortools.sat.python import cp_model
from collections import defaultdict
import cProfile
import pstats
from utils import ( time_str_to_block, blocks_to_time_str, get_capacity_and_allowed, teams_to_constraints, build_fields_by_id, find_top_field_and_cost)
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

        partial_time = c.partial_time or 0
        partial_cost = c.partial_cost or 0

        for _ in range(c.sessions):
            all_sessions.append(
                (
                    session_index,
                    c.team_id,
                    forced_top_field,
                    final_cost,
                    c.length,
                    c.required_field,
                    c.start_time,
                    c.day_of_week,
                    partial_time,
                    partial_cost
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
        for day_name, avail in f.availability.items():
            start_block = time_str_to_block(avail.start_time)
            end_block = time_str_to_block(avail.end_time)
            d_idx = day_to_idx[day_name]
            day_windows[d_idx] = (start_block, end_block)

        field_info[f.field_id] = {
            'total_cap': total_cap,
            'allowed_demands': allowed_demands,
            'max_splits': max_splits,
            'day_windows': day_windows
        }

    all_starts = []
    all_ends = []
    for f in fields:
        for (start_blk, end_blk) in field_info[f.field_id]['day_windows'].values():
            all_starts.append(start_blk)
            all_ends.append(end_blk)
    if not all_starts:
        print("No field availability found, no feasible solution.")
        return None

    model = cp_model.CpModel()

    # Variables for presence, start, end, intervals
    presence_var = {}
    start_var_main = {}
    end_var_main = {}
    interval_var_main = {}
    demands_capacity_main = {}
    demands_splits_main = {}
    start_var_partial = {}
    end_var_partial = {}
    interval_var_partial = {}
    demands_capacity_partial = {}
    demands_splits_partial = {}
    session_presence_vars = [[] for _ in range(num_sessions)]

    for s in range(num_sessions):
        ( sid, team_id, forced_field, req_capacity, length_15, req_field_id, c_start_time, c_day_of_week, partial_time, partial_cost
        ) = all_sessions[s]
        # If partial_time > 0, the total session duration is length_15 + partial_time
        duration_main = length_15
        duration_partial = partial_time
        duration_total = duration_main + duration_partial

        if forced_field:
            possible_top_fields = [fields_by_id[forced_field]]
        else:
            possible_top_fields = fields

        if c_day_of_week is not None:
            possible_days = [c_day_of_week]
        else:
            possible_days = range(7)

        for f_obj in possible_top_fields:
            f_id = f_obj.field_id
            fi = field_info[f_id]

            if req_capacity not in fi['allowed_demands']:
                continue

            for d in possible_days:
                if d not in fi['day_windows']:
                    continue

                window_start, window_end = fi['day_windows'][d]
                if window_end - window_start < duration_total:
                    continue

                pres = model.NewBoolVar(f'pres_s{sid}_f{f_id}_d{d}')
                presence_var[(s, f_id, d)] = pres
                session_presence_vars[s].append(pres)

                # Main session interval
                if duration_partial > 0:
                    s_main = model.NewIntVar(window_start, window_end - duration_total,
                                             f'start_s{sid}_f{f_id}_d{d}_main')
                    e_main = model.NewIntVar(window_start + duration_main,
                                             window_end - duration_partial,
                                             f'end_s{sid}_f{f_id}_d{d}_main')
                else:
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
                demands_splits_main[(s, f_id, d)] = 1  # or your own logic for "splits"

                # Partial session interval if needed
                if duration_partial > 0:
                    s_part = model.NewIntVar(window_start + duration_main,
                                             window_end - duration_partial,
                                             f'start_s{sid}_f{f_id}_d{d}_part')
                    e_part = model.NewIntVar(window_start + duration_main + duration_partial,
                                             window_end,
                                             f'end_s{sid}_f{f_id}_d{d}_part')

                    interval_partial_ = model.NewOptionalIntervalVar(
                        s_part, duration_partial, e_part, pres,
                        f'interval_s{sid}_f{f_id}_d{d}_part'
                    )

                    # Force partial to start exactly where main ends
                    model.Add(s_part == e_main).OnlyEnforceIf(pres)

                    start_var_partial[(s, f_id, d)] = s_part
                    end_var_partial[(s, f_id, d)] = e_part
                    interval_var_partial[(s, f_id, d)] = interval_partial_
                    demands_capacity_partial[(s, f_id, d)] = partial_cost
                    demands_splits_partial[(s, f_id, d)] = 1

                if c_start_time is not None:
                    fixed_block = time_str_to_block(c_start_time)
                    model.Add(s_main == fixed_block).OnlyEnforceIf(pres)

    for s in range(num_sessions):
        model.AddExactlyOne(session_presence_vars[s])

    for f in fields:
        f_id = f.field_id
        fi = field_info[f_id]
        cap = fi['total_cap']
        max_splits = fi['max_splits']

        for d in fi['day_windows']:
            intervals_fd = []
            cap_demands_fd = []
            split_demands_fd = []

            # Collect main intervals
            for s in range(num_sessions):
                if (s, f_id, d) in interval_var_main:
                    intervals_fd.append(interval_var_main[(s, f_id, d)])
                    cap_demands_fd.append(demands_capacity_main[(s, f_id, d)])
                    split_demands_fd.append(demands_splits_main[(s, f_id, d)])
                if (s, f_id, d) in interval_var_partial:
                    intervals_fd.append(interval_var_partial[(s, f_id, d)])
                    cap_demands_fd.append(demands_capacity_partial[(s, f_id, d)])
                    split_demands_fd.append(demands_splits_partial[(s, f_id, d)])

            if intervals_fd:
                model.AddCumulative(intervals_fd, cap_demands_fd, cap)
                model.AddCumulative(intervals_fd, split_demands_fd, max_splits)

    team_sessions = defaultdict(list)
    for s, (sid, team_id, forced_field, req_capacity, length_15,
            req_field_id, c_start_time, c_day_of_week,
            partial_time, partial_cost) in enumerate(all_sessions):
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
            sid, team_id, forced_field, req_capacity, length_15, req_field_id, c_start_time, c_day_of_week, partial_time, partial_cost = all_sessions[s]
            chosen_day = None
            chosen_field = None
            assigned_start_main = None
            assigned_end_main = None
            assigned_start_partial = None
            assigned_end_partial = None
            for f_id in top_field_ids:
                for d in range(7):
                    key = (s, f_id, d)
                    if key in presence_var and solver.Value(presence_var[key]) == 1:
                        chosen_field = f_id
                        chosen_day   = d
                        assigned_start_main = solver.Value(start_var_main[key])
                        assigned_end_main   = solver.Value(end_var_main[key])
                        
                        if partial_time > 0 and key in start_var_partial:
                            assigned_start_partial = solver.Value(start_var_partial[key])
                            assigned_end_partial   = solver.Value(end_var_partial[key])
                        break
                if chosen_field is not None:
                    break

            # Main interval record
            start_str_main = blocks_to_time_str(assigned_start_main)
            end_str_main   = blocks_to_time_str(assigned_end_main)

            main_session = {
                "team_id": team_id,
                "day_of_week": idx_to_day[chosen_day],
                "start_time": start_str_main,
                "end_time": end_str_main,
                "field_id": chosen_field,
                "required_cost": req_capacity,
                "required_field": req_field_id
            }
            solution.append(main_session)

            # Partial interval record
            if partial_time > 0 and assigned_start_partial is not None:
                start_str_part = blocks_to_time_str(assigned_start_partial)
                end_str_part   = blocks_to_time_str(assigned_end_partial)

                partial_session = {
                    "team_id": team_id,
                    "day_of_week": idx_to_day[chosen_day],
                    "start_time": start_str_part,
                    "end_time": end_str_part,
                    "field_id": chosen_field,
                    "required_cost": partial_cost,
                    "required_field": req_field_id
                }
                solution.append(partial_session)

        solution = post_process_solution(solution, top_fields)
        print(solution)
        schedule_id = save_schedule(solution, club_id=club_id, facility_id=facility_id, name=schedule_name)
        print(f"Schedule saved successfully with ID: {schedule_id}")

        for sess in solution:
            print(sess)
        return schedule_id
    else:
        print("No feasible solution found.")
        return None
