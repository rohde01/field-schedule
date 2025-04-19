<script lang="ts">
  import EditableField from './EditableField.svelte';
  import { writable, type Writable, get } from 'svelte/store';
  import { onMount } from 'svelte';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { formatDateTimeUTC } from '$lib/utils/dateUtils';
  import { teams } from '../../stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '../../stores/fields';
  import type { Field } from '$lib/schemas/field';
  import { updateScheduleEntry } from '../../stores/schedules';

  // Accept only UiId from the clicked entry
  export let entryUiId: string;
  
  // Create an internal writable store for the form state
  const infoCardForm: Writable<Record<string, any>> = writable({});
  
  // Track previous IDs for change detection
  let prevTeamId: number | null | undefined;
  let prevFieldId: number | null | undefined;
  
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
        starts: formatDateTimeUTC(entry.dtstart),
        ends: formatDateTimeUTC(entry.dtend),
        summary: entry.summary,
        recurrence_id: entry.recurrence_id || null,
        isRecurring: entry.isRecurring
      });
  
      // Initialize previous values
      prevTeamId = entry.team_id;
      prevFieldId = entry.field_id;
    }
  });
  
  // Subscribe to form changes to update schedule entry on team/field change
  infoCardForm.subscribe(form => {
    if (prevTeamId !== undefined && form.team_id !== prevTeamId) {
      updateScheduleEntry({ uid: form.uid, schedule_id: form.schedule_id, team_id: form.team_id, recurrence_id: form.isRecurring ? form.starts : form.recurrence_id });
    }
    if (prevFieldId !== undefined && form.field_id !== prevFieldId) {
      updateScheduleEntry({ uid: form.uid, schedule_id: form.schedule_id, field_id: form.field_id, recurrence_id: form.isRecurring ? form.starts : form.recurrence_id });
    }
    prevTeamId = form.team_id;
    prevFieldId = form.field_id;
  });

  // Handle form submission
  function handleSubmit() {
    const formData = get(infoCardForm);
    updateScheduleEntry({ 
      uid: formData.uid, 
      schedule_id: formData.schedule_id, 
      team_id: formData.team_id, 
      field_id: formData.field_id,
      recurrence_id: formData.isRecurring ? formData.starts : formData.recurrence_id 
    });
  }
</script>

<div 
  class="p-4 rounded-lg shadow-lg bg-white"
  role="button"
  tabindex="0"
  on:keydown={(e) => { if(e.key === "Enter" || e.key === " ") e.stopPropagation(); }}
  on:click|stopPropagation
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



