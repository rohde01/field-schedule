<script lang="ts">
  import { browser } from '$app/environment';
  import { dropdownState } from '../../stores/ScheduleDropdownState';
  import type { Field } from '$lib/schemas/field';
  import type { ProcessedScheduleEntry } from '$lib/utils/calendarUtils';
  import { fields } from '$stores/fields';
  import { teams } from '$stores/teams';
  import { derived } from 'svelte/store';
  import { buildResources, timeSlots,
          nextDay, previousDay, getRowForTimeWithSlots, getEntryRowEndWithSlots,
          getEntryContentVisibility,
          currentDate, formatDate, shouldShowEntryOnDate, processedEntries } from '$lib/utils/calendarUtils';
  import { getFieldColumns, buildFieldToGridColumnMap, generateHeaderCells, getFieldName } from '$lib/utils/fieldUtils';

  const activeFields = browser ? derived([fields, dropdownState], ([$fields, $dropdownState]) => {
    return buildResources($fields, $dropdownState.selectedSchedule);
  }) : derived(fields, () => []);

  $: headerCells = $activeFields.length > 0 
    ? generateHeaderCells($activeFields, fieldToGridColMap)
    : [];

  $: totalColumns = Math.max(2, 1 + $activeFields.reduce((acc: number, f: Field) => acc + getFieldColumns(f), 0));
  
  $: fieldToGridColMap = buildFieldToGridColumnMap($activeFields);
  
  const teamNameLookup = browser ? derived(teams, ($teams) => {
    const lookup = new Map<number, string>();
    for (const team of $teams) {
      lookup.set(team.team_id!, team.name);
    }
    return lookup;
  }) : derived(teams, () => new Map());

  // Function to get the best title for an entry, prioritizing summary
  function getEntryTitle(entry: ProcessedScheduleEntry): string {
    if (entry.summary) {
      return entry.summary;
    }
    if (entry.team_id != null) {
      return $teamNameLookup.get(entry.team_id) ?? `Team ${entry.team_id}`;
    }
    return "Untitled Event";
  }
</script>

<div class="schedule-container">
  <div class="schedule-controls flex justify-between items-center my-2 py-2">
    <div class="weekday-navigation flex items-center gap-2">
      <button on:click={previousDay} class="nav-button">‹</button>
      <span class="current-day text-lg font-medium text-sage-800">
        {formatDate($currentDate)}
      </span>
      <button on:click={nextDay} class="nav-button">›</button>
    </div>
  </div>

  <div 
    class="schedule-grid"
    style="--total-columns: {totalColumns}; --total-rows: {$timeSlots.length + 1};"
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
    {#each $timeSlots as time, rowIndex}
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

    <!-- ENTRIES -->
    {#each $processedEntries.filter(entry => shouldShowEntryOnDate(entry, $currentDate)) as entry (entry.schedule_entry_id)}
      {#if entry.field_id != null && fieldToGridColMap.has(entry.field_id)}
        {@const mapping = fieldToGridColMap.get(entry.field_id)!}
        {@const startRow = getRowForTimeWithSlots(entry.start_time, $timeSlots)}
        {@const endRow = getEntryRowEndWithSlots(entry.end_time, $timeSlots)}
        {@const visibility = getEntryContentVisibility(startRow, endRow)}
        <div
          class="schedule-event"
          style="
            grid-row-start: {startRow};
            grid-row-end: {endRow + 1};
            grid-column-start: {mapping.colIndex};
            grid-column-end: span {mapping.colSpan};
          "
        >
          <div class="event-team font-bold text-[1.15em]">
            {getEntryTitle(entry)}
          </div>
          {#if visibility.showField}
            <div class="event-field flex items-center gap-1 text-[1.12em] text-gray-600">
              📍 {getFieldName(entry.field_id!, $activeFields)}
            </div>
          {/if}
          {#if visibility.showTime}
            <div class="event-time flex items-center gap-1 text-[1.12em] text-gray-600">
              🕐 {entry.start_time} - {entry.end_time}
            </div>
          {/if}
        </div>
      {/if}
    {/each}
  </div>
</div>