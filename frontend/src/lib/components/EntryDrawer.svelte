<!-- filepath: /Users/rohdee/Github/field-schedule/frontend/src/lib/components/EntryDrawer.svelte -->
<script lang="ts">
  import { Button, CloseButton, Heading, Datepicker, Timepicker, Helper, Label } from 'flowbite-svelte';
  import { CloseOutline, ClockSolid, TrashBinSolid } from 'flowbite-svelte-icons';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { deleteScheduleEntry } from '$lib/stores/schedules';
  import { computeDateUTC, currentDate } from '$lib/utils/dateUtils';
  import { commitUpdate, getOriginalRecurrenceStart } from '$lib/utils/calendarUtils';

  let { hidden = $bindable(true), entryUiId }: { 
    hidden: boolean; 
    entryUiId: string;
  } = $props();

  let selectedDate = $state<Date | null>(null);
  let selectedTimerange = $state({ time: '', endTime: '' });
  let isDeleting = $state(false);

  let entry = $derived($processedEntries.find(e => e.ui_id === entryUiId));
  
  $effect(() => {
    if (entry) {
      selectedDate = entry.dtstart;
      const oldStart = entry.dtstart.toISOString().slice(11,16);
      const oldEnd = entry.dtend.toISOString().slice(11,16);
      selectedTimerange = { time: oldStart, endTime: oldEnd };
    }
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
    hidden = true;
    isDeleting = false;
  }
</script>

<Heading tag="h5" class="mb-6 text-sm font-semibold uppercase">Edit Event Details</Heading>
<CloseButton onclick={() => (hidden = true)} class="absolute top-2.5 right-2.5 text-gray-400 hover:text-black dark:text-white" />

<div class="space-y-4">
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