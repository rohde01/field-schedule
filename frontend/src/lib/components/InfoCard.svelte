<script lang="ts">
  import { Label, Input, Select, Datepicker, Timepicker } from 'flowbite-svelte';
  import { TrashBinSolid, ClockSolid } from 'flowbite-svelte-icons';
  import { writable, type Writable, get } from 'svelte/store';
  import { onMount } from 'svelte';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { teams } from '../../stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '../../stores/fields';
  import type { Field } from '$lib/schemas/field';
  import { updateScheduleEntry, deleteScheduleEntry } from '../../stores/schedules';
  import { formatDateAsYYYYMMDD } from '$lib/utils/dateUtils';

  export let entryUiId: string;

  const infoCardForm: Writable<Record<string, any>> = writable({});
  let teamsData: Team[] = [];
  let fieldsData: Field[] = [];
  let timeUpdateTimer: ReturnType<typeof setTimeout> | null = null;
  let originalStartTimeForRecurrence: string | null = null; // store original start for recurrence
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

  function handleDelete() {
    isDeleting = true;
    const formValues = get(infoCardForm);
    const recDate = originalStartTimeForRecurrence
      ? new Date(originalStartTimeForRecurrence)
      : formValues.recurrence_id
        ? new Date(formValues.recurrence_id)
        : null;
    deleteScheduleEntry(formValues.uid, formValues.schedule_id, recDate);
    isDeleting = false;
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
  class="event-info-card max-w-[300px] relative"
>
  <div class="event-info-card-header mb-1">
    <Label class="space-y-0">
      <Input
        type="text"
        placeholder="Event name"
        bind:value={$infoCardForm.summary}
        required
        class="text-xl font-semibold text-black mt-0 bg-transparent border-none focus:ring-0 focus:border-none px-2 py-0.5 placeholder:text-gray-300"
        on:focus={() => summaryEditing = true}
        on:blur={() => summaryEditing = false}
        on:change={() => {
          console.log('Summary changed:', $infoCardForm.summary);
          updateScheduleEntry({ uid: $infoCardForm.uid, schedule_id: $infoCardForm.schedule_id, summary: $infoCardForm.summary, dtstart: new Date($infoCardForm.starts), dtend: new Date($infoCardForm.ends), recurrence_id: originalStartTimeForRecurrence ? new Date(originalStartTimeForRecurrence) : ($infoCardForm.recurrence_id ? new Date($infoCardForm.recurrence_id) : null) });
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
            bind:value={$infoCardForm.field_id}
            required
            on:focus={() => fieldEditing = true}
            on:blur={() => fieldEditing = false}
            on:change={() => {
              console.log('Field changed:', $infoCardForm.field_id);
              updateScheduleEntry({ uid: $infoCardForm.uid, schedule_id: $infoCardForm.schedule_id, field_id: $infoCardForm.field_id, dtstart: new Date($infoCardForm.starts), dtend: new Date($infoCardForm.ends), recurrence_id: originalStartTimeForRecurrence ? new Date(originalStartTimeForRecurrence) : ($infoCardForm.recurrence_id ? new Date($infoCardForm.recurrence_id) : null) });
            }}
          />
        </Label>
        <Label class="space-y-2">
          <Select
            class="mt-2 text-s border-gray-200 bg-transparent h-8 py-0"
            size="sm"
            items={teamsData.filter(t => t.team_id !== undefined).map(t => ({ value: t.team_id, name: t.name }))}
            bind:value={$infoCardForm.team_id}
            required
            on:focus={() => teamEditing = true}
            on:blur={() => teamEditing = false}
            on:change={() => {
              console.log('Team changed:', $infoCardForm.team_id);
              updateScheduleEntry({ uid: $infoCardForm.uid, schedule_id: $infoCardForm.schedule_id, team_id: $infoCardForm.team_id, dtstart: new Date($infoCardForm.starts), dtend: new Date($infoCardForm.ends), recurrence_id: originalStartTimeForRecurrence ? new Date(originalStartTimeForRecurrence) : ($infoCardForm.recurrence_id ? new Date($infoCardForm.recurrence_id) : null) });
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