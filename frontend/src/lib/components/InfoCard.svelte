<script lang="ts">
  import { Label, Input, Select } from 'flowbite-svelte';
  import { ClockSolid } from 'flowbite-svelte-icons';
  import { writable, type Writable, get } from 'svelte/store';
  import { onMount } from 'svelte';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { teams } from '../../stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '../../stores/fields';
  import type { Field } from '$lib/schemas/field';
  import { updateScheduleEntry } from '../../stores/schedules';
  import { Datepicker, Timepicker } from 'flowbite-svelte';
  import { formatDateAsYYYYMMDD } from '$lib/utils/dateUtils';

  export let entryUiId: string;

  const infoCardForm: Writable<Record<string, any>> = writable({});
  let teamsData: Team[] = [];
  let fieldsData: Field[] = [];
  let timeUpdateTimer: ReturnType<typeof setTimeout> | null = null;
  let originalStartTimeForRecurrence: string | null = null; // store original start for recurrence

  teams.subscribe(data => {
    teamsData = data;
  });

  fields.subscribe(() => {
    fieldsData = getFlattenedFields();
  });

  let selectedDate: Date | null = null;
  let selectedTimerange = { time: '', endTime: '' };

  function handleDateChange(event: any) {
    console.log('handleDateChange called', { event, selectedDate });
    const formValues = get(infoCardForm);
    if (!formValues.starts || !formValues.ends) return;
    
    const oldStartTime = formValues.starts.slice(11, 19);
    const oldEndTime = formValues.ends.slice(11, 19);
    const [sh, sm] = oldStartTime.split(':').map(Number);
    const [eh, em] = oldEndTime.split(':').map(Number);
    const dateToUse = selectedDate || new Date(event.target.value);
    const [year, month, day] = formatDateAsYYYYMMDD(dateToUse).split('-').map(Number);
    const newStartDate = new Date(Date.UTC(year, month - 1, day, sh, sm));
    const newEndDate = new Date(Date.UTC(year, month - 1, day, eh, em));
    const newStartIso = newStartDate.toISOString();
    const newEndIso = newEndDate.toISOString();
    const recId = originalStartTimeForRecurrence || formValues.recurrence_id;

    console.log('Date changed:', { newStartIso, newEndIso, selectedDate: dateToUse });
    updateScheduleEntry({ 
      uid: formValues.uid, 
      schedule_id: formValues.schedule_id, 
      dtstart: newStartDate, 
      dtend: newEndDate, 
      recurrence_id: recId 
    });
    infoCardForm.update(f => ({ ...f, starts: newStartIso, ends: newEndIso }));
  }

  interface TimepickerSelectEventDetail {
    time: string;
    endTime?: string;
  }

  interface TimepickerSelectEvent extends CustomEvent<TimepickerSelectEventDetail> {}

  function handleTimeChange(event: TimepickerSelectEvent) {
    const { time, endTime } = event.detail;
    if (!endTime) return;
    // Only update when the time input is complete  
    if (!time || !endTime) return;
    selectedTimerange = { time, endTime };
    if (!selectedDate) return;
    const [sh, sm] = time.split(':').map(Number);
    const [eh, em] = endTime.split(':').map(Number);
    const [year, month, day] = formatDateAsYYYYMMDD(selectedDate).split('-').map(Number);
    const newStartDate = new Date(Date.UTC(year, month - 1, day, sh, sm));
    const newEndDate = new Date(Date.UTC(year, month - 1, day, eh, em));
    const newStartIso = newStartDate.toISOString();
    const newEndIso = newEndDate.toISOString();
    const formValues = get(infoCardForm);
    const recId = originalStartTimeForRecurrence || formValues.recurrence_id;
    console.log('Time changed:', { newStartIso, newEndIso });
    
    if (timeUpdateTimer) {
      clearTimeout(timeUpdateTimer);
    }
    timeUpdateTimer = setTimeout(() => {
      updateScheduleEntry({ uid: formValues.uid, schedule_id: formValues.schedule_id, dtstart: newStartDate, dtend: newEndDate, recurrence_id: recId });
    }, 800);
    
    infoCardForm.update(f => ({ ...f, starts: newStartIso, ends: newEndIso }));
  }

  onMount(async () => {
    const currentEntries = get(processedEntries);
    const entry = currentEntries.find(entry => entry.ui_id === entryUiId);

    if (entry) {
      infoCardForm.set({
        uid: entry.uid,
        schedule_id: entry.schedule_id,
        team_id: entry.team_id || null,
        field_id: entry.field_id || null,
        starts: entry.dtstart.toISOString(),
        ends: entry.dtend.toISOString(),
        summary: entry.summary || '',
        recurrence_id: entry.recurrence_id
          ? (entry.recurrence_id instanceof Date
              ? entry.recurrence_id.toISOString()
              : entry.recurrence_id)
          : null,
        isRecurring: entry.isRecurring
      });
      selectedDate = entry.dtstart;
      const oldStart = entry.dtstart.toISOString().slice(11,16);
      const oldEnd = entry.dtend.toISOString().slice(11,16);
      selectedTimerange = { time: oldStart, endTime: oldEnd };

      // capture original start for recurrence logic
      if (entry.isRecurring) {
        originalStartTimeForRecurrence = entry.dtstart.toISOString();
      } else if (entry.recurrence_id) {
        originalStartTimeForRecurrence =
          entry.recurrence_id instanceof Date
            ? entry.recurrence_id.toISOString()
            : entry.recurrence_id;
      } else {
        originalStartTimeForRecurrence = null;
      }
    }
  });
