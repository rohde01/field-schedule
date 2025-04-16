<script lang="ts">
  import { browser } from '$app/environment';
  import { dropdownState } from '../../stores/ScheduleDropdownState';
  import type { Field } from '$lib/schemas/field';
  import type { ProcessedScheduleEntry } from '$lib/utils/calendarUtils';
  import { fields } from '$stores/fields';
  import { teams } from '$stores/teams';
  import { derived } from 'svelte/store';
  import { buildResources, timeSlots, 
          getRowForTimeWithSlots, getEntryRowEndWithSlots,
          getEntryContentVisibility, isDraftSchedule, 
          processedEntries } from '$lib/utils/calendarUtils';
  import { currentDate, formatDate, formatWeekdayOnly,
          nextDay, previousDay } from '$lib/utils/dateUtils';
  import { getFieldColumns, buildFieldToGridColumnMap, generateHeaderCells, getFieldName } from '$lib/utils/fieldUtils';
  import { writable } from 'svelte/store';
  import Calendar from '$lib/components/Calendar.svelte';

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

  const viewMode = writable('day');
  
  // Month view title
  const currentMonthDate = writable(new Date());
  
  $: monthViewTitle = $currentMonthDate.toLocaleDateString('en-US', { 
    month: 'long', 
    year: 'numeric' 
  });
  
  // Reference to the Calendar component for navigation
  let calendarComponent: Calendar;
  
  // Update navigation functions for week/month view
  function previousPeriod() {
    if ($viewMode === 'day') {
      previousDay();
    } else {
      calendarComponent?.navigatePrev();
      const newDate = new Date($currentMonthDate);
      newDate.setMonth(newDate.getMonth() - 1);
      $currentMonthDate = newDate;
    }
  }
  
  function nextPeriod() {
    if ($viewMode === 'day') {
      nextDay();
    } else {
      calendarComponent?.navigateNext();
      const newDate = new Date($currentMonthDate);
      newDate.setMonth(newDate.getMonth() + 1);
      $currentMonthDate = newDate;
    }
  }
  
  // Reset to current month when switching to month view
  $: if ($viewMode === 'week') {
    $currentMonthDate = new Date();
  }

  // Check if the current schedule is a draft
  $: isDraft = isDraftSchedule($dropdownState.selectedSchedule);

  // Function to check if a time slot is an hour mark (00 minutes) and should be displayed
  function isHourMark(time: string): boolean {
    return time.endsWith(':00') && time !== '00:00' && time !== '24:00';
  }
</script>

<div class="schedule-container">
  <div class="schedule-controls flex items-center my-2 py-2">
    <div class="current-date flex-1">
      <span class="text-xl font-semibold text-black">
        {#if $viewMode === 'day'}
          {isDraft ? formatWeekdayOnly($currentDate) : formatDate($currentDate)}
        {:else}
          {monthViewTitle}
        {/if}
      </span>
    </div>

    <div class="view-toggle-container flex-shrink-0">
      <div class="view-toggle">
        <button
          class="view-toggle-btn { $viewMode === 'day' ? 'active' : '' }"
          on:click={() => $viewMode = 'day'}
        >
          Day
        </button>
        <button
          class="view-toggle-btn { $viewMode === 'week' ? 'active' : '' }"
          on:click={() => $viewMode = 'week'}
        >
          Month
        </button>
      </div>
    </div>

    <div class="navigation-controls flex-1 flex items-center gap-2 justify-end">
      <button on:click={previousPeriod} class="nav-button">‹</button>
      <button on:click={nextPeriod} class="nav-button">›</button>
    </div>
  </div>

  {#if $viewMode === 'day'}
    <!-- HEADER ROW OUTSIDE SCROLLABLE CONTAINER -->
    <div class="schedule-grid" style="--total-columns: {totalColumns};">
      <div class="schedule-header schedule-header-time">
      </div>
      {#each headerCells as cell}
        <div
          class="schedule-header"
          style="grid-column: {cell.colIndex} / span {cell.colSpan};"
        >
          {cell.label}
        </div>
      {/each}
    </div>
    <div class="daily-schedule-wrapper" 
         style="height: calc(80vh); overflow-y: auto; overscroll-behavior: contain;">
      <div 
        class="schedule-grid"
        style="--total-columns: {totalColumns}; --total-rows: {$timeSlots.length + 1};">
        <!-- TIMESLOT ROWS -->
        {#each $timeSlots as time, rowIndex}
          <div
            class="schedule-time"
            style="grid-column: 1; grid-row: {rowIndex + 2}; justify-content: flex-end;"
          >
            {#if isHourMark(time)}
              <span style="transform: translateY(-50%);">{time}</span>
            {/if}
          </div>

          {#each headerCells as cell}
            <div
              class={`schedule-cell ${isHourMark(time) ? 'schedule-hour-mark' : ''}`}
              style="grid-column: {cell.colIndex} / span {cell.colSpan}; grid-row: {rowIndex + 2};"
            ></div>
          {/each}
        {/each}

        <!-- ENTRIES -->
        {#each $processedEntries as entry (entry.schedule_entry_id)}
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
  {:else if $viewMode === 'week'}
    <div class="month-view">
      <Calendar bind:this={calendarComponent} />
    </div>
  {/if}
</div>
