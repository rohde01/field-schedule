<script lang="ts">
    import { fieldSchema } from '$lib/schemas/field';
    import type { z } from 'zod';
    import { sampleFields, sampleEvents } from '$lib/utils/test_data';
  
    // Types & Schemas
    type InferredField = z.infer<typeof fieldSchema>;
  
    interface Event {
      id: number;
      title: string;
      field_id: number;
      start_time: string;
      end_time: string;
    }
  
    // Use sample data from test_data.ts
    export let fields: InferredField[] = sampleFields;
    let events: Event[] = sampleEvents;
  
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
  
    function getQuarterFieldsForHalf(field: InferredField, halfFieldId: number) {
      return field.quarter_subfields.filter(
        (q) => q.parent_field_id === halfFieldId
      );
    }
  
    function getFieldColumns(field: InferredField): number {
      if (!field.half_subfields.length) {
        return 1;
      }
      return field.half_subfields.reduce((acc, half) => {
        const quarterCount = getQuarterFieldsForHalf(field, half.field_id).length;
        return acc + (quarterCount || 1);
      }, 0);
    }
  
    function buildFieldToGridColumnMap(fields: InferredField[]) {
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
  
            if (quarterFields.length === 0) {
              map.set(half.field_id, {
                colIndex: currentColIndex,
                colSpan: 1
              });
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
    const timeslots: string[] = generateTimeSlots("16:00", "20:30", 30);
  
    interface HeaderCell {
      label: string;
      colIndex: number;
      colSpan: number;
    }
    let headerCells: HeaderCell[] = [];
    
    {
      let colIndex = 2;  // col 1 is "Time"
  
      for (const field of fields) {
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
    const totalColumns = 1 + fields.reduce((acc, f) => acc + getFieldColumns(f), 0);
  
    const fieldToGridColMap = buildFieldToGridColumnMap(fields);
  
    function rowForTime(time: string): number {
      return timeslots.indexOf(time) + 2;  // +2 for header row offset
    }
  </script>
  
  <div 
    class="schedule-grid"
    style="
      --total-columns: {totalColumns};
      --total-rows: {timeslots.length};
    "
  >
    <!-- HEADER ROW -->
    <div
      class="schedule-header"
      style="grid-row: 1; grid-column: 1;"
    >
      Time
    </div>

    {#each headerCells as cell}
      <div
        class="schedule-header"
        style="
          grid-row: 1;
          grid-column: {cell.colIndex} / span {cell.colSpan};
        "
      >
        {cell.label}
      </div>
    {/each}

    <!-- TIMESLOT ROWS (just the time label + empty cells) -->
    {#each timeslots as time, rowIndex}
      <!-- Leftmost cell: the timeslot label -->
      <div
        class="schedule-time"
        style="grid-row: {rowIndex + 2}; grid-column: 1;"
      >
        {time}
      </div>

      <!-- For each header cell, place an empty cell at [rowIndex, columnIndex]. 
           We do not put events in these cells; events are placed separately below. -->
      {#each headerCells as cell}
        <div
          class="schedule-cell"
          style="
            grid-row: {rowIndex + 2};
            grid-column: {cell.colIndex} / span {cell.colSpan};
          "
        ></div>
      {/each}
    {/each}

    <!-- EVENTS: each one spans multiple rows from start_time to end_time -->
    {#each events as event}
      {#if fieldToGridColMap.has(event.field_id)}
        {@const mapping = fieldToGridColMap.get(event.field_id)!}
          <div
            class="schedule-event"
            style="
              grid-row: {rowForTime(event.start_time)} / {rowForTime(event.end_time)};
              grid-column: {mapping.colIndex} / span {mapping.colSpan};
            "
          >
            {event.title}
          </div>
      {/if}
    {/each}
  </div>