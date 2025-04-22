<script lang="ts">
  import { Label, Input, Select, Datepicker, Timepicker } from 'flowbite-svelte';
  import { TrashBinSolid, ClockSolid } from 'flowbite-svelte-icons';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { teams } from '../../stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '../../stores/fields';
  import type { Field } from '$lib/schemas/field';
  import { deleteScheduleEntry } from '../../stores/schedules';
  import { computeDateUTC } from '$lib/utils/dateUtils';
  import { commitUpdate, getOriginalRecurrenceStart } from '$lib/utils/calendarUtils';

  export let entryUiId: string;

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
  role="button"
  tabindex="0"
  on:keydown={(e) => { if(e.key === "Enter" || e.key === " ") e.stopPropagation(); }}
  on:click|stopPropagation
  class="event-info-card max-w-[300px] relative"
>
  <div class="event-info-card-header mb-1">
    <Label class="space-y-0">
      <Input
        type="text"
        placeholder="Event name"
        bind:value={entry.summary}
        required
        class="text-xl font-semibold text-black mt-0 bg-transparent border-none focus:ring-0 focus:border-none px-2 py-0.5 placeholder:text-gray-300"
        on:focus={() => summaryEditing = true}
        on:blur={() => summaryEditing = false}
        on:change={() => {
          processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, summary: entry.summary } : e));
          commitUpdate({ ...entry, summary: entry.summary }, getOriginalRecurrenceStart(entry));
        }}
      />
    </Label>
  </div>
  <div class="event-info-card-content">
    <div class="flex flex-col space-y-3">
      <div class="grid grid-cols-2 gap-3">
        <Label class="space-y-2">
          <Select
            class="mt-2 text-s border-gray-200 bg-transparent h-8 py-0"
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
        </Label>
        <Label class="space-y-2">
          <Select
            class="mt-2 text-s border-gray-200 bg-transparent h-8 py-0"
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
        </Label>
      </div>

      <div class="flex flex-col space-y-2">
        <Label class="mt-2">
          <Datepicker
            bind:value={selectedDate}
            on:select={handleDateChange}
            inputClass="mt-2 text-s border-gray-200 h-8 py-0"
            on:focus={() => dateEditing = true}
            on:blur={() => dateEditing = false}
          />
        </Label>
        
        <button class="text-gray-400 text-[16px] mt-1 hover:text-gray-600 focus:outline-none text-left pl-1" on:click={() => showTimeInput = !showTimeInput}>
          {showTimeInput ? '− time' : '+ time'}
        </button>
        
        {#if showTimeInput}
          <div class="mt-2 bg-transparent">
            <Label class="space-y-2 ">
              <Timepicker
                type="range"
                size="sm"
                icon={ClockSolid as any}
                value={selectedTimerange.time}
                endValue={selectedTimerange.endTime}
                on:select={handleTimeChange} 
              />
            </Label>
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- trash icon -->
  <button class="absolute bottom-2 right-2 text-red-500 hover:text-red-600" on:click={handleDelete}>
    <TrashBinSolid />
  </button>
</div>