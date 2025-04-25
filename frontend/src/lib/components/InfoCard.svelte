<script lang="ts">
  import { Label, Input, Select, Datepicker, Timepicker } from 'flowbite-svelte';
  import { TrashBinSolid, ClockSolid } from 'flowbite-svelte-icons';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { teams } from '../stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '../stores/fields';
  import type { Field } from '$lib/schemas/field';
  import { deleteScheduleEntry } from '../stores/schedules';
  import { computeDateUTC } from '$lib/utils/dateUtils';
  import { commitUpdate, getOriginalRecurrenceStart } from '$lib/utils/calendarUtils';
  import { Card } from 'flowbite-svelte';
  import { onMount } from 'svelte';

  export let entryUiId: string;

  let wrapperElement: HTMLDivElement;
  let wrapperStyle: string = '';
  const cardWidth = 300;
  const offset = 20;

  onMount(() => {
    if (wrapperElement) {
      const parent = wrapperElement.parentElement as HTMLElement;
      const rect = parent.getBoundingClientRect();
      const spaceRight = window.innerWidth - (rect.left + rect.width);
      if (spaceRight > cardWidth + offset) {
        wrapperStyle = `top:0px; left:${rect.width + offset}px;`;
      } else {
        wrapperStyle = `top:0px; left:-${cardWidth + offset}px;`;
      }
    }
  });

  let entry: any;
  let selectedDate: Date | null = null;
  let selectedTimerange = { time: '', endTime: '' };

  $: entry = $processedEntries.find(e => e.ui_id === entryUiId);
  $: if (entry) {
    selectedDate = entry.dtstart;
    const oldStart = entry.dtstart.toISOString().slice(11,16);
    const oldEnd = entry.dtend.toISOString().slice(11,16);
    selectedTimerange = { time: oldStart, endTime: oldEnd };
  }

  let teamsData: Team[] = [];
  let fieldsData: Field[] = [];
  let summaryEditing = false;
  let fieldEditing = false;
  let teamEditing = false;
  let dateEditing = false;
  let showTimeInput = false;
  let isDeleting = false;

  teams.subscribe(data => {
    teamsData = data;
  });

  fields.subscribe(() => {
    fieldsData = getFlattenedFields();
  });

  function handleDateChange(event: any) {
    if (!entry) return;
    const date = selectedDate || new Date(event.target.value);
    const start = entry.start_time;
    const end = entry.end_time;
    const newStart = computeDateUTC(date, start);
    const newEnd = computeDateUTC(date, end);
    processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, dtstart: newStart, dtend: newEnd } : e));
    commitUpdate({ ...entry, dtstart: newStart, dtend: newEnd }, getOriginalRecurrenceStart(entry));
  }

  function handleTimeChange(event: CustomEvent<{ time: string; endTime?: string }>) {
    if (!entry || !selectedDate) return;
    const { time, endTime: rawEndTime } = event.detail;
    const endTime = rawEndTime!;
    const newStart = computeDateUTC(selectedDate, time);
    const newEnd = computeDateUTC(selectedDate, endTime);
    processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, dtstart: newStart, dtend: newEnd, start_time: time, end_time: endTime } : e));
    commitUpdate({ ...entry, dtstart: newStart, dtend: newEnd, start_time: time, end_time: endTime }, getOriginalRecurrenceStart(entry));
  }

  function handleDelete() {
    isDeleting = true;
    const recDateStr = getOriginalRecurrenceStart(entry);
    const recDate = recDateStr ? new Date(recDateStr) : null;
    deleteScheduleEntry(entry.uid, entry.schedule_id, recDate);
    isDeleting = false;
  }
</script>

<div
  bind:this={wrapperElement}
  role="button"
  tabindex="0"
  on:keydown={(e) => { if(e.key === "Enter" || e.key === " ") e.stopPropagation(); }}
  on:click|stopPropagation
  class="absolute z-20 w-[300px]"
  style={wrapperStyle}
>
  <Card>
    <Input
      type="text"
      placeholder="Event name"
      bind:value={entry.summary}
      required
      class="text-xl font-semibold text-black dark:text-white mb-3 bg-transparent dark:bg-transparent border-none focus:ring-0 focus:border-none px-0 py-0.5 placeholder:text-gray-400 dark:placeholder:text-gray-500"
      on:focus={() => summaryEditing = true}
      on:blur={() => summaryEditing = false}
      on:change={() => {
        processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, summary: entry.summary } : e));
        commitUpdate({ ...entry, summary: entry.summary }, getOriginalRecurrenceStart(entry));
      }}
    />

    <div class="grid grid-cols-2 gap-3 mb-3">
      <Select
        class="text-s border-gray-200 h-8 py-0"
        size="sm"
        items={fieldsData.filter(f => f.field_id !== undefined).map(f => ({ value: f.field_id, name: f.name }))}
        bind:value={entry.field_id}
        required
        on:focus={() => fieldEditing = true}
        on:blur={() => fieldEditing = false}
        on:change={() => {
          processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, field_id: entry.field_id } : e));
          commitUpdate({ ...entry, field_id: entry.field_id }, getOriginalRecurrenceStart(entry));
        }}
      />
      <Select
        class="text-s border-gray-200 h-8 py-0"
        size="sm"
        items={teamsData.filter(t => t.team_id !== undefined).map(t => ({ value: t.team_id, name: t.name }))}
        bind:value={entry.team_id}
        required
        on:focus={() => teamEditing = true}
        on:blur={() => teamEditing = false}
        on:change={() => {
          processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, team_id: entry.team_id } : e));
          commitUpdate({ ...entry, team_id: entry.team_id }, getOriginalRecurrenceStart(entry));
        }}
      />
    </div>

    <Datepicker
      bind:value={selectedDate}
      on:select={handleDateChange}
      inputClass="text-s border-gray-200 h-8 py-0 mb-2"
      on:focus={() => dateEditing = true}
      on:blur={() => dateEditing = false}
    />
    
    <button class="text-gray-400 text-sm hover:text-gray-600 focus:outline-none text-left mb-2" on:click={() => showTimeInput = !showTimeInput}>
      {showTimeInput ? '− time' : '+ time'}
    </button>
    
    {#if showTimeInput}
      <Timepicker
        type="range"
        size="sm"
        icon={ClockSolid as any}
        value={selectedTimerange.time}
        endValue={selectedTimerange.endTime}
        on:select={handleTimeChange} 
      />
    {/if}

    <!-- trash icon -->
    <button class="absolute bottom-2 right-2 text-red-500 hover:text-red-600" on:click={handleDelete}>
      <TrashBinSolid />
    </button>
  </Card>
</div>