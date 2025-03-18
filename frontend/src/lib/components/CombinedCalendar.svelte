<script lang="ts">
    import type { Field } from '$lib/schemas/field';
    import type { ScheduleEntry } from '$lib/schemas/schedule';
    import { fields } from '$stores/fields';
    import { teams } from '$stores/teams';
    import { derived, get, writable } from 'svelte/store';
    import { updateScheduleEntry, addScheduleEntry } from '$stores/schedules';
    import { buildResources, normalizeTime, handleGranularityChange, timeSlots, 
            getRowForTimeWithSlots, getEventRowEndWithSlots, addMinutes,
            includeActiveFields, handleIncludeActiveFieldsToggle, getEventContentVisibility } from '$lib/utils/calendarUtils';
    import { addDays, formatDateForDisplay, getDayOfWeek,
            findActiveScheduleForDate, getWeekDates } from '$lib/utils/dateUtils';
    import InfoCard from '$lib/components/InfoCard.svelte';
    import { detectOverlappingEvents, 
      calculateEventOffsets, getTotalOverlaps } from '$lib/utils/overlapUtils';
    import { getFieldColumns, buildFieldToGridColumnMap, generateHeaderCells, getFieldName, generateFieldOptions } from '$lib/utils/fieldUtils';
    import { initializeTopDrag, initializeBottomDrag, initializeEventDrag, initializeHorizontalDrag } from '$lib/utils/dndUtils';
    import { infoCardStore } from '$lib/utils/infoCardUtils';
    import { facilities } from '$stores/facilities';
    import { activeSchedules } from '$stores/activeSchedules';
    import { schedules } from '$stores/schedules';
  
    let containerElement: HTMLElement;
    
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
    
    const currentActiveSchedule = derived(
      [currentDate, activeSchedules], 
      ([$currentDate, $activeSchedules]) => {
        return findActiveScheduleForDate($currentDate, $activeSchedules);
      }
    );
    
    const currentSchedule = derived(
      [currentActiveSchedule, schedules],
      ([$currentActiveSchedule, $schedules]) => {
        if (!$currentActiveSchedule) return null;
        return $schedules.find(s => s.schedule_id === $currentActiveSchedule.schedule_id) ?? null;
      }
    );
    
    const weekDates = derived(
      [currentDate, activeSchedules],
      ([$currentDate, $activeSchedules]) => {
        return getWeekDates($currentDate, $activeSchedules);
      }
    );
    
    const selectedFacilityName = derived([facilities, currentSchedule], ([$facilities, $currentSchedule]) => {
      if (!$currentSchedule || !$currentSchedule.facility_id) {
        return "this facility";
      }
      
      const facility = $facilities.find(f => f.facility_id === $currentSchedule?.facility_id);
      return facility?.name || "this facility";
    });
    
    const activeFields = derived([fields, currentSchedule, includeActiveFields], ([$fields, $currentSchedule, $includeActiveFields]) => {
      return buildResources($fields, $currentSchedule, $includeActiveFields);
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
    
    // Filter active events for current date
    const filteredEvents = derived(
      [currentWeekDay, currentSchedule, viewMode],
      ([$currentWeekDay, $currentSchedule, $viewMode]) => {
        if (!$currentSchedule || !$currentSchedule.entries) return [];
        
        // In day view, filter by current day; in week view, return all entries
        if ($viewMode === 'day') {
          return $currentSchedule.entries.filter(event => {
            return event.week_day === $currentWeekDay;
          });
        } else {
          // Week view - return all entries
          return $currentSchedule.entries;
        }
      }
    );
    
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
  
    // Compute overlapping events for the current day
    $: overlapMap = detectOverlappingEvents($filteredEvents, $currentWeekDay, $activeFields);
    $: eventOffsets = calculateEventOffsets(overlapMap);
    $: weekOverlapMaps = $weekDates.map(date => 
      detectOverlappingEvents($filteredEvents.filter(e => e.week_day === date.weekDay), date.weekDay, $activeFields)
    );
    $: weekEventOffsets = weekOverlapMaps.map(overlapMap => 
      calculateEventOffsets(overlapMap)
    );
  
    // Function to calculate event style based on overlap information
    function getEventStyle(
      event: ScheduleEntry, 
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
        border-left: ${totalOverlaps > 0 ? '3px solid #e53e3e' : 'none'};none'};
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
  
      <div class="date-navigation flex items-center gap-2" style="{$viewMode === 'week' ? 'visibility: hidden;' : ''}">
        <button on:click={previousDay} class="nav-button" disabled={$viewMode === 'week'}>‹</button>
        <span class="current-date text-lg font-medium text-sage-800">
          {formatDateForDisplay($currentDate)}
          {#if !$currentActiveSchedule}
            <span class="text-red-500 text-sm ml-2">(No active schedule)</span>
          {/if}
        </span>
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
              on:dblclick={(e) => handleEmptyCellDblClick(e, time, cell, $currentWeekDay)}
            ></div>
          {/each}
        {/each}
    
        <!-- EVENTS -->
        {#if $currentSchedule}
          {#each $filteredEvents.filter(event => event.week_day === $currentWeekDay) as event (event.schedule_entry_id)}
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
            {#each $filteredEvents.filter(event => event.week_day === calendarDate.weekDay) as event (event.schedule_entry_id)}
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
