<script lang="ts">
  import EditableField from './EditableField.svelte';
  import { writable, type Writable, get } from 'svelte/store';
  import { onMount } from 'svelte';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { teams } from '../../stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '../../stores/fields';
  import type { Field } from '$lib/schemas/field';

  // Accept only UID from the clicked entry
  export let entryUid: string;
  
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
    const entry = currentEntries.find(entry => entry.uid === entryUid);

    if (entry) {

      infoCardForm.set({
        uid: entry.uid,
        team_id: entry.team_id || null,
        field_id: entry.field_id || null,
        starts: entry.dtstart.toISOString(),
        ends: entry.dtend.toISOString(),
        summary: entry.summary || '',
        schedule_entry_id: entry.schedule_entry_id
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
    <EditableField
      form={infoCardForm}
      errors={{}}
      name="summary"
      label=""
      type="text"
      view_mode_style="title"
      required={true}
    />
  </div>
  <div class="event-info-card-content">
    <div class="event-info-card-grid">
      <EditableField
        form={infoCardForm}
        errors={{}}
        name="field_id"
        label="Field"
        type="select"
        view_mode_style="pill"
        options={fieldsData
          .filter(field => field.field_id !== undefined)
          .map(field => ({ value: field.field_id, label: field.name }))}
        required={true}
      />
      <EditableField
        form={infoCardForm}
        errors={{}}
        name="team_id"
        label="Team"
        type="select"
        view_mode_style="normal"
        options={teamsData
          .filter(team => team.team_id !== undefined)
          .map(team => ({ value: team.team_id as number, label: team.name }))}
        required={true}
      />
    </div>
    <div class="event-info-card-grid">
      <EditableField
        form={infoCardForm}
        errors={{}}
        name="starts"
        label="Starts"
        type="text"
        placeholder="HH:MM"
        view_mode_style="normal"
        required={true}
      />
      <EditableField
        form={infoCardForm}
        errors={{}}
        name="ends"
        label="Ends"
        type="text"
        placeholder="HH:MM"
        view_mode_style="normal"
        required={true}
      />
    </div>
  </div>
</div>



