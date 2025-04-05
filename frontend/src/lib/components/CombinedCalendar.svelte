<script lang="ts">
  import type { Field } from '$lib/schemas/field';
  import type { Event } from '$lib/schemas/event';
  import { fields } from '$stores/fields';
  import { teams } from '$stores/teams';
  import { derived, get, writable } from 'svelte/store';
  import { updateScheduleEntry, addScheduleEntry } from '$stores/schedules';
  import { buildResources, normalizeTime, handleGranularityChange, timeSlots, 
          getRowForTimeWithSlots, getEventRowEndWithSlots, addMinutes,
          includeActiveFields, handleIncludeActiveFieldsToggle, getEventContentVisibility } from '$lib/utils/calendarUtils';
  import { addDays, formatDateForDisplay, getDayOfWeek,
          findActiveScheduleForDate, getWeekDates, getWeekNumber, 
          getCurrentMonthDate, navigateMonth, 
          getFormattedMonth, formatDateYYYYMMDD } from '$lib/utils/dateUtils';
  import InfoCard from '$lib/components/InfoCard.svelte';
  import { detectOverlappingEvents, 
    calculateEventOffsets, getTotalOverlaps } from '$lib/utils/overlapUtils';
  import { getFieldColumns, buildFieldToGridColumnMap, generateHeaderCells, getFieldName, generateFieldOptions } from '$lib/utils/fieldUtils';
  import { initializeTopDrag, initializeBottomDrag, initializeEventDrag, initializeHorizontalDrag } from '$lib/utils/dndUtils';
  import { infoCardStore } from '$lib/utils/infoCardUtils';
  import { facilities } from '$stores/facilities';
  import { activeSchedules } from '$stores/activeSchedules';
  import { events, updateEventOverride, createEventOverride } from '$stores/events';
  import Calendar from '$lib/components/Calendar.svelte';
  
  let containerElement: HTMLElement;
  let calendarComponent: any; // Reference to the Calendar component
  
  const currentDate = writable(new Date());
  
  const viewMode = writable('day');
  
  // Derived store for current weekDay based on date - using getDayOfWeek for consistent indexing
  const currentWeekDay = derived(currentDate, $date => getDayOfWeek($date));
  
  function nextDay() {
    currentDate.update(date => addDays(date, 1));
  }
  
  function previousDay() {
    currentDate.update(date => addDays(date, -1));
  }
  
  function nextWeek() {
    currentDate.update(date => addDays(date, 7));
  }
  
  function previousWeek() {
    currentDate.update(date => addDays(date, -7));
  }

  // Store for the current month title
  const currentMonthTitle = writable('');
  
  // Update month title when navigating
  function updateMonthTitle() {
      if (calendarComponent) {
          const title = calendarComponent.getCurrentTitle();
          if (title) {
              currentMonthTitle.set(title);
          }
      }
  }
  
  const currentMonthDate = writable(getCurrentMonthDate());
  
  function previousMonth() {
      currentMonthDate.update(date => navigateMonth(date, 'prev'));
      if (calendarComponent) {
          calendarComponent.navigatePrev();
      }
  }
  
  function nextMonth() {
      currentMonthDate.update(date => navigateMonth(date, 'next'));
      if (calendarComponent) {
          calendarComponent.navigateNext();
      }
  }
  
  $: formattedMonth = getFormattedMonth($currentMonthDate);
  
  $: if ($viewMode === 'month' && calendarComponent) {
      setTimeout(updateMonthTitle, 100);
  }
  
  // Determine the active schedule using the activeSchedules store
  const currentActiveSchedule = derived(
    [currentDate, activeSchedules], 
    ([$currentDate, $activeSchedules]) => {
      return findActiveScheduleForDate($currentDate, $activeSchedules);
    }
  );
  
  // Get the event schedule for the active schedule from the new events store
  const currentEventSchedule = derived(
    [currentActiveSchedule, events],
    ([$currentActiveSchedule, $events]) => {
      if (!$currentActiveSchedule) return null;
      return $events.find(e => e.schedule_id === $currentActiveSchedule.schedule_id) ?? null;
    }
  );
  
  const weekDates = derived(
    [currentDate, activeSchedules],
    ([$currentDate, $activeSchedules]) => {
      return getWeekDates($currentDate, $activeSchedules);
    }
  );
  
  const selectedFacilityName = derived([facilities, currentEventSchedule], ([$facilities, $currentEventSchedule]) => {
    if (!$currentEventSchedule || !$currentEventSchedule.facility_id) {
      return "this facility";
    }
    
    const facility = $facilities.find(f => f.facility_id === $currentEventSchedule?.facility_id);
    return facility?.name || "this facility";
  });
  
  const activeFields = derived([fields, currentEventSchedule, includeActiveFields], ([$fields, $currentEventSchedule, $includeActiveFields]) => {
    return buildResources($fields, $currentEventSchedule, $includeActiveFields);
  });

  $: headerCells = $activeFields.length > 0 
    ? generateHeaderCells($activeFields, fieldToGridColMap)
    : [];

  $: totalColumns = Math.max(2, 1 + $activeFields.reduce((acc: number, f: Field) => acc + getFieldColumns(f), 0));
  
  $: fieldToGridColMap = buildFieldToGridColumnMap($activeFields);
  
  // Create a lookup for team names
  const teamNameLookup = derived(teams, ($teams) => {
    const lookup = new Map<number, string>();
    for (const team of $teams) {
      lookup.set(team.team_id!, team.name);
    }
    return lookup;
  });
  
  const formattedCurrentDate = derived(currentDate, $currentDate => formatDateYYYYMMDD($currentDate));
  
  // Filter events for rendering based on view mode and override properties.
  const filteredEvents = derived(
    [currentWeekDay, currentEventSchedule, viewMode, formattedCurrentDate],
    ([$currentWeekDay, $currentEventSchedule, $viewMode, $formattedCurrentDate]) => {
      if (!$currentEventSchedule || !$currentEventSchedule.entries) return [];
      
      // Create a map of schedule_entry_ids that have overrides for the current date
      const overriddenEntries = new Set(
        $currentEventSchedule.entries
          .filter(e => e.override_id && e.override_date === $formattedCurrentDate)
          .map(e => e.schedule_entry_id)
      );
      
      if ($viewMode === 'day') {
        return $currentEventSchedule.entries.filter(event => {
          if (event.override_id) {
            // Show override only if it matches the current date and isn't deleted
            return event.override_date === $formattedCurrentDate && !event.is_deleted;
          } else {
            // Show base entry only if it matches the weekday AND doesn't have an override for this date
            return event.week_day === $currentWeekDay && !overriddenEntries.has(event.schedule_entry_id);
          }
        });
      } else if ($viewMode === 'week') {
        return $currentEventSchedule.entries;
      } else {
        return $currentEventSchedule.entries;
      }
    }
  );
  
  function handleEventUpdate(event: Event, updates: Partial<Event>, isLocal: boolean = false) {
    if (event.override_id) {
      // Handle updates for override events using the events store
      updateEventOverride(event.schedule_entry_id, event.override_id, updates);
    } else {
      // Base events should not be updated through drag and drop
      console.warn('Base events cannot be modified through drag and drop');
    }
  }
  
  function handleTopDragMouseDown(e: MouseEvent, event: Event) {
    if (!event.override_id) return;
    
    const gridElement = (e.currentTarget as HTMLElement).closest('.schedule-grid');
    if (!gridElement) return;
    
    initializeTopDrag(e, event, gridElement as HTMLElement, get(timeSlots), {
      onUpdate: (updates, isLocal) => handleEventUpdate(event, updates as Partial<Event>, isLocal)
    });
  }

  function handleBottomDragMouseDown(e: MouseEvent, event: Event) {
    if (!event.override_id) return;
    
    const gridElement = (e.currentTarget as HTMLElement).closest('.schedule-grid');
    if (!gridElement) return;
    
    initializeBottomDrag(e, event, gridElement as HTMLElement, get(timeSlots), {
      onUpdate: (updates, isLocal) => handleEventUpdate(event, updates as Partial<Event>, isLocal)
    });
  }

  function handleEventDragMouseDown(e: MouseEvent, event: Event) {
    if (!event.override_id) return;
    
    const gridElement = (e.currentTarget as HTMLElement).closest('.schedule-grid');
    if (!gridElement) return;
    
    initializeEventDrag(
      e,
      event,
      gridElement as HTMLElement,
      get(timeSlots),
      totalColumns,
      headerCells,
      $activeFields,
      fieldToGridColMap,
      {
        onUpdate: (updates, isLocal) => handleEventUpdate(event, updates as Partial<Event>, isLocal)
      }
    );
  }

  function handleHorizontalDragMouseDown(e: MouseEvent, event: Event, direction: 'left' | 'right') {
    if (!event.override_id) return;
    
    const gridElement = (e.currentTarget as HTMLElement).closest('.schedule-grid');
    if (!gridElement) return;
    
    initializeHorizontalDrag(
      e,
      event,
      direction,
      gridElement as HTMLElement,
      totalColumns,
      $activeFields,
      fieldToGridColMap,
      {
        onUpdate: (updates, isLocal) => handleEventUpdate(event, updates as Partial<Event>, isLocal)
      }
    );
  }
  
  // Info card state
  const handleEventInfoCard = (e: MouseEvent, event: Event) => {
    infoCardStore.openEventInfoCard(e, event, containerElement);
  };

  function handleWindowClick() {
    infoCardStore.closeInfoCard();
  }

  $: ({ editingEvent, infoCardForm, editingEventPosition } = $infoCardStore);

  function handleEmptyCellDblClick(e: MouseEvent, time: string, cell: { fieldId: number }, weekDay: number) {
    e.stopPropagation();
    const newEntry = {
      schedule_entry_id: Date.now(),
      team_id: null,
      field_id: cell.fieldId,
      week_day: weekDay,
      start_time: time,
      end_time: addMinutes(time, 60)
    };
    addScheduleEntry(newEntry);
    infoCardStore.openEventInfoCard(e, newEntry, containerElement);
  }
  
  async function handleRecurringClick(event: Event, date: Date) {
    if (!event.override_id && $currentEventSchedule) {
      const dateStr = formatDateYYYYMMDD(date);
      
      // Check if we already have an override for this date
      const existingOverride = $currentEventSchedule.entries.find(e => 
        e.override_id && 
        e.schedule_entry_id === event.schedule_entry_id && 
        e.override_date === dateStr
      );
      
      if (!existingOverride && $currentActiveSchedule) {
        await createEventOverride(event, dateStr, $currentActiveSchedule.active_schedule_id);
      }
    }
  }
  
  // Compute overlapping events for the current day
  $: overlapMap = detectOverlappingEvents($filteredEvents, $currentWeekDay, $activeFields);
  $: eventOffsets = calculateEventOffsets(overlapMap);
  $: weekOverlapMaps = $weekDates.map(date => 
    detectOverlappingEvents($filteredEvents.filter(e => {
      if(e.override_id) {
        return e.override_date === formatDateYYYYMMDD(date.date) && !e.is_deleted;
      } else {
        return e.week_day === date.weekDay;
      }
    }), date.weekDay, $activeFields)
  );
  $: weekEventOffsets = weekOverlapMaps.map(overlapMap => 
    calculateEventOffsets(overlapMap)
  );
  
  // Function to calculate event style based on overlap information
  function getEventStyle(
    event: Event, 
    mapping: { colIndex: number, colSpan: number }, 
    startRow: number, 
    endRow: number, 
    offsetMap: Map<number, number>,
    overlapMap: Map<number, number[]>
  ) {
    const offset = offsetMap.get(event.schedule_entry_id) || 0;
    const totalOverlaps = getTotalOverlaps(event.schedule_entry_id, overlapMap);
    
    let widthPercentage = 100;
    if (totalOverlaps > 0) {
      widthPercentage = Math.max(65, 100 - (totalOverlaps * 10));
    }
    
    const horizontalOffset = offset * 8;
    
    return `
      grid-row-start: ${startRow};
      grid-row-end: ${endRow + 1};
      grid-column-start: ${mapping.colIndex};
      grid-column-end: span ${mapping.colSpan};
      position: relative;
      width: calc(${widthPercentage}% - 10px); /* Account for margins on both sides */
      left: ${horizontalOffset}px;
      z-index: ${10 + offset};
      box-shadow: ${offset > 0 ? '0 2px 4px rgba(0,0,0,0.1)' : 'none'};
      border-left: ${totalOverlaps > 0 ? '3px solid #e53e3e' : 'none'};
    `;
  }
