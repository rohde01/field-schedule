<!-- filepath: /Users/rohdee/Github/field-schedule/frontend/src/lib/components/EntryDrawer.svelte -->
<script lang="ts">
  import { Button, CloseButton, Heading, Datepicker, Timepicker, Label, Input, Select, Checkbox } from 'flowbite-svelte';
  import { CloseOutline, ClockSolid, TrashBinSolid } from 'flowbite-svelte-icons';
  import { processedEntries, parseRecurrenceFrequency, createRecurrenceRule, canEditRecurrence } from '$lib/utils/calendarUtils';
  import { deleteScheduleEntry } from '$lib/stores/schedules';
  import { currentDate } from '$lib/utils/dateUtils';
  import { getOriginalRecurrenceStart } from '$lib/utils/calendarUtils';
  import { teams } from '$lib/stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '$lib/stores/fields';
  import type { FlattenedField } from '$lib/schemas/field';
  import { applyEntryChanges, updateEntryField, updateEntryDate, updateEntryTimeRange, toggleRecurrence } from '$lib/utils/entryEditUtils';
  import RecurringDialog from '$lib/components/Recurring.svelte';
  import DeleteRecurringDialog from '$lib/components/DeleteRecurringDialog.svelte';
  import { handleRecurringDelete } from '$lib/utils/deleteRecurringUtils';

  let { hidden = $bindable(true), entryUiId }: { 
    hidden: boolean; 
    entryUiId: string;
  } = $props();

  let selectedDate = $state<Date | null>(null);
  let selectedTimerange = $state({ time: '', endTime: '' });
  let isDeleting = $state(false);
  let teamsData = $state<Team[]>([]);
  let fieldsData = $state<FlattenedField[]>([]);
  let hasRecurrence = $state(false);
  let recurrenceFrequency = $state('WEEKLY');

  let entry = $derived($processedEntries.find(e => e.ui_id === entryUiId));
  
  $effect(() => {
    if (entry) {
      selectedDate = entry.dtstart;
      selectedTimerange = { time: entry.start_time, endTime: entry.end_time };
      if (canEditRecurrence(entry)) {
        hasRecurrence = !!entry.recurrence_rule;
        recurrenceFrequency = parseRecurrenceFrequency(entry.recurrence_rule);
      }
    }
  });

  teams.subscribe(data => { teamsData = data; });
  fields.subscribe(() => { fieldsData = getFlattenedFields(); });

  function handleDateChange(event: any) {
    if (!entry) return;
    const date = selectedDate || new Date(event.target.value);
    updateEntryDate(entryUiId, date);
    currentDate.set(date);
  }

  function handleTimeChange(event: CustomEvent<{ time: string; endTime?: string }>) {
    if (!entry || !selectedDate) return;
    const { time, endTime: rawEndTime } = event.detail; if (!rawEndTime) return;
    updateEntryTimeRange(entryUiId, time, rawEndTime);
  }

  function handleDelete() {
    if (!entry) return;
    isDeleting = true;
    handleRecurringDelete(entry);
    isDeleting = false;
  }

  function handleRecurrenceToggle() {
    if (!entry) return;
    hasRecurrence = !hasRecurrence;
    const recurrenceRule = hasRecurrence ? createRecurrenceRule(recurrenceFrequency) : null;
    toggleRecurrence(entryUiId, hasRecurrence, recurrenceRule);
  }

  function handleRecurrenceFrequencyChange() {
    if (!entry || !hasRecurrence) return;
    const recurrenceRule = createRecurrenceRule(recurrenceFrequency);
    toggleRecurrence(entryUiId, true, recurrenceRule);
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
        on:change={() => updateEntryField(entryUiId, 'summary', entry.summary)}
      />
    </Label>

    <div class="grid grid-cols-2 gap-3">
      <Label class="space-y-2">
        <span>Field</span>
        <Select
          items={fieldsData.filter(f => f.field_id !== undefined).map(f => ({ value: f.field_id, name: f.name }))}
          bind:value={entry.field_id}
          required
          on:change={() => updateEntryField(entryUiId, 'field_id', entry.field_id)}
        />
      </Label>
      <Label class="space-y-2">
        <span>Team</span>
        <Select
          items={teamsData.filter(t => t.team_id !== undefined).map(t => ({ value: t.team_id, name: t.name }))}
          bind:value={entry.team_id}
          required
          on:change={() => updateEntryField(entryUiId, 'team_id', entry.team_id)}
        />
      </Label>
    </div>

    <Label class="space-y-2">
      <span>Category</span>
      <Select
        items={[{ value: 'Training', name: 'Training' }, { value: 'Match', name: 'Match' }, { value: 'Event', name: 'Event' }]}
        bind:value={entry.categories[0]}
        required
        placeholder="Select category"
        on:change={() => applyEntryChanges(entryUiId, { categories: [entry.categories[0]] })}
      />
    </Label>

    <Label class="space-y-2">
      <span>Date</span>
      <Datepicker bind:value={selectedDate} on:select={handleDateChange} inputClass="text-s border-gray-200 h-10 py-2" />
    </Label>

    <Label class="space-y-2">
      <span>Time</span>
      <Timepicker type="range" size="sm" icon={ClockSolid as any} value={selectedTimerange.time} endValue={selectedTimerange.endTime} on:select={handleTimeChange} />
    </Label>

    {#if canEditRecurrence(entry)}
      <div class="space-y-3 border-t pt-4">
        <div class="flex items-center space-x-3">
          <Checkbox checked={hasRecurrence} on:click={handleRecurrenceToggle} />
          <span class="text-sm font-medium">Repeats {hasRecurrence ? recurrenceFrequency.toLowerCase() : ''}</span>
        </div>
        {#if hasRecurrence}
          <Label class="space-y-2">
            <span>Frequency</span>
            <Select
              items={[{ value: 'DAILY', name: 'Daily' }, { value: 'WEEKLY', name: 'Weekly' }, { value: 'MONTHLY', name: 'Monthly' }]}
              bind:value={recurrenceFrequency}
              on:change={handleRecurrenceFrequencyChange}
            />
          </Label>
        {/if}
      </div>
    {/if}
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
<RecurringDialog />
<DeleteRecurringDialog />