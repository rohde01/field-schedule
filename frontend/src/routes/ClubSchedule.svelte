<script lang="ts">
  import { browser } from '$app/environment';
  import type { Field } from '$lib/schemas/field';
  import type { ProcessedScheduleEntry } from '$lib/utils/calendarUtils';
  import { fields } from '$lib/stores/fields';
  import { teams } from '$lib/stores/teams';
  import { derived } from 'svelte/store';
  import { onMount } from 'svelte';
  import { buildResources, timeSlots, 
          getRowForTimeWithSlots, getEntryRowEndWithSlots,
          getEntryContentVisibility, 
          processedEntries, showEarlyTimeslots } from '$lib/utils/calendarUtils';
  import { currentDate, formatDate, formatWeekdayOnly,
          nextDay, previousDay, currentTime, updateCurrentTime,
          getCurrentTimePosition, formatTimeForDisplay,
          shouldHideHourLabel, isHourMark, timeTrackingEnabled } from '$lib/utils/dateUtils';
  import { getFieldColumns, buildFieldToGridColumnMap, generateHeaderCells, getFieldName } from '$lib/utils/fieldUtils';
  import { selectedSchedule, schedules } from '$lib/stores/schedules';
  import { Heading, Button, Toggle, Tooltip, Input, DarkMode } from 'flowbite-svelte';
  import { AngleLeftOutline, AngleRightOutline } from 'flowbite-svelte-icons';
  import { page } from '$app/stores';

  // Function to find the active schedule for a given date
  function findActiveScheduleForDate(date: Date): number | null {
    const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD format
    
    for (const schedule of $schedules) {
      const activeFrom = schedule.active_from;
      const activeUntil = schedule.active_until;
      
      // Skip schedules without BOTH active_from AND active_until defined
      if (!activeFrom || !activeUntil) {
        continue;
      }
      
      // Check if current date is within the active range
      if (dateStr >= activeFrom && dateStr <= activeUntil) {
        return schedule.schedule_id!;
      }
    }
    
    return null;
  }

  // Update selected schedule when current date changes
  $: if (browser && $schedules.length > 0) {
    const activeScheduleId = findActiveScheduleForDate($currentDate);
    if (activeScheduleId && activeScheduleId !== $selectedSchedule?.schedule_id) {
      const activeSchedule = $schedules.find(s => s.schedule_id === activeScheduleId);
      if (activeSchedule) {
        selectedSchedule.set(activeSchedule);
      }
    } else if (!activeScheduleId) {
      // Clear selected schedule if no active schedule found
      selectedSchedule.set(null);
    }
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

  const activeFields = browser ? derived([fields, selectedSchedule], ([$fields, $selectedSchedule]) => {
    return buildResources($fields, $selectedSchedule);
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

  const logoUrl = derived(page, $page => $page.data.club?.logo_url || '/favicon.png');

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

  // Function to check if time should be hidden when early timeslots are off
  function shouldHideFirstHourMarkWhenEarlyOff(time: string, earlyTimeslotsOn: boolean): boolean {
    return time === '12:00' && !earlyTimeslotsOn;
  }

  let teamSearchTerm = "";
  $: filteredEntries = teamSearchTerm
    ? $processedEntries.filter(entry =>
        $teamNameLookup.get(entry.team_id)?.toLowerCase().includes(teamSearchTerm.toLowerCase())
      )
    : $processedEntries;

  // Navigate to root domain without subdomain
  function navigateHome() {
    if (!browser) return;
    const { protocol, hostname, port } = window.location;
    const portSegment = port ? `:${port}` : '';
    let mainDomain;
    if (hostname === 'localhost') {
      mainDomain = `localhost${portSegment}`;
    } else if (hostname === 'baneplanen.info' || hostname === 'www.baneplanen.info') {
      mainDomain = 'baneplanen.info';
    } else if (hostname.endsWith('.baneplanen.info')) {
      mainDomain = 'baneplanen.info';
    } else {
      mainDomain = hostname.replace(/^[^.]+\./, '');
    }
    window.location.href = `${protocol}//${mainDomain}${portSegment}/`;
  }
</script>


<!-- make container focusable and keyboard-operable -->
<div id="main-content" class="relative mx-auto h-full w-full overflow-y-auto bg-gray-50 dark:bg-gray-900 px-4 py-4">
  <div class="schedule-container">
    {#if $selectedSchedule}
      <div class="flex items-center justify-between mb-4">
        <a href="/" on:click|preventDefault={navigateHome}>
          <img src={$logoUrl} class="h-26 mb-3" alt="Club logo" />
        </a>
        <DarkMode class="text-primary-500 dark:text-primary-600 border dark:border-gray-800" />
      </div>
      <div class="mb-4">
        <Heading tag="h1">{$selectedSchedule.name}</Heading>
      </div>
    {/if}
    <div class="schedule-controls flex items-center my-2 py-2">
      <div class="current-date flex-1">
        <Heading tag="h2">
          {formatDate($currentDate)}
        </Heading>
        <Heading tag="h3" class="mt-1 text-gray-600">
          {formatWeekdayOnly($currentDate)}
        </Heading>
      </div>

      <div class="navigation-controls flex-1 flex items-center gap-8 justify-end">
        <div class="team-filter flex items-center ms-4">
          <Input size="md" bind:value={teamSearchTerm} placeholder="Find dit hold" />
        </div>
        <div class="toggle-container">
          <Toggle bind:checked={$showEarlyTimeslots}></Toggle>
          <Tooltip placement="top">Vis hele dagen</Tooltip>
        </div>
        <div class="day-nav flex items-center gap-2">
          <Button outline={true} class="p-2!" on:click={previousDay}>
            <AngleLeftOutline class="w-5 h-5" />
          </Button>
          <Button outline={true} class="p-2!" on:click={nextDay}>
            <AngleRightOutline class="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Display message when no schedule is active -->
    {#if !$selectedSchedule}
      <div class="no-schedule-message bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 text-center my-4">
        <p class="text-gray-600 dark:text-gray-400 text-lg">No active schedule on this day</p>
      </div>
    {:else}
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
            {#if isHourMark(time) && !shouldHideHourLabel(time) && !shouldHideFirstHourMarkWhenEarlyOff(time, $showEarlyTimeslots)}
              <span style="position:absolute; bottom:50%; right:5;">{time}</span>
            {/if}
          </div>

          {#each headerCells as cell}
            <div
              class={`schedule-cell ${isHourMark(time) && !shouldHideFirstHourMarkWhenEarlyOff(time, $showEarlyTimeslots) ? 'schedule-hour-mark' : ''} ${cell.colIndex > 1 && cell.colIndex < totalColumns ? 'border-grid' : ''}`}
              style="grid-column: {cell.colIndex} / span {cell.colSpan}; grid-row: {rowIndex + 2};"
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
        {#each filteredEntries as entry (entry.ui_id)}
          {#if entry.field_id != null && fieldToGridColMap.has(entry.field_id)}
            {@const mapping = fieldToGridColMap.get(entry.field_id)!}
            {@const startRow = getRowForTimeWithSlots(entry.start_time, $timeSlots)}
            {@const endRow = getEntryRowEndWithSlots(entry.end_time, $timeSlots)}
            {@const visibility = getEntryContentVisibility(startRow, endRow)}
            <div class="schedule-event"
               style="grid-row-start: {startRow}; grid-row-end: {endRow + 1}; grid-column-start: {mapping.colIndex}; grid-column-end: span {mapping.colSpan};"
             >
              <div class="event-team font-bold text-[1.15em]">
                {getEntryTitle(entry)}
              </div>
              {#if visibility.showField}
                <div class="event-field text-[1.12em] text-gray-600">
                  {getFieldName(entry.field_id!, $activeFields)}
                </div>
              {/if}
              {#if visibility.showTime}
                <div class="event-time text-[1.12em] text-gray-600">
                  {entry.start_time} - {entry.end_time}
                </div>
              {/if}
            </div>
          {/if}
        {/each}
      </div>
    </div>
    {/if}
  </div>
</div>

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
    container-type: inline-size;
    container-name: entry;
    background-color: var(--color-primary-200);
    color: var(--color-primary-700);
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
  }

  .event-team {
    /* graphite title for both light and dark mode */
    color: #444;
  }

  @container entry (max-width: 120px) {
    .event-time {
      display: none;
    }
  }

  @container entry (max-width: 80px) {
    .event-field {
      display: none;
    }
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

</style>