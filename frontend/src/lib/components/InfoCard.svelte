<script lang="ts">
  import { Label, Input, Select } from 'flowbite-svelte';
  import { writable, type Writable, get } from 'svelte/store';
  import { onMount } from 'svelte';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { teams } from '../../stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '../../stores/fields';
  import type { Field } from '$lib/schemas/field';
  import { updateScheduleEntry } from '../../stores/schedules';

  // Accept only UiId from the clicked entry
  export let entryUiId: string;
  
  // Create an internal writable store for the form state
  const infoCardForm: Writable<Record<string, any>> = writable({});
  
  // Get teams and fields from the stores
  let teamsData: Team[] = [];
  let fieldsData: Field[] = [];
  
  // Subscribe to stores
  teams.subscribe(data => {
    teamsData = data;
  });
  
  // Use getFlattenedFields function to get all fields including subfields
  fields.subscribe(() => {
    fieldsData = getFlattenedFields();
  });
  
  // Initialize form data based on entry UID
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
        recurrence_id: entry.recurrence_id || null,
        isRecurring: entry.isRecurring
      });
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
        on:change={() => updateScheduleEntry({ uid: $infoCardForm.uid, schedule_id: $infoCardForm.schedule_id, summary: $infoCardForm.summary, recurrence_id: $infoCardForm.isRecurring ? $infoCardForm.starts : $infoCardForm.recurrence_id })}
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
          on:change={() => updateScheduleEntry({ uid: $infoCardForm.uid, schedule_id: $infoCardForm.schedule_id, field_id: $infoCardForm.field_id, recurrence_id: $infoCardForm.isRecurring ? $infoCardForm.starts : $infoCardForm.recurrence_id })}
        />
      </Label>
      <Label>
        <span>Team</span>
        <Select
          class="mt-2"
          items={teamsData.filter(t => t.team_id !== undefined).map(t => ({ value: t.team_id, name: t.name }))}
          bind:value={$infoCardForm.team_id}
          required
          on:change={() => updateScheduleEntry({ uid: $infoCardForm.uid, schedule_id: $infoCardForm.schedule_id, team_id: $infoCardForm.team_id, recurrence_id: $infoCardForm.isRecurring ? $infoCardForm.starts : $infoCardForm.recurrence_id })}
        />
      </Label>
    </div>
    <div class="event-info-card-grid">
      <Label>
        <span>Starts</span>
        <Input class="mb-6 mt-2" size="sm" disabled value={$infoCardForm.starts} />
      </Label>
      <Label>
        <span>Ends</span>
        <Input class="mb-6 mt-2" size="sm" disabled value={$infoCardForm.ends} />
      </Label>
    </div>
  </div>
</div>