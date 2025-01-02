<script lang="ts">
    import { dropdownState } from '../../stores/ScheduleDropdownState';
    import type { Field } from '$lib/schemas/field';
    import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';
    import { fields } from '$stores/fields';
    import { teams } from '$stores/teams';
    import { derived } from 'svelte/store';

    function buildResources(allFields: Field[], selectedSchedule: Schedule | null): Field[] {
        if (!selectedSchedule) return [];
        return allFields.filter(field => field.facility_id === selectedSchedule.facility_id);
    }

    // Create a derived store for active fields based on selected schedule
    const activeFields = derived([fields, dropdownState], ([$fields, $dropdownState]) => {
        const selectedSchedule = $dropdownState.selectedSchedule;
        return buildResources($fields, selectedSchedule);
    });

    function generateTimeSlots(
      start: string,
      end: string,
      intervalMinutes: number
    ): string[] {
      const slots: string[] = [];
      let [startH, startM] = start.split(":").map(Number);
      const [endH, endM] = end.split(":").map(Number);

      let currentMinutes = startH * 60 + startM;
      const endTotalMinutes = endH * 60 + endM;

      while (currentMinutes <= endTotalMinutes) {
        const hh = Math.floor(currentMinutes / 60).toString().padStart(2, "0");
        const mm = (currentMinutes % 60).toString().padStart(2, "0");
        slots.push(`${hh}:${mm}`);
        currentMinutes += intervalMinutes;
      }

      return slots;
    }

    function getQuarterFieldsForHalf(field: Field, halfFieldId: number) {
      return field.quarter_subfields.filter(
        (q) => q.parent_field_id === halfFieldId
      );
    }

    function getFieldColumns(field: Field): number {
      if (!field.half_subfields.length) {
        return 1;
      }
      return field.half_subfields.reduce((acc, half) => {
        const quarterCount = getQuarterFieldsForHalf(field, half.field_id).length;
        return acc + (quarterCount || 1);
      }, 0);
    }

    function buildFieldToGridColumnMap(fields: Field[]) {
      const map = new Map<number, { colIndex: number; colSpan: number }>();
      let currentColIndex = 2;  // col 1 is reserved for Time

      for (const field of fields) {
        const totalColumnsForField = getFieldColumns(field);
        map.set(field.field_id, {
          colIndex: currentColIndex,
          colSpan: totalColumnsForField
        });

        if (!field.half_subfields.length) {
          currentColIndex += 1;
        } else {
          for (const half of field.half_subfields) {
            const quarterFields = getQuarterFieldsForHalf(field, half.field_id);

            // Add mapping for the half field itself
            map.set(half.field_id, {
              colIndex: currentColIndex,
              colSpan: quarterFields.length || 1
            });

            if (quarterFields.length === 0) {
              currentColIndex += 1;
            } else {
              for (const q of quarterFields) {
                map.set(q.field_id, {
                  colIndex: currentColIndex,
                  colSpan: 1
                });
                currentColIndex += 1;
              }
            }
          }
        }
      }

      return map;
    }

    // Grid layout setup
    const timeslots: string[] = generateTimeSlots("16:00", "20:30", 15);
    const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    let currentWeekDay = 0;

    function nextDay() {
        currentWeekDay = (currentWeekDay + 1) % 7;
    }

    function previousDay() {
        currentWeekDay = (currentWeekDay - 1 + 7) % 7;
    }

    interface HeaderCell {
      label: string;
      colIndex: number;
      colSpan: number;
    }
    let headerCells: HeaderCell[] = [];

    $: {
      headerCells = [];
      let colIndex = 2;  // col 1 is "Time"

      for (const field of $activeFields) {
        if (!field.half_subfields.length) {
          headerCells.push({
            label: field.name,
            colIndex,
            colSpan: 1
          });
          colIndex += 1;
        } else {
          for (const half of field.half_subfields) {
            const quarterFields = getQuarterFieldsForHalf(field, half.field_id);
            if (quarterFields.length === 0) {
              headerCells.push({
                label: half.name,
                colIndex,
                colSpan: 1
              });
              colIndex += 1;
            } else {
              for (const q of quarterFields) {
                headerCells.push({
                  label: q.name,
                  colIndex,
                  colSpan: 1
                });
                colIndex += 1;
              }
            }
          }
        }
      }
    }

    // Total columns = 1 (Time label) + sum of all field columns
    $: totalColumns = 1 + $activeFields.reduce((acc: number, f: Field) => acc + getFieldColumns(f), 0);

    $: fieldToGridColMap = buildFieldToGridColumnMap($activeFields);

    function normalizeTime(time: string): string {
      return time.slice(0, 5); // keep "HH:MM" only
    }

    function rowForTime(time: string): number {
      return timeslots.indexOf(normalizeTime(time)) + 2;  // +2 for header row offset
    }

    const activeEvents = derived(dropdownState, ($dropdownState): ScheduleEntry[] => {
      const selectedSchedule = $dropdownState.selectedSchedule;
      if (!selectedSchedule) return [];
      return selectedSchedule.entries;
    });

    // Create a lookup for team names
    const teamNameLookup = derived(teams, ($teams) => {
        const lookup = new Map<number, string>();
        for (const team of $teams) {
            lookup.set(team.team_id!, team.name);
        }
        return lookup;
    });

    // Field name lookup function
    function getFieldName(fieldId: number): string {
        const field = $activeFields.find(f => f.field_id === fieldId);
        if (field) return field.name;
        
        for (const mainField of $activeFields) {
            const half = mainField.half_subfields.find(h => h.field_id === fieldId);
            if (half) return half.name;
            
            const quarter = mainField.quarter_subfields.find(q => q.field_id === fieldId);
            if (quarter) return quarter.name;
        }
        return `Field ${fieldId}`;
    }

    $: filteredEvents = $activeEvents.filter((event: ScheduleEntry) => event.week_day === currentWeekDay);