</script>

<svelte:window on:click={handleWindowClick} />

<!-- Set containerElement as a reference and ensure position relative -->
<div class="schedule-container" bind:this={containerElement} style="position: relative;">
  <div class="schedule-controls flex justify-between items-center my-2 py-2">
    <div class="timeslot-selector flex items-center gap-4">
      <select
        id="timeslot-granularity"
        class="form-input-sm"
        on:change={handleGranularityChange}
      >
        <option value="15">15 Minutes</option>
        <option value="30">30 Minutes</option>
      </select>
      
      <!-- Toggle for including active fields-->
      <div class="checkbox-container">
        <input 
          id="include-active-fields"
          type="checkbox"
          checked={$includeActiveFields}
          on:change={handleIncludeActiveFieldsToggle}
          class="form-checkbox tooltip-target"
          data-tooltip="Include all fields from {$selectedFacilityName}"
        />
      </div>
    </div>

    <div class="date-navigation flex items-center gap-2">
      {#if $viewMode === 'day'}
        <button on:click={previousDay} class="nav-button">‹</button>
        <span class="current-date text-lg font-medium text-sage-800">
          {formatDateForDisplay($currentDate)}
          {#if !$currentActiveSchedule}
            <span class="text-red-500 text-sm ml-2">(No active schedule)</span>
          {/if}
        </span>
        <button on:click={nextDay} class="nav-button">›</button>
      {:else if $viewMode === 'week'}
        <button on:click={previousWeek} class="nav-button">‹</button>
        <span class="current-date text-lg font-medium text-sage-800">
          Week {getWeekNumber($currentDate)}
          {#if !$weekDates.some(d => d.isWithinActiveSchedule)}
            <span class="text-red-500 text-sm ml-2">(No active schedule)</span>
          {/if}
        </span>
        <button on:click={nextWeek} class="nav-button">›</button>
      {:else}
        <!-- Custom month view navigation -->
        <button on:click={previousMonth} class="nav-button">‹</button>
        <span class="current-date text-lg font-medium text-sage-800">
          {formattedMonth}
        </span>
        <button on:click={nextMonth} class="nav-button">›</button>
      {/if}
    </div>

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
        Week
      </button>
      <button
        class="view-toggle-btn { $viewMode === 'month' ? 'active' : '' }"
        on:click={() => $viewMode = 'month'}
      >
        Month
      </button>
    </div>
  </div>

  {#if $viewMode === 'month'}
    <Calendar bind:this={calendarComponent} />
  {:else if $viewMode === 'day'}
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
            role="button" 
            tabindex="0"
            aria-label="Create new event"
            style="grid-column: {cell.colIndex} / span {cell.colSpan}; grid-row: {rowIndex + 2};"
            on:dblclick={(e) => handleEmptyCellDblClick(e, time, cell, $currentWeekDay)}
          ></div>
        {/each}
      {/each}
  
      <!-- EVENTS -->
      {#if $currentEventSchedule}
        {#each $filteredEvents as event (event.override_id ? `${event.schedule_entry_id}-${event.override_id}` : `${event.schedule_entry_id}`)}
          {#if fieldToGridColMap.has(event.field_id!)}
            {@const mapping = fieldToGridColMap.get(event.field_id!)!}
            {@const hasOverlaps = getTotalOverlaps(event.schedule_entry_id, overlapMap) > 0}
            {@const startRow = getRowForTimeWithSlots(event.start_time, $timeSlots)}
            {@const endRow = getEventRowEndWithSlots(event.end_time, $timeSlots)}
            {@const visibility = getEventContentVisibility(startRow, endRow)}
            <div
              class="schedule-event"
              role="button"
              tabindex="0"
              data-overlapping={hasOverlaps}
              on:dblclick={(e) => handleEventInfoCard(e, event)}
              on:mousedown={(e) => handleEventDragMouseDown(e, event)}
              style={getEventStyle(
                event,
                mapping,
                startRow,
                endRow,
                eventOffsets,
                overlapMap
              )}
            >
              <!-- Recurring indicator -->
              <button
                type="button"
                class="recurring-indicator {event.override_id ? 'override' : 'regular'}" 
                title="{event.override_id ? 'Modified occurrence' : 'Recurring event'}"
                on:click|stopPropagation={() => handleRecurringClick(event, $currentDate)}
                style="cursor: {event.override_id ? 'default' : 'pointer'}"
                aria-label="Create override event"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                  <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
                </svg>
              </button>
              
              <!-- Horizontal resize handles -->
              <div 
                class="resize-handle left" 
                role="button"
                tabindex="0"
                aria-label="Resize event horizontally (left edge)"
                on:mousedown={(e) => handleHorizontalDragMouseDown(e, event, 'left')}
                style="position: absolute; left: 0; top: 0; bottom: 0; width: 5px; cursor: ew-resize; background: transparent;"
              ></div>
              <div 
                class="resize-handle right" 
                role="button"
                tabindex="0"
                aria-label="Resize event horizontally (right edge)"
                on:mousedown={(e) => handleHorizontalDragMouseDown(e, event, 'right')}
                style="position: absolute; right: 0; top: 0; bottom: 0; width: 5px; cursor: ew-resize; background: transparent;"
              ></div>
      
              <!-- Top resize handle -->
              <div 
                class="resize-handle top" 
                role="button"
                tabindex="0"
                aria-label="Resize event start time"
                on:mousedown={(e) => handleTopDragMouseDown(e, event)}
                style="position: absolute; top: 0; left: 0; right: 0; height: 5px; cursor: ns-resize; background: transparent;"
              ></div>
              <!-- Event content -->
              <div class="event-team font-bold text-[1.15em]">
                { event.team_id !== null 
                    ? ($teamNameLookup.get(event.team_id) ?? `Team ${event.team_id}`) 
                    : "Select a team" }
              </div>
              {#if visibility.showField}
                <div class="event-field flex items-center gap-1 text-[1.12em] text-gray-600">
                  📍 {getFieldName(event.field_id!, $activeFields)}
                </div>
              {/if}
              {#if visibility.showTime}
                <div class="event-time flex items-center gap-1 text-[1.12em] text-gray-600">
                  🕐 {normalizeTime(event.start_time)} - {normalizeTime(event.end_time)}
                </div>
              {/if}
              <!-- Bottom resize handle -->
              <div 
                class="resize-handle bottom" 
                role="button"
                tabindex="0"
                aria-label="Resize event end time"
                on:mousedown={(e) => handleBottomDragMouseDown(e, event)}
                style="position: absolute; bottom: 0; left: 0; right: 0; height: 5px; cursor: ns-resize; background: transparent;"
              ></div>
            </div>
          {/if}
        {/each}
      {/if}
    </div>
  
  {:else}
    <!-- Week View: Show each day with its date -->
    {#each $weekDates as calendarDate, index}
      <div class="day-section">
        <h3 class="day-header">
          {calendarDate.formattedDate}
          {#if !calendarDate.isWithinActiveSchedule}
            <span class="text-red-500 text-sm ml-2">(No active schedule)</span>
          {/if}
        </h3>
        
        <div 
          class="schedule-grid"
          style="--total-columns: {totalColumns}; --total-rows: {$timeSlots.length + 1}; margin-bottom: 2rem;"
        >
          <!-- Day grid content - headers, timeslots, and events filtered by the day's weekDay -->
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
                role="button" 
                tabindex="0"
                aria-label="Create new event"
                style="grid-column: {cell.colIndex} / span {cell.colSpan}; grid-row: {rowIndex + 2};"
                on:dblclick={(e) => handleEmptyCellDblClick(e, time, cell, calendarDate.weekDay)}
              ></div>
            {/each}
          {/each}
  
          <!-- EVENTS for this day -->
          {#each $filteredEvents.filter(event => {
            // Create a Set of schedule_entry_ids that have overrides for this date
            const dateStr = formatDateYYYYMMDD(calendarDate.date);
            const overriddenEntries = new Set(
              $filteredEvents
                .filter(e => e.override_id && e.override_date === dateStr)
                .map(e => e.schedule_entry_id)
            );
            
            if (event.override_id) {
              return event.override_date === dateStr && !event.is_deleted;
            } else {
              return event.week_day === calendarDate.weekDay && !overriddenEntries.has(event.schedule_entry_id);
            }
          }) as event (event.override_id ? `${event.schedule_entry_id}-${event.override_id}` : `${event.schedule_entry_id}`)}
            {#if fieldToGridColMap.has(event.field_id!)}
              {@const mapping = fieldToGridColMap.get(event.field_id!)!}
              {@const hasOverlaps = getTotalOverlaps(event.schedule_entry_id, weekOverlapMaps[index]) > 0}
              {@const startRow = getRowForTimeWithSlots(event.start_time, $timeSlots)}
              {@const endRow = getEventRowEndWithSlots(event.end_time, $timeSlots)}
              {@const visibility = getEventContentVisibility(startRow, endRow)}
              <div
                class="schedule-event"
                role="button"
                tabindex="0"
                data-overlapping={hasOverlaps}
                on:dblclick={(e) => handleEventInfoCard(e, event)}
                on:mousedown={(e) => handleEventDragMouseDown(e, event)}
                style={getEventStyle(
                  event,
                  mapping,
                  startRow,
                  endRow,
                  weekEventOffsets[index],
                  weekOverlapMaps[index]
                )}
              >
                <!-- Recurring indicator -->
                <button
                  type="button"
                  class="recurring-indicator {event.override_id ? 'override' : 'regular'}" 
                  title="{event.override_id ? 'Modified occurrence' : 'Recurring event'}"
                  on:click|stopPropagation={() => handleRecurringClick(event, calendarDate.date)}
                  style="cursor: {event.override_id ? 'default' : 'pointer'}"
                  aria-label="Create override event"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                    <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
                  </svg>
                </button>
                
                <!-- Horizontal resize handles -->
                <div 
                  class="resize-handle left" 
                  role="button"
                  tabindex="0"
                  aria-label="Resize event horizontally (left edge)"
                  on:mousedown={(e) => handleHorizontalDragMouseDown(e, event, 'left')}
                  style="position: absolute; left: 0; top: 0; bottom: 0; width: 5px; cursor: ew-resize; background: transparent;"
                ></div>
                <div 
                  class="resize-handle right" 
                  role="button"
                  tabindex="0"
                  aria-label="Resize event horizontally (right edge)"
                  on:mousedown={(e) => handleHorizontalDragMouseDown(e, event, 'right')}
                  style="position: absolute; right: 0; top: 0; bottom: 0; width: 5px; cursor: ew-resize; background: transparent;"
                ></div>
        
                <!-- Top resize handle -->
                <div 
                  class="resize-handle top" 
                  role="button"
                  tabindex="0"
                  aria-label="Resize event start time"
                  on:mousedown={(e) => handleTopDragMouseDown(e, event)}
                  style="position: absolute; top: 0; left: 0; right: 0; height: 5px; cursor: ns-resize; background: transparent;"
                ></div>
                <!-- Event content -->
                <div class="event-team font-bold text-[1.15em]">
                  { event.team_id !== null 
                      ? ($teamNameLookup.get(event.team_id) ?? `Team ${event.team_id}`) 
                      : "Select a team" }
                </div>
                {#if visibility.showField}
                  <div class="event-field flex items-center gap-1 text-[1.12em] text-gray-600">
                    📍 {getFieldName(event.field_id!, $activeFields)}
                  </div>
                {/if}
                {#if visibility.showTime}
                  <div class="event-time flex items-center gap-1 text-[1.12em] text-gray-600">
                    🕐 {normalizeTime(event.start_time)} - {normalizeTime(event.end_time)}
                  </div>
                {/if}
                <!-- Bottom resize handle -->
                <div 
                  class="resize-handle bottom" 
                  role="button"
                  tabindex="0"
                  aria-label="Resize event end time"
                  on:mousedown={(e) => handleBottomDragMouseDown(e, event)}
                  style="position: absolute; bottom: 0; left: 0; right: 0; height: 5px; cursor: ns-resize; background: transparent;"
                ></div>
              </div>
            {/if}
          {/each}
        </div>
      </div>
    {/each}
  {/if}

  <!-- INFO CARD -->
  {#if editingEvent && infoCardForm}
    <InfoCard 
      infoCardForm={infoCardForm} 
      editingEventPosition={editingEventPosition} 
      teams={$teams} 
      activeFields={$activeFields} 
      generateFieldOptions={generateFieldOptions} 
    />
  {/if}
</div>
