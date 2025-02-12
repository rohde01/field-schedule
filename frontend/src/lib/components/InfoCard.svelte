<script lang="ts">
  import EditableField from './EditableField.svelte';
  import type { Writable } from 'svelte/store';

  export let infoCardForm: Writable<Record<string, any>>;
  export let editingEventPosition: { top: number; left: number };
  export let teams: any[];
  export let activeFields: any[];
  export let generateFieldOptions: (fields: any[]) => { value: number; label: string }[];
</script>

<div 
  role="button"
  tabindex="0"
  on:keydown={(e) => { if(e.key === "Enter" || e.key === " ") e.stopPropagation(); }}
  on:click|stopPropagation
  class="event-info-card"
  style="position: absolute; top: {editingEventPosition.top}px; left: {editingEventPosition.left}px;"
>
  <div class="event-info-card-header">
    <EditableField
      form={infoCardForm}
      errors={{}}
      name="team_id"
      label=""
      type="select"
      view_mode_style="title"
      options={teams
        .filter(team => team.team_id !== undefined)
        .map(team => ({ value: team.team_id, label: team.name }))}
      required={true}
    />
  </div>
  <div class="event-info-card-content">
    <div class="event-info-card-grid">
      <EditableField
        form={infoCardForm}
        errors={{}}
        name="field_id"
        label="Location"
        type="select"
        view_mode_style="pill"
        options={generateFieldOptions(activeFields)}
        required={true}
      />
      <EditableField
        form={infoCardForm}
        errors={{}}
        name="week_day"
        label="Day"
        type="select"
        view_mode_style="normal"
        options={['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
          .map((day, index) => ({ value: index, label: day }))}
        required={true}
      />
    </div>
    <div class="event-info-card-grid">
      <EditableField
        form={infoCardForm}
        errors={{}}
        name="start_time"
        label="Start Time"
        type="text"
        placeholder="HH:MM"
        view_mode_style="normal"
        required={true}
      />
      <EditableField
        form={infoCardForm}
        errors={{}}
        name="end_time"
        label="End Time"
        type="text"
        placeholder="HH:MM"
        view_mode_style="normal"
        required={true}
      />
    </div>
  </div>
</div>