</script>

<div
  role="button"
  tabindex="0"
  on:keydown={(e) => { if(e.key === "Enter" || e.key === " ") e.stopPropagation(); }}
  on:click|stopPropagation
  class="event-info-card"
>
  <div class="event-info-card-header">
    <Label class="space-y-2">
      <span>Summary</span>
      <Input
        type="text"
        size="sm"
        placeholder="Summary"
        bind:value={$infoCardForm.summary}
        required
        on:change={() => {
          console.log('Summary changed:', $infoCardForm.summary);
          updateScheduleEntry({ uid: $infoCardForm.uid, schedule_id: $infoCardForm.schedule_id, summary: $infoCardForm.summary, dtstart: new Date($infoCardForm.starts), dtend: new Date($infoCardForm.ends), recurrence_id: originalStartTimeForRecurrence ? new Date(originalStartTimeForRecurrence) : ($infoCardForm.recurrence_id ? new Date($infoCardForm.recurrence_id) : null) });
        }}
      />
    </Label>
  </div>
  <div class="event-info-card-content">
    <div class="event-info-card-grid">
      <Label>
        <span>Field</span>
        <Select
          class="mt-2"
          items={fieldsData.filter(f => f.field_id !== undefined).map(f => ({ value: f.field_id, name: f.name }))}
          bind:value={$infoCardForm.field_id}
          required
          on:change={() => {
            console.log('Field changed:', $infoCardForm.field_id);
            updateScheduleEntry({ uid: $infoCardForm.uid, schedule_id: $infoCardForm.schedule_id, field_id: $infoCardForm.field_id, dtstart: new Date($infoCardForm.starts), dtend: new Date($infoCardForm.ends), recurrence_id: originalStartTimeForRecurrence ? new Date(originalStartTimeForRecurrence) : ($infoCardForm.recurrence_id ? new Date($infoCardForm.recurrence_id) : null) });
          }}
        />
      </Label>
      <Label>
        <span>Team</span>
        <Select
          class="mt-2"
          items={teamsData.filter(t => t.team_id !== undefined).map(t => ({ value: t.team_id, name: t.name }))}
          bind:value={$infoCardForm.team_id}
          required
          on:change={() => {
            console.log('Team changed:', $infoCardForm.team_id);
            updateScheduleEntry({ uid: $infoCardForm.uid, schedule_id: $infoCardForm.schedule_id, team_id: $infoCardForm.team_id, dtstart: new Date($infoCardForm.starts), dtend: new Date($infoCardForm.ends), recurrence_id: originalStartTimeForRecurrence ? new Date(originalStartTimeForRecurrence) : ($infoCardForm.recurrence_id ? new Date($infoCardForm.recurrence_id) : null) });
          }}
        />
      </Label>
    </div>
    <div class="mt-4">
      <Label>
        <span>Date</span>
        <Datepicker
          bind:value={selectedDate}
          on:select={handleDateChange}
        />
      </Label>
    </div>
    <div class="event-info-card-grid">
      <Label>
        <span>Select Time Range:</span>
        <Timepicker
          icon={ClockSolid as any}
          type="range"
          value={selectedTimerange.time}
          endValue={selectedTimerange.endTime}
          on:select={handleTimeChange} 
        />
      </Label>
    </div>
  </div>
</div>