"""
Filename: main.py 
Main module to solve the soccer scheduling problem.
Provides a generate_schedule function to be called from other modules.
"""

from ortools.sat.python import cp_model
from collections import defaultdict
import cProfile
import pstats
from utils import time_str_to_block, get_capacity_and_allowed, teams_to_constraints, SIZE_TO_CAPACITY
from database.schedules import save_schedule
from database.fields import get_fields_by_facility
from assign_subfields import post_process_solution
from typing import List, Any, Optional

def generate_schedule(facility_id: int, team_ids: List[int], club_id: int, schedule_name: str = "Generated Schedule", constraints_list: Optional[List[Any]] = None) -> int:
    profiler = cProfile.Profile()
    profiler.enable()

    top_fields = get_fields_by_facility(facility_id)

    fields_by_id = {}
    def add_field_and_descendants(field):
        fields_by_id[field.field_id] = field
        for hf in field.half_subfields:
            add_field_and_descendants(hf)
        for qf in field.quarter_subfields:
            add_field_and_descendants(qf)

    for tf in top_fields:
        add_field_and_descendants(tf)

    fields = top_fields

    default_constraints = teams_to_constraints(team_ids)
    constraints_list = default_constraints + (constraints_list or [])

    def find_top_field_and_cost(subfield_id: int) -> tuple[int, int]:
        """
        Given a subfield_id, return (top_level_field_id, cost_for_subfield).
        cost_for_subfield is derived by dividing the top-level capacity 
        based on whether subfield is 'full', 'half', or 'quarter'.
        """
        if subfield_id not in fields_by_id:
            raise ValueError(f"Unknown required_field {subfield_id}")
        sf = fields_by_id[subfield_id]
        
        # climb up to the top-level
        top_field = sf
        while top_field.parent_field_id is not None:
            top_field = fields_by_id[top_field.parent_field_id]

        top_capacity = SIZE_TO_CAPACITY[top_field.size]
        # deduce sub_cost from the subfield type
        if sf.field_type == 'full':
            sub_cost = top_capacity
        elif sf.field_type == 'half':
            sub_cost = top_capacity // 2
        elif sf.field_type == 'quarter':
            sub_cost = top_capacity // 4
        else:
            sub_cost = top_capacity

        return (top_field.field_id, sub_cost)

    all_sessions = []
    session_index = 0
    for c in constraints_list:
        if c.required_field is not None:
            top_f_id, sub_cost = find_top_field_and_cost(c.required_field)
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
                    forced_top_field,  # store top-level field or None
                    final_cost,        # capacity cost
                    c.length,
                    c.required_field,  # for post-processing
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

    # Determine global earliest and latest blocks
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

    global_earliest = min(all_starts)
    global_latest = max(all_ends)

    model = cp_model.CpModel()

    # Create start_var for each session
    start_var = []
    for s in range(num_sessions):
        sid, team_id, forced_field, req_capacity, length_15, req_field_id, c_start_time = all_sessions[s]
        if c_start_time is not None:
            fixed_block = time_str_to_block(c_start_time)
            lb = max(global_earliest, fixed_block)
            ub = min(global_latest, fixed_block)
            var = model.NewIntVar(lb, ub, f'start_s{sid}')
        else:
            var = model.NewIntVar(global_earliest, global_latest, f'start_s{sid}')
        start_var.append(var)

    presence_var = {}
    session_intervals = {}
    demands_capacity = {}
    demands_splits = {}
    session_presence_vars = [[] for _ in range(num_sessions)]

    # Build presence/intervals for each top-level field
    for s in range(num_sessions):
        sid, team_id, forced_field, req_capacity, length_15, req_field_id, c_start_time = all_sessions[s]
        duration = length_15

        # If forced_field is set, only that field is valid. Otherwise, all top_fields.
        possible_top_fields = [fields_by_id[forced_field]] if forced_field else fields

        for f in possible_top_fields:
            f_id = f.field_id
            fi = field_info[f_id]
            for d in range(7):
                if d in fi['day_windows'] and (req_capacity in fi['allowed_demands']):
                    (window_start, window_end) = fi['day_windows'][d]

                    pres = model.NewBoolVar(f'pres_s{sid}_f{f_id}_d{d}')
                    presence_var[(s, f_id, d)] = pres
                    session_presence_vars[s].append(pres)

                    interval = model.NewOptionalIntervalVar(
                        start_var[s],
                        duration,
                        model.NewIntVar(0, global_latest, ''),
                        pres,
                        f'interval_s{sid}_f{f_id}_d{d}'
                    )
                    session_intervals[(s, f_id, d)] = interval

                    demands_capacity[(s, f_id, d)] = req_capacity
                    demands_splits[(s, f_id, d)] = 1

                    model.Add(start_var[s] >= window_start).OnlyEnforceIf(pres)
                    model.Add(start_var[s] <= window_end - duration).OnlyEnforceIf(pres)

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

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Build solution
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
            for f_id in top_field_ids:
                for d in range(7):
                    if (s, f_id, d) in presence_var:
                        if solver.Value(presence_var[(s, f_id, d)]) == 1:
                            chosen_day = d
                            chosen_field = f_id
                            break
                if chosen_day is not None:
                    break

            assigned_start = solver.Value(start_var[s])
            hh = assigned_start // 4
            mm = (assigned_start % 4) * 15
            start_str = f"{hh:02d}:{mm:02d}"

            end_block = assigned_start + length_15
            hh_end = end_block // 4
            mm_end = (end_block % 4) * 15
            end_str = f"{hh_end:02d}:{mm_end:02d}"

            solution.append({
                "team_id": team_id,
                "day_of_week": idx_to_day[chosen_day],
                "start_time": start_str,
                "end_time": end_str,
                "field_id": chosen_field,
                "required_cost": req_capacity,
                "required_field": req_field_id  # Keep track so post-process can enforce exact subfield if needed
            })

        # Post-process subfield assignment
        solution = post_process_solution(solution, top_fields)

        schedule_id = save_schedule(solution, club_id=club_id, facility_id=facility_id, name=schedule_name)
        print(f"Schedule saved successfully with ID: {schedule_id}")

        for sess in solution:
            print(sess)
        return solution
    else:
        print("No feasible solution found.")
        return None