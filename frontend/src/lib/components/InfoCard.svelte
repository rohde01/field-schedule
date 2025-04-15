<script lang="ts">
  import EditableField from './EditableField.svelte';
  import type { Writable } from 'svelte/store';
  import { deleteScheduleEntry } from '$stores/schedules';
  import { infoCardStore } from '$lib/utils/infoCardUtils';

  export let infoCardForm: Writable<Record<string, any>>;
  export let editingEventPosition: { top: number; left: number };
  export let teams: any[];
  export let activeFields: any[];
  export let generateFieldOptions: (fields: any[]) => { value: number; label: string }[];
  
  let showConfirmModal = false;

  async function handleDelete() {
    showConfirmModal = true;
  }
  
  async function confirmDelete() {
    // Delete schedule entry
    const entryId = $infoCardForm.schedule_entry_id;
    const success = await deleteScheduleEntry(entryId);
    
    if (success) {
      infoCardStore.closeInfoCard();
    }
    showConfirmModal = false;
  }
  
  function cancelDelete() {
    showConfirmModal = false;
  }
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
  
  <button 
    type="button" 
    class="btn-trash" 
    aria-label="Delete entry" 
    on:click|stopPropagation={handleDelete}
    tabindex="-1"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  </button>
</div>

{#if showConfirmModal}
  <div 
    class="modal-overlay" 
    on:click|self={cancelDelete}
    on:keydown={(e) => {
      if (e.key === 'Escape') cancelDelete();
    }}
    role="dialog"
    aria-labelledby="modal-title"
    aria-describedby="modal-description"
  >
    <div class="modal-container">
      <h2 id="modal-title" class="modal-title">Confirm Deletion</h2>
      <p id="modal-description">
        Are you sure you want to delete this schedule entry?
      </p>
      
      <div class="modal-actions">
        <button class="btn-secondary" on:click={cancelDelete}>Cancel</button>
        <button class="btn-danger" on:click={confirmDelete}>Delete</button>
      </div>
    </div>
  </div>
{/if}


