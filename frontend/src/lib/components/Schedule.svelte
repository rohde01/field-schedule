<script lang="ts">
  import { browser } from '$app/environment';
  import { dropdownState } from '../stores/ScheduleDropdownState';
  import type { Field } from '$lib/schemas/field';
  import type { ProcessedScheduleEntry } from '$lib/utils/calendarUtils';
  import { fields } from '$lib/stores/fields';
  import { teams } from '$lib/stores/teams';
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
  import InfoCard from '$lib/components/InfoCard.svelte';
  import { resizeHandle, horizontalDrag, moveHandle } from '$lib/utils/dndUtils';
  import { addScheduleEntry } from '$lib/stores/schedules';
  import { get } from 'svelte/store';
  import { Heading, Button } from 'flowbite-svelte';
  import { AngleLeftOutline, AngleRightOutline } from 'flowbite-svelte-icons';
  

  // InfoCard state
  let showInfoCard = false;
  let selectedEntryUiId = "";
  let recentDrag = false;

  // Handle single click on entry
  function handleEntryInteraction(event: MouseEvent|KeyboardEvent, entry: ProcessedScheduleEntry) {
    if (recentDrag) { recentDrag = false; return; }
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

  // Check if the current schedule is a draft
  $: isDraft = isDraftSchedule($dropdownState.selectedSchedule);

  // create new entry on double-click
  function handleSlotDoubleClick(event: MouseEvent, cell: any, time: string) {
    event.stopPropagation();
    const startDateTime = combineDateAndTime(get(currentDate), time);
    addScheduleEntry({
      schedule_entry_id: null,
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

<style>
  .schedule-cell {
    background: transparent;
    padding: 0.5rem 1rem;
    position: relative;
    height: 1.5rem;
    border-bottom: 0;
  }
  
  .schedule-hour-mark {
    border-top: 1px solid #e5e5e5;
  }
  
  .schedule-grid {
    width: 100%;
    border-radius: 0.5rem;
    overflow: hidden;
    position: relative;
    display: grid !important;
    grid-template-columns: 50px repeat(auto-fit, minmax(0, 1fr)) !important;
    grid-template-rows: auto repeat(var(--total-rows) - 1, minmax(2.5rem, auto));
  }

  .border-grid {
    border-right: 1px solid #e5e5e5;
  }

  .schedule-time {
    position: relative;
  }
  
  .schedule-event {
    background-color: #edfcf5;
    color: #065f46;
    padding: 0.375rem;
    border-radius: 0.125rem;
    font-size: 0.875rem;
    font-weight: 500;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    position: absolute;
    inset: 0;
    margin: 2px;
    transition:
      transform 0.15s ease-out,
      box-shadow 0.15s ease-out,
      border-left 0.15s ease-out;
  }

  
  .current-time-indicator {
    position: absolute;
    display: flex;
    align-items: center;
    z-index: 100;
    pointer-events: none;
    width: 100%;
    left: 0;
  }

  .current-time-bubble {
    background-color: #ff3b30;
    color: white;
    font-size: 14px;
    font-weight: 500;
    border-radius: 6px;
    padding: 2px 6px;
    line-height: 1.2;
    margin-left: 0;
    min-width: 50px;
    text-align: center;
  }

  .current-time-line {
    flex: 1;
    height: 2.5px;
    background-color: #ff3b30;
  }

  .resize-handle {
    position: absolute;
    left: 0;
    right: 0;
    height: 6px;
    background: transparent;
    z-index: 2;
  }
  .resize-handle.top {
    top: 0;
  }
  .resize-handle.bottom {
    bottom: 0;
  }
  .horizontal-handle {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 6px;
    background: transparent;
    z-index: 2;
    cursor: ew-resize;
  }
  .horizontal-handle.left {
    left: 0;
  }
  .horizontal-handle.right {
    right: 0;
  }

</style>

<!-- make container focusable and keyboard-operable -->
<div class="schedule-container" role="button" tabindex="0" on:click|self={closeInfoCard} on:keydown|self={(e) => (e.key === 'Enter' || e.key === ' ') && (closeInfoCard(), e.preventDefault())}>
  <div class="schedule-controls flex items-center my-2 py-2">
    <div class="current-date flex-1">
      <Heading tag="h2">
        {formatDate($currentDate)}
      </Heading>
      <Heading tag="h3" class="mt-1 text-gray-600">
        {formatWeekdayOnly($currentDate)}
      </Heading>
    </div>

    <div class="navigation-controls flex-1 flex items-center gap-2 justify-end">
      <Button outline={true} class="p-2!" on:click={previousDay}>
        <AngleLeftOutline class="w-5 h-5" />
      </Button>
      <Button outline={true} class="p-2!" on:click={nextDay}>
        <AngleRightOutline class="w-5 h-5" />
      </Button>
    </div>
  </div>

  <!-- HEADER ROW OUTSIDE SCROLLABLE CONTAINER -->
  <div class="schedule-grid bg-gray-100 dark:bg-gray-700">
    <div 
      class="p-4 font-medium text-gray-900 dark:text-white"
      style="grid-column: 1;"
    >
    </div>
    {#each headerCells as cell}
      <div
        class="p-4 font-medium text-gray-900 dark:text-white text-center"
        style="grid-column: {cell.colIndex} / span {cell.colSpan}; border-right: none;"
      >
        {cell.label}
      </div>
    {/each}
  </div>
  <div class="daily-schedule-wrapper" style="margin-top: 7px;">
    <div 
      class="schedule-grid"
      style="--total-columns: {totalColumns}; --total-rows: {$timeSlots.length + 1};">
      <!-- TIMESLOT ROWS -->
      {#each $timeSlots as time, rowIndex}
        <div
          class="schedule-time text-gray-900 dark:text-white"
          style="grid-column: 1; grid-row: {rowIndex + 2}; justify-content: flex-end;"
        >
          {#if isHourMark(time) && !shouldHideHourLabel(time)}
            <span style="position:absolute; bottom:50%; right:5;">{time}</span>
          {/if}
        </div>

        {#each headerCells as cell}
          <div
            class={`schedule-cell ${isHourMark(time) ? 'schedule-hour-mark' : ''} ${cell.colIndex > 1 && cell.colIndex < totalColumns ? 'border-grid' : ''}`}
            role="button"
            tabindex="0"
            style="grid-column: {cell.colIndex} / span {cell.colSpan}; grid-row: {rowIndex + 2};"
            on:dblclick={(e) => handleSlotDoubleClick(e, cell, time)}
          ></div>
        {/each}
      {/each}

      <!-- CURRENT TIME INDICATOR -->
      {#if timeTrackingEnabled}
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
          <div use:moveHandle={{ ui_id: entry.ui_id, totalColumns, activeFields: $activeFields, fieldToGridColMap }}
             on:dragend={(e) => recentDrag = !!e.detail}
             class="schedule-event"
             role="button"
             tabindex="0"
             style="grid-row-start: {startRow}; grid-row-end: {endRow + 1}; grid-column-start: {mapping.colIndex}; grid-column-end: span {mapping.colSpan};
             position: relative;"
             on:click={(e) => handleEntryInteraction(e, entry)}
             on:keydown={(e) => handleEntryInteraction(e, entry)}
           >
            <div class="resize-handle top" use:resizeHandle={{ ui_id: entry.ui_id, edge: 'top' }}></div>
            <div class="resize-handle bottom" use:resizeHandle={{ ui_id: entry.ui_id, edge: 'bottom' }}></div>
            <div class="horizontal-handle left" use:horizontalDrag={{ ui_id: entry.ui_id, direction: 'left', totalColumns, headerCells, activeFields: $activeFields, fieldToGridColMap }}></div>
            <div class="horizontal-handle right" use:horizontalDrag={{ ui_id: entry.ui_id, direction: 'right', totalColumns, headerCells, activeFields: $activeFields, fieldToGridColMap }}></div>
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
</div>
