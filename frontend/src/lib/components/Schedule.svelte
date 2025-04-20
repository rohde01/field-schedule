<script lang="ts">
  import { browser } from '$app/environment';
  import { dropdownState } from '../../stores/ScheduleDropdownState';
  import type { Field } from '$lib/schemas/field';
  import type { ProcessedScheduleEntry } from '$lib/utils/calendarUtils';
  import { fields } from '$stores/fields';
  import { teams } from '$stores/teams';
  import { derived } from 'svelte/store';
  import { onMount } from 'svelte';
  import { buildResources, timeSlots, 
          getRowForTimeWithSlots, getEntryRowEndWithSlots,
          getEntryContentVisibility, isDraftSchedule, 
          processedEntries } from '$lib/utils/calendarUtils';
  import { currentDate, formatDate, formatWeekdayOnly,
          nextDay, previousDay, currentTime, updateCurrentTime,
          getCurrentTimePosition, formatTimeForDisplay,
          shouldHideHourLabel, isHourMark, timeTrackingEnabled,
          combineDateAndTime } from '$lib/utils/dateUtils';
  import { getFieldColumns, buildFieldToGridColumnMap, generateHeaderCells, getFieldName } from '$lib/utils/fieldUtils';
  import { writable } from 'svelte/store';
  import Calendar from '$lib/components/Calendar.svelte';
  import InfoCard from '$lib/components/InfoCard.svelte';
  import { addScheduleEntry } from '$stores/schedules';
  import { get } from 'svelte/store';

  // InfoCard state
  let showInfoCard = false;
  let selectedEntryUiId = "";
  
  // Handle single click on entry
  function handleEntryInteraction(event: MouseEvent|KeyboardEvent, entry: ProcessedScheduleEntry) {
    // only respond to click or Enter/Space key
    if (event instanceof KeyboardEvent && !(event.key === 'Enter' || event.key === ' ')) return;
    showInfoCard = true;
    selectedEntryUiId = entry.ui_id;
    event.stopPropagation();
    
    // Add document click listener when InfoCard is shown
    setTimeout(() => {
      document.addEventListener('click', handleOutsideClick);
    }, 0);
  }

  function closeInfoCard() {
    showInfoCard = false;
    document.removeEventListener('click', handleOutsideClick);
  }
  
  // Handle clicks outside the InfoCard
  function handleOutsideClick(event: MouseEvent) {
    const infoCard = document.querySelector('.info-card-container');
    const active = document.activeElement as Node;
    if (
      infoCard && 
      (infoCard.contains(event.target as Node) || infoCard.contains(active))
    ) {
      return;
    }
    closeInfoCard();
  }

  // Time tracking variables
  let currentTimePosition = 0;
  let timeTrackingInterval: ReturnType<typeof setInterval>;

  // Initialize time tracking on component mount
  onMount(() => {
    updateCurrentTime();
    timeTrackingInterval = setInterval(() => {
      updateCurrentTime();
      currentTimePosition = getCurrentTimePosition();
    }, 60000); // Update every minute
    
    return () => {
      clearInterval(timeTrackingInterval);
    };
  });
  
  // Update time tracking when date changes
  $: {
    $currentDate;
    if (browser) {
      updateCurrentTime();
      currentTimePosition = getCurrentTimePosition();
    }
  }

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

  // create new entry on double-click
  function handleSlotDoubleClick(event: MouseEvent, cell: any, time: string) {
    event.stopPropagation();
    const startDateTime = combineDateAndTime(get(currentDate), time);
    addScheduleEntry({
      schedule_entry_id: -Date.now(),
      schedule_id: get(dropdownState).selectedSchedule!.schedule_id,
      uid: crypto.randomUUID(),
      dtstart: startDateTime,
      dtend: new Date(startDateTime.getTime() + 3600000),
      summary: 'new event',
      description: null,
      team_id: null,
      field_id: cell.fieldId,
      recurrence_rule: null,
      recurrence_id: null,
      exdate: null
    });
  }
</script>

<!-- make container focusable and keyboard-operable -->
<div class="schedule-container" role="button" tabindex="0" on:click|self={closeInfoCard} on:keydown|self={(e) => (e.key === 'Enter' || e.key === ' ') && (closeInfoCard(), e.preventDefault())}>
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

    <div class="view-toggle-container shrink-0">
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
            {#if isHourMark(time) && !shouldHideHourLabel(time)}
              <span style="transform: translateY(-50%);">{time}</span>
            {/if}
          </div>

          {#each headerCells as cell}
            <div
              class={`schedule-cell ${isHourMark(time) ? 'schedule-hour-mark' : ''}`}
              role="button"
              tabindex="0"
              style="grid-column: {cell.colIndex} / span {cell.colSpan}; grid-row: {rowIndex + 2};"
              on:dblclick={(e) => handleSlotDoubleClick(e, cell, time)}
            ></div>
          {/each}
        {/each}

        <!-- CURRENT TIME INDICATOR -->
        {#if timeTrackingEnabled && $viewMode === 'day'}
          <div 
            class="current-time-indicator" 
            style="grid-column: 1 / span {totalColumns}; top: calc({currentTimePosition}% - 1px);"
          >
            <div class="current-time-bubble">
              {formatTimeForDisplay($currentTime)}
            </div>
            <div class="current-time-line"></div>
          </div>
        {/if}

        <!-- ENTRIES -->
        {#each $processedEntries as entry (entry.ui_id)}
          {#if entry.field_id != null && fieldToGridColMap.has(entry.field_id)}
            {@const mapping = fieldToGridColMap.get(entry.field_id)!}
            {@const startRow = getRowForTimeWithSlots(entry.start_time, $timeSlots)}
            {@const endRow = getEntryRowEndWithSlots(entry.end_time, $timeSlots)}
            {@const visibility = getEntryContentVisibility(startRow, endRow)}
            <div
              class="schedule-event"
              role="button"
              tabindex="0"
              style="
                grid-row-start: {startRow};
                grid-row-end: {endRow + 1};
                grid-column-start: {mapping.colIndex};
                grid-column-end: span {mapping.colSpan};
              "
              on:click={(e) => handleEntryInteraction(e, entry)}
              on:keydown={(e) => handleEntryInteraction(e, entry)}
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
              {#if showInfoCard && selectedEntryUiId === entry.ui_id}
                <div class="info-card-container">
                  <InfoCard entryUiId={entry.ui_id} />
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
