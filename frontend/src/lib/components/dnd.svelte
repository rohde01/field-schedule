<script lang="ts">
  import { dropdownState } from '../../stores/ScheduleDropdownState';
  import type { Field } from '$lib/schemas/field';
  import type { ScheduleEntry } from '$lib/schemas/schedule';
  import { fields } from '$stores/fields';
  import { teams } from '$stores/teams';
  import { derived, get, writable } from 'svelte/store';
  import { updateScheduleEntry, addScheduleEntry } from '$stores/schedules';
  import { buildResources, normalizeTime, weekDays, handleGranularityChange, timeSlots, activeEvents, 
          nextDay, previousDay, currentWeekDay, getRowForTimeWithSlots, getEventRowEndWithSlots, addMinutes } from '$lib/utils/calendarUtils';
  import InfoCard from '$lib/components/InfoCard.svelte';
  import { getFieldColumns, buildFieldToGridColumnMap, generateHeaderCells, getFieldName, generateFieldOptions } from '$lib/utils/fieldUtils';
  import { initializeTopDrag, initializeBottomDrag, initializeEventDrag, initializeHorizontalDrag } from '$lib/utils/dndUtils';
  import { infoCardStore } from '$lib/utils/infoCardUtils';

  let containerElement: HTMLElement;
  const activeFields = derived([fields, dropdownState], ([$fields, $dropdownState]) => {
    const selectedSchedule = $dropdownState.selectedSchedule;
    if (!selectedSchedule) {
      if ($dropdownState.selectedFacility) {
        return $fields.filter(field => field.facility_id === $dropdownState.selectedFacility?.facility_id);
      }
      return [];
    }
        return $fields.filter(field => field.facility_id === selectedSchedule.facility_id);
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
  
  function handleTopDragMouseDown(e: MouseEvent, scheduleEntry: ScheduleEntry) {
    const gridElement = (e.currentTarget as HTMLElement).closest('.schedule-grid');
    if (!gridElement) return;
    
    initializeTopDrag(e, scheduleEntry, gridElement as HTMLElement, get(timeSlots), {
      onUpdate: (updates, isLocal) => updateScheduleEntry(scheduleEntry.schedule_entry_id, updates, isLocal)
    });
  }

  function handleBottomDragMouseDown(e: MouseEvent, scheduleEntry: ScheduleEntry) {
    const gridElement = (e.currentTarget as HTMLElement).closest('.schedule-grid');
    if (!gridElement) return;
    
    initializeBottomDrag(e, scheduleEntry, gridElement as HTMLElement, get(timeSlots), {
      onUpdate: (updates, isLocal) => updateScheduleEntry(scheduleEntry.schedule_entry_id, updates, isLocal)
    });
  }

  function handleEventDragMouseDown(e: MouseEvent, scheduleEntry: ScheduleEntry) {
    const gridElement = (e.currentTarget as HTMLElement).closest('.schedule-grid');
    if (!gridElement) return;
    
    initializeEventDrag(
      e,
      scheduleEntry,
      gridElement as HTMLElement,
      get(timeSlots),
      totalColumns,
      headerCells,
      $activeFields,
      fieldToGridColMap,
      {
        onUpdate: (updates, isLocal) => updateScheduleEntry(scheduleEntry.schedule_entry_id, updates, isLocal)
      }
    );
  }

  function handleHorizontalDragMouseDown(e: MouseEvent, scheduleEntry: ScheduleEntry, direction: 'left' | 'right') {
    const gridElement = (e.currentTarget as HTMLElement).closest('.schedule-grid');
    if (!gridElement) return;
    
    initializeHorizontalDrag(
      e,
      scheduleEntry,
      direction,
      gridElement as HTMLElement,
      totalColumns,
      $activeFields,
      fieldToGridColMap,
      {
        onUpdate: (updates, isLocal) => updateScheduleEntry(scheduleEntry.schedule_entry_id, updates, isLocal)
      }
    );
  }
  
  // Info card state
  const handleEventInfoCard = (e: MouseEvent, event: ScheduleEntry) => {
    infoCardStore.openEventInfoCard(e, event, containerElement);
  };

  function handleWindowClick() {
    infoCardStore.closeInfoCard();
  }

  $: ({ editingEvent, infoCardForm, editingEventPosition } = $infoCardStore);

  // Weekday state
  $: currentDay = $currentWeekDay;

  // View mode state
  let viewMode = writable('day');

  function handleEmptyCellDblClick(e: MouseEvent, time: string, cell: { fieldId: number }) {
    e.stopPropagation();
    const newEntry = {
      schedule_entry_id: Date.now(),
      team_id: null,
      field_id: cell.fieldId,
      week_day: $currentWeekDay,
      start_time: time,
      end_time: addMinutes(time, 60)
    };
    addScheduleEntry(newEntry);
    infoCardStore.openEventInfoCard(e, newEntry, containerElement);
  }

</script>

<svelte:window on:click={handleWindowClick} />

<!-- Set containerElement as a reference and ensure position relative -->
<div class="schedule-container" bind:this={containerElement} style="position: relative;">
  <div class="schedule-controls flex justify-between items-center my-2 py-2">
    <div class="timeslot-selector">
      <select
        id="timeslot-granularity"
        class="form-input-sm"
        on:change={handleGranularityChange}
      >
        <option value="15">15 Minutes</option>
        <option value="30">30 Minutes</option>
      </select>
    </div>

    <div class="weekday-navigation flex items-center gap-2" style="{$viewMode === 'week' ? 'visibility: hidden;' : ''}">
      <button on:click={previousDay} class="nav-button" disabled={$viewMode === 'week'}>‹</button>
      <span class="current-day text-lg font-medium text-sage-800">{weekDays[$currentWeekDay]}</span>
      <button on:click={nextDay} class="nav-button" disabled={$viewMode === 'week'}>›</button>
    </div>

    <div class="view-toggle">
      <button
        class="view-toggle-btn left-btn { $viewMode === 'day' ? 'active' : '' }"
        on:click={() => $viewMode = 'day'}
      >
        Day
      </button>
      <button
        class="view-toggle-btn right-btn { $viewMode === 'week' ? 'active' : '' }"
        on:click={() => $viewMode = 'week'}
      >
        Week
      </button>
    </div>
  </div>

  {#if $viewMode === 'day'}
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
            on:dblclick={(e) => handleEmptyCellDblClick(e, time, cell)}
          ></div>
        {/each}
      {/each}
  
      <!-- EVENTS -->
      {#each $activeEvents.filter(event => event.week_day === $currentWeekDay) as event (event.schedule_entry_id)}
        {#if fieldToGridColMap.has(event.field_id!)}
          {@const mapping = fieldToGridColMap.get(event.field_id!)!}
          <div
            class="schedule-event"
            role="button"
            tabindex="0"
            on:dblclick={(e) => handleEventInfoCard(e, event)}
            on:mousedown={(e) => handleEventDragMouseDown(e, event)}
            style="
              grid-row-start: {getRowForTimeWithSlots(event.start_time, $timeSlots)};
              grid-row-end: {getEventRowEndWithSlots(event.end_time, $timeSlots) + 1};
              grid-column-start: {mapping.colIndex};
              grid-column-end: span {mapping.colSpan};
              position: relative;
            "
          >
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
            <div class="event-field flex items-center gap-1 text-[1.12em] text-gray-600">
              📍 {getFieldName(event.field_id!, $activeFields)}
            </div>
            <div class="event-time flex items-center gap-1 text-[1.12em] text-gray-600">
              🕐 {normalizeTime(event.start_time)} - {normalizeTime(event.end_time)}
            </div>
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
  
  {:else}
    <!-- Continuous View Mode: Render a schedule grid for each day stacked vertically -->
    {#each weekDays as day, dayIndex}
      <div class="day-section">
        <div 
          class="schedule-grid"
          style="--total-columns: {totalColumns}; --total-rows: {$timeSlots.length + 1}; margin-bottom: 2rem;"
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
                on:dblclick={(e) => handleEmptyCellDblClick(e, time, cell)}
              ></div>
            {/each}
          {/each}
  
          <!-- EVENTS for this day -->
          {#each $activeEvents.filter(event => event.week_day === dayIndex) as event (event.schedule_entry_id)}
            {#if fieldToGridColMap.has(event.field_id!)}
              {@const mapping = fieldToGridColMap.get(event.field_id!)!}
              <div
                class="schedule-event"
                role="button"
                tabindex="0"
                on:dblclick={(e) => handleEventInfoCard(e, event)}
                on:mousedown={(e) => handleEventDragMouseDown(e, event)}
                style="
                  grid-row-start: {getRowForTimeWithSlots(event.start_time, $timeSlots)};
                  grid-row-end: {getEventRowEndWithSlots(event.end_time, $timeSlots) + 1};
                  grid-column-start: {mapping.colIndex};
                  grid-column-end: span {mapping.colSpan};
                  position: relative;
                "
              >
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
                <div class="event-field flex items-center gap-1 text-[1.12em] text-gray-600">
                  📍 {getFieldName(event.field_id!, $activeFields)}
                </div>
                <div class="event-time flex items-center gap-1 text-[1.12em] text-gray-600">
                  🕐 {normalizeTime(event.start_time)} - {normalizeTime(event.end_time)}
                </div>
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
