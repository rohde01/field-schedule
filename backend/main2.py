from ortools.sat.python import cp_model
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict, List, Optional
from typing import Literal
import cProfile
import pstats
from database.fields import get_fields_by_facility
from database.index import with_db_connection

@dataclass
class FieldAvailability:
    day_of_week: Literal['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    start_time: str    # e.g. "16:00"
    end_time: str      # e.g. "20:00"

@dataclass
class Field:
    field_id: int
    facility_id: int
    name: str
    size: str                  # '11v11', '8v8', '5v5', '3v3'
    field_type: str            # e.g. 'Outdoor', 'Indoor'
    parent_field_id: Optional[int]
    is_active: bool = True
    availability: Dict[str, FieldAvailability] = field(default_factory=dict)
    quarter_subfields: List['Field'] = field(default_factory=list)
    half_subfields: List['Field'] = field(default_factory=list)

@dataclass
class Constraint:
    team_id: int
    sessions: int
    length: int               # in 15-minute blocks
    required_size: str        # '125','250','500','1000'
    start_time: Optional[str] = None  # optional fixed start time

SIZE_TO_CAPACITY = {
    '11v11': 1000,
    '8v8':   500,
    '5v5':   250,
    '3v3':   125,
}

def time_str_to_block(s: str) -> int:
    hh, mm = s.split(':')
    return int(hh)*4 + int(int(mm)//15)

def create_test_data():
    """
    Gets fields from the database and returns a tuple: (list_of_fields, list_of_constraints).
    """
    fields = get_fields_by_facility(4)  # Hardcoded facility_id=4

    constraints = [
        Constraint(team_id=1, sessions=3, length=4, required_size='1000'),# U18-2
        Constraint(team_id=1, sessions=2, length=4, required_size='500'), 

        Constraint(team_id=3, sessions=3, length=4, required_size='500'), # U13

        Constraint(team_id=2, sessions=2, length=4, required_size='1000'), # U10

        Constraint(team_id=4, sessions=3, length=4, required_size='500'), #U12

        Constraint(team_id=7, sessions=4, length=4, required_size='500'), #U16-pige

        Constraint(team_id=5, sessions=2, length=4, required_size='1000'), #U11

        Constraint(team_id=6, sessions=4, length=4, required_size='500'), #U18
    ]

    return fields, constraints

def get_capacity_and_allowed(field: Field) -> tuple[int, List[int], int]:
    total_cap = SIZE_TO_CAPACITY[field.size]
    if field.quarter_subfields:
        max_splits = 4
    elif field.half_subfields:
        max_splits = 2
    else:
        max_splits = 1
    demands = {total_cap}
    if max_splits >= 2:
        demands.add(total_cap // 2)
    if max_splits >= 4:
        demands.add(total_cap // 4)
    allowed_demands = sorted(list(demands))
    return total_cap, allowed_demands, max_splits

def assign_subfields(field: Field, day_sessions: List[dict]) -> None:
    """
    Post-process to assign specific subfields to sessions scheduled on the same field and day.
    Modifies the sessions in-place to add subfield assignments.
    """
    if not field.half_subfields and not field.quarter_subfields:
        # No subfields to assign
        return

    # Sort sessions by start time to process them in chronological order
    day_sessions.sort(key=lambda x: (x['start_time'], x['end_time']))
    
    # Track subfield usage over time
    subfield_usage = {}  # (start_block, end_block) -> set of used subfield_ids
    
    for session in day_sessions:
        start_block = time_str_to_block(session['start_time'])
        end_block = time_str_to_block(session['end_time'])
        required_size = session['required_size']
        
        # Find overlapping sessions
        overlapping_subfields = set()
        for (s, e), used_subfields in subfield_usage.items():
            if not (end_block <= s or start_block >= e):
                overlapping_subfields.update(used_subfields)
        
        # Determine available subfields based on capacity requirement
        if required_size == 1000:  # Full field
            session['field_id'] = field.field_id
        elif required_size == 500 and field.size == '11v11':  # Half field
            available_subfields = [f.field_id for f in field.half_subfields 
                                 if f.field_id not in overlapping_subfields]
            if len(available_subfields) >= 1:
                # Assign the first available subfield
                subfield = available_subfields[0]
                session['field_id'] = subfield
            else:
                print(f"Warning: Could not find available subfield for session {session}")
        elif required_size == 250 and field.size == '11v11':  # Quarter field
            available_subfields = [f.field_id for f in field.quarter_subfields 
                                 if f.field_id not in overlapping_subfields]
            if len(available_subfields) >= 1:
                # Assign the first available subfield
                subfield = available_subfields[0]
                session['field_id'] = subfield
            else:
                print(f"Warning: Could not find available subfield for session {session}")
        elif required_size == 500 and field.size == '8v8':
            session['field_id'] = field.field_id
        elif required_size == 250 and field.size == '8v8':
            available_subfields = [f.field_id for f in field.half_subfields
                                 if f.field_id not in overlapping_subfields]
            if len(available_subfields) >= 1:
                # Assign the first available subfield
                subfield = available_subfields[0]
                session['field_id'] = subfield
            else:
                print(f"Warning: Could not find available subfield for session {session}")
        elif required_size == 125 and field.size == '8v8':
            available_subfields = [f.field_id for f in field.quarter_subfields
                                 if f.field_id not in overlapping_subfields]
            if len(available_subfields) >= 1:
                # Assign the first available subfield
                subfield = available_subfields[0]
                session['field_id'] = subfield
            else:
                print(f"Warning: Could not find available subfield for session {session}")
        elif required_size == 250 and field.size == '5v5':
            session['field_id'] = field.field_id
        elif required_size == 125 and field.size == '5v5':
            available_subfields = [f.field_id for f in field.half_subfields
                                 if f.field_id not in overlapping_subfields]
            if len(available_subfields) >= 1:
                # Assign the first available subfield
                subfield = available_subfields[0]
                session['field_id'] = subfield
            else:
                print(f"Warning: Could not find available subfield for session {session}")
        elif required_size == 125 and field.size == '3v3':
            session['field_id'] = field.field_id
            
        # Update subfield usage
        if (start_block, end_block) not in subfield_usage:
            subfield_usage[(start_block, end_block)] = set()
        subfield_usage[(start_block, end_block)].add(session['field_id'])

def post_process_solution(solution: List[dict], fields: List[Field]) -> List[dict]:
    """
    Post-process the entire solution to assign specific subfields.
    """
    # Create field lookup
    field_lookup = {f.field_id: f for f in fields}
    
    # Group sessions by field and day
    field_day_sessions = defaultdict(lambda: defaultdict(list))
    for session in solution:
        field_id = session['field_id']
        day = session['day_of_week']
        # Add required_size based on team capacity
        session['required_size'] = int(session.get('required_size', 1000))  # Default to full field if not specified
        field_day_sessions[field_id][day].append(session)
    
    # Process each field's sessions
    for field_id, day_sessions in field_day_sessions.items():
        field = field_lookup[field_id]
        for day, sessions in day_sessions.items():
            assign_subfields(field, sessions)
    
    # Flatten the processed solution
    processed_solution = []
    for field_sessions in field_day_sessions.values():
        for day_sessions in field_sessions.values():
            processed_solution.extend(day_sessions)
    
    return processed_solution

@with_db_connection
def save_schedule(conn, solution: List[dict], club_id: int, facility_id: int, name: str) -> int:
    """
    Save the generated schedule to the database.
    
    Args:
        conn: Database connection from decorator
        solution: List of scheduled sessions
        club_id: ID of the club the schedule belongs to
        facility_id: ID of the facility
        name: Name of the schedule
        
    Returns:
        schedule_id: ID of the created schedule
    """
    # Insert into schedules table
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO schedules (club_id, name, facility_id)
            VALUES (%s, %s, %s)
            RETURNING schedule_id
            """,
            (club_id, name, facility_id)
        )
        schedule_id = cur.fetchone()[0]
        
        # Insert all entries
        for entry in solution:
            # Convert day of week from string to integer (0 = Monday, 6 = Sunday)
            day_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
            week_day = day_mapping[entry['day_of_week']]
            
            cur.execute(
                """
                INSERT INTO schedule_entries 
                (schedule_id, team_id, field_id, start_time, end_time, week_day)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    schedule_id,
                    entry['team_id'],
                    entry['field_id'],
                    entry['start_time'],
                    entry['end_time'],
                    week_day
                )
            )
        
        conn.commit()
        return schedule_id

def solve_field_schedule():

    profiler = cProfile.Profile()
    profiler.enable()

    fields, constraints_list = create_test_data()

    all_sessions = []
    session_index = 0
    for c in constraints_list:
        for _ in range(c.sessions):
            all_sessions.append((session_index, c.team_id, int(c.required_size), c.length))
            session_index += 1

    num_sessions = len(all_sessions)
    day_to_idx = {'Mon':0,'Tue':1,'Wed':2,'Thu':3,'Fri':4,'Sat':5,'Sun':6}
    idx_to_day = {v:k for k,v in day_to_idx.items()}

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

    model = cp_model.CpModel()
    max_time_blocks = 24 * 4
    day_var = [model.NewIntVar(0, 6, f'day_s{s}') for s in range(num_sessions)]
    field_ids = [f.field_id for f in fields]
    field_var = [model.NewIntVarFromDomain(cp_model.Domain.FromValues(field_ids), f'field_s{s}') for s in range(num_sessions)]
    start_var = [model.NewIntVar(0, max_time_blocks, f'start_s{s}') for s in range(num_sessions)]

    session_intervals = {}  # (s, f, d) -> intervalVar
    presence_var = {}       # (s, f, d) -> BoolVar controlling presence
    demands_capacity = {}
    demands_splits = {}

    for s, (sid, team_id, req_capacity, length_15) in enumerate(all_sessions):
        duration = length_15
        for f in fields:
            f_id = f.field_id
            fi = field_info[f_id]
            for d in range(7):
                if (d in fi['day_windows']) and (req_capacity in fi['allowed_demands']):
                    (window_start, window_end) = fi['day_windows'][d]
                    pres = model.NewBoolVar(f'pres_s{s}_f{f_id}_d{d}')
                    presence_var[(s, f_id, d)] = pres

                    interval = model.NewOptionalIntervalVar(
                        start_var[s], duration,
                        model.NewIntVar(0, max_time_blocks, ''), 
                        pres,
                        f'interval_s{s}_f{f_id}_d{d}'
                    )

                    session_intervals[(s, f_id, d)] = interval
                    demands_capacity[(s, f_id, d)] = req_capacity
                    demands_splits[(s, f_id, d)] = 1

                    model.Add(day_var[s] == d).OnlyEnforceIf(pres)
                    model.Add(field_var[s] == f_id).OnlyEnforceIf(pres)
                    model.Add(start_var[s] >= window_start).OnlyEnforceIf(pres)
                    model.Add(start_var[s] <= window_end - duration).OnlyEnforceIf(pres)

                    b_not_day = model.NewBoolVar(f'not_day_s{s}_d{d}')
                    b_not_field = model.NewBoolVar(f'not_field_s{s}_f{f_id}')
                    model.Add(day_var[s] != d).OnlyEnforceIf(b_not_day)
                    model.Add(field_var[s] != f_id).OnlyEnforceIf(b_not_field)
                    model.AddImplication(b_not_day, pres.Not())
                    model.AddImplication(b_not_field, pres.Not())

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

    team_sessions = defaultdict(list)
    for s, (sid, team_id, req_capacity, length_15) in enumerate(all_sessions):
        team_sessions[team_id].append(s)

    for team_id, sess_list in team_sessions.items():
        for d in range(7):
            bools_for_that_day = []
            for s in sess_list:
                for f_id in field_ids:
                    if (s, f_id, d) in presence_var:
                        bools_for_that_day.append(presence_var[(s, f_id, d)])
            if bools_for_that_day:
                model.Add(sum(bools_for_that_day) <= 1)

    for s in range(num_sessions):
        feasible_bools = []
        for f_id in field_ids:
            for d in range(7):
                if (s, f_id, d) in presence_var:
                    feasible_bools.append(presence_var[(s, f_id, d)])
        # Always require the session to be assigned exactly once.
        # If feasible_bools is empty, this forces the model to be infeasible, which is correct.
        model.Add(sum(feasible_bools) == 1)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("Found a feasible solution!")
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats(10)
        solution = []
        for s, (sid, team_id, req_capacity, length_15) in enumerate(all_sessions):
            assigned_day = solver.Value(day_var[s])
            assigned_field = solver.Value(field_var[s])
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
                "day_of_week": idx_to_day[assigned_day],
                "start_time": start_str,
                "end_time": end_str,
                "field_id": assigned_field,
                "required_size": req_capacity
            })
        
        # Post-process the solution to assign specific subfields
        solution = post_process_solution(solution, fields)
        
        # Save the schedule to database
        schedule_id = save_schedule(solution, club_id=5, facility_id=4, name="generated 2")
        print(f"Schedule saved successfully with ID: {schedule_id}")
        
        for sess in solution:
            print(sess)
        return solution
    else:
        print("No feasible solution found.")
        return None

if __name__ == "__main__":
    solve_field_schedule()
