<!-- filepath: /Users/rohdee/Github/field-schedule/frontend/src/lib/components/EntryDrawer.svelte -->
<script lang="ts">
  import { Button, CloseButton, Heading, Datepicker, Timepicker, Helper, Label, Input, Select } from 'flowbite-svelte';
  import { CloseOutline, ClockSolid, TrashBinSolid } from 'flowbite-svelte-icons';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { deleteScheduleEntry } from '$lib/stores/schedules';
  import { computeDateUTC, currentDate } from '$lib/utils/dateUtils';
  import { commitUpdate, getOriginalRecurrenceStart } from '$lib/utils/calendarUtils';
  import { teams } from '$lib/stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '$lib/stores/fields';
  import type { FlattenedField } from '$lib/schemas/field';

  let { hidden = $bindable(true), entryUiId }: { 
    hidden: boolean; 
    entryUiId: string;
  } = $props();

  let selectedDate = $state<Date | null>(null);
  let selectedTimerange = $state({ time: '', endTime: '' });
  let isDeleting = $state(false);
  let teamsData = $state<Team[]>([]);
  let fieldsData = $state<FlattenedField[]>([]);

  let entry = $derived($processedEntries.find(e => e.ui_id === entryUiId));
  
  $effect(() => {
    if (entry) {
      selectedDate = entry.dtstart;
      const oldStart = entry.dtstart.toISOString().slice(11,16);
      const oldEnd = entry.dtend.toISOString().slice(11,16);
      selectedTimerange = { time: oldStart, endTime: oldEnd };
    }
  });

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
    currentDate.set(newStart);
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
    if (!entry) return;
    isDeleting = true;
    const recDateStr = getOriginalRecurrenceStart(entry);
    const recDate = recDateStr ? new Date(recDateStr) : null;
    deleteScheduleEntry(entry.uid, entry.schedule_id!, recDate);
    isDeleting = false;
  }
</script>

<Heading tag="h5" class="mb-6 text-sm font-semibold uppercase">Edit Event Details</Heading>
<CloseButton onclick={() => (hidden = true)} class="absolute top-2.5 right-2.5 text-gray-400 hover:text-black dark:text-white" />

<div class="space-y-4">
  {#if entry}
    <Label class="space-y-2">
      <span>Event Name</span>
      <Input
        type="text"
        placeholder="Event name"
        bind:value={entry.summary}
        required
        on:change={() => {
          processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, summary: entry!.summary } : e));
          commitUpdate({ ...entry, summary: entry!.summary }, getOriginalRecurrenceStart(entry));
        }}
      />
    </Label>

    <div class="grid grid-cols-2 gap-3">
      <Label class="space-y-2">
        <span>Field</span>
        <Select
          items={fieldsData.filter(f => f.field_id !== undefined).map(f => ({ value: f.field_id, name: f.name }))}
          bind:value={entry.field_id}
          required
          on:change={() => {
            processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, field_id: entry!.field_id } : e));
            commitUpdate({ ...entry, field_id: entry!.field_id }, getOriginalRecurrenceStart(entry));
          }}
        />
      </Label>
      <Label class="space-y-2">
        <span>Team</span>
        <Select
          items={teamsData.filter(t => t.team_id !== undefined).map(t => ({ value: t.team_id, name: t.name }))}
          bind:value={entry.team_id}
          required
          on:change={() => {
            processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, team_id: entry!.team_id } : e));
            commitUpdate({ ...entry, team_id: entry!.team_id }, getOriginalRecurrenceStart(entry));
          }}
        />
      </Label>
    </div>

    <Label class="space-y-2">
      <span>Category</span>
      <Select
        items={[
          { value: "Training", name: "Training" },
          { value: "Match", name: "Match" },
          { value: "Event", name: "Event" }
        ]}
        bind:value={entry.categories[0]}
        required
        placeholder="Select category"
        on:change={() => {
          processedEntries.update(es => es.map(e => e.ui_id === entryUiId ? { ...e, categories: [entry!.categories[0]] } : e));
          commitUpdate({ ...entry, categories: [entry!.categories[0]] }, getOriginalRecurrenceStart(entry));
        }}
      />
    </Label>

    <Label class="space-y-2">
      <span>Date</span>
      <Datepicker
        bind:value={selectedDate}
        on:select={handleDateChange}
        inputClass="text-s border-gray-200 h-10 py-2"
      />
    </Label>

    <Label class="space-y-2">
      <span>Time</span>
      <Timepicker
        type="range"
        size="sm"
        icon={ClockSolid as any}
        value={selectedTimerange.time}
        endValue={selectedTimerange.endTime}
        on:select={handleTimeChange} 
      />
    </Label>
  {/if}

  <div class="bottom-0 left-0 flex w-full justify-center space-x-4 pb-4 md:absolute md:px-4">
    <Button color="red" class="w-full" onclick={handleDelete} disabled={isDeleting}>
      <TrashBinSolid class="me-2" />
      {isDeleting ? 'Deleting...' : 'Delete Event'}
    </Button>
    <Button color="alternative" class="w-full" onclick={() => (hidden = true)}>
      <CloseOutline /> Close
    </Button>
  </div>
</div>