</script>

<div class="schedule-container">
    <div class="weekday-navigation">
        <button on:click={previousDay} class="nav-button">‹</button>
        <span class="current-day">{weekDays[currentWeekDay]}</span>
        <button on:click={nextDay} class="nav-button">›</button>
    </div>

    <div 
        class="schedule-grid"
        style="--total-columns: {totalColumns}; --total-rows: {timeslots.length + 1};"
    >
        <!-- HEADER ROW -->
        <div class="schedule-header schedule-header-time">
            Time
        </div>

        {#each headerCells as cell}
            <div
                class="schedule-header"
                style="grid-column: {cell.colIndex} / span {cell.colSpan}; grid-row: 1;"
            >
                {cell.label}
            </div>
        {/each}

        <!-- TIMESLOT ROWS -->
        {#each timeslots as time, rowIndex}
            <div
                class="schedule-time"
                style="grid-column: 1; grid-row: {rowIndex + 2};"
            >
                {time}
            </div>

            {#each headerCells as cell}
                <div
                    class="schedule-cell"
                    style="grid-column: {cell.colIndex} / span {cell.colSpan}; grid-row: {rowIndex + 2};"
                ></div>
            {/each}
        {/each}

        <!-- EVENTS -->
        {#each filteredEvents as event}
            {#if fieldToGridColMap.has(event.field_id!) && event.team_id !== null}
                {@const mapping = fieldToGridColMap.get(event.field_id!)!}
                <div
                    class="schedule-event"
                    style="
                        grid-row-start: {rowForTime(event.start_time)};
                        grid-row-end: {rowForTime(event.end_time) + 1};
                        grid-column-start: {mapping.colIndex};
                        grid-column-end: span {mapping.colSpan};
                    "
                >
                    <div class="event-team">
                        {$teamNameLookup.get(event.team_id) ?? `Team ${event.team_id}`}
                    </div>
                    <div class="event-field">
                        📍 {getFieldName(event.field_id!)}
                    </div>
                    <div class="event-time">
                        🕐 {normalizeTime(event.start_time)} - {normalizeTime(event.end_time)}
                    </div>
                </div>
            {/if}
        {/each}
    </div>
</div>
