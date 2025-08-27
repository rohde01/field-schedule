<script lang="ts">
  import { Input, Select, Drawer } from 'flowbite-svelte';
  import { TrashBinSolid } from 'flowbite-svelte-icons';
  import { processedEntries } from '$lib/utils/calendarUtils';
  import { teams } from '../../../lib/stores/teams';
  import type { Team } from '$lib/schemas/team';
  import { fields, getFlattenedFields } from '../../../lib/stores/fields';
  import type { FlattenedField } from '$lib/schemas/field';
  import { deleteScheduleEntry } from '../../../lib/stores/schedules';
  import { getOriginalRecurrenceStart } from '$lib/utils/calendarUtils';
  import { Card } from 'flowbite-svelte';
  import { onMount } from 'svelte';
  import EntryDrawer from '$lib/components/EntryDrawer.svelte';
  import { updateEntryField, applyEntryChanges } from '$lib/utils/entryEditUtils';
  import RecurringDialog from '$lib/components/Recurring.svelte';
  import DeleteRecurringDialog from '$lib/components/DeleteRecurringDialog.svelte';
  import { handleRecurringDelete } from '$lib/utils/deleteRecurringUtils';

  let { entryUiId }: { entryUiId: string } = $props();

  let wrapperElement: HTMLDivElement;
  let wrapperStyle = $state('');
  const cardWidth = 300;
  const offset = 20;

  onMount(() => {
    if (wrapperElement) {
      const parent = wrapperElement.parentElement as HTMLElement;
      const rect = parent.getBoundingClientRect();
      const spaceRight = window.innerWidth - (rect.left + rect.width);
      wrapperStyle = spaceRight > cardWidth + offset
        ? `top:0px; left:${rect.width + offset}px;`
        : `top:0px; left:-${cardWidth + offset}px;`;
    }
  });

  let entry = $derived($processedEntries.find(e => e.ui_id === entryUiId));

  let teamsData = $state<Team[]>([]);
  let fieldsData = $state<FlattenedField[]>([]);
  let summaryEditing = false;
  let fieldEditing = false;
  let teamEditing = false;
  let hiddenDrawer = $state(true);
  let isDeleting = $state(false);

  teams.subscribe(data => { teamsData = data; });
  fields.subscribe(() => { fieldsData = getFlattenedFields(); });

  function handleDelete() {
    if (!entry) return;
    isDeleting = true;
    handleRecurringDelete(entry);
    isDeleting = false;
  }
</script>

<div
  bind:this={wrapperElement}
  role="button"
  tabindex="0"
  onkeydown={(e) => { if(e.key === 'Enter' || e.key === ' ') e.stopPropagation(); }}
  onclick={(e) => e.stopPropagation()}
  class="absolute z-20 w-[300px]"
  style={wrapperStyle}
>
  <Card>
    {#if entry}
      <Input
        type="text"
        placeholder="Event name"
        bind:value={entry.summary}
        required
        class="text-xl font-semibold text-black dark:text-white mb-3 bg-transparent dark:bg-transparent border-none focus:ring-0 focus:border-none px-0 py-0.5 placeholder:text-gray-400 dark:placeholder:text-gray-500"
        on:focus={() => summaryEditing = true}
        on:blur={() => summaryEditing = false}
        on:change={() => updateEntryField(entryUiId, 'summary', entry.summary)}
      />

      <div class="grid grid-cols-2 gap-3 mb-3">
        <Select
          class="text-s border-gray-200 h-8 py-0"
          size="sm"
          items={fieldsData.filter(f => f.field_id !== undefined).map(f => ({ value: f.field_id, name: f.name }))}
          bind:value={entry.field_id}
          required
          on:focus={() => fieldEditing = true}
            on:blur={() => fieldEditing = false}
          on:change={() => updateEntryField(entryUiId, 'field_id', entry.field_id)}
        />
        <Select
          class="text-s border-gray-200 h-8 py-0"
          size="sm"
          items={teamsData.filter(t => t.team_id !== undefined).map(t => ({ value: t.team_id, name: t.name }))}
          bind:value={entry.team_id}
          required
          on:focus={() => teamEditing = true}
          on:blur={() => teamEditing = false}
          on:change={() => updateEntryField(entryUiId, 'team_id', entry.team_id)}
        />
      </div>

      <div class="mb-3">
        <Select
          class="text-s border-gray-200 h-8 py-0"
          size="sm"
          items={[{ value: 'Training', name: 'Training' }, { value: 'Match', name: 'Match' }, { value: 'Event', name: 'Event' }]}
          bind:value={entry.categories[0]}
          required
          placeholder="Select category"
          on:change={() => applyEntryChanges(entryUiId, { categories: [entry.categories[0]] })}
        />
      </div>

      <button class="text-gray-400 text-sm hover:text-gray-600 focus:outline-none text-left mb-2" onclick={() => hiddenDrawer = false}>
        + expand
      </button>

      <button class="absolute bottom-2 right-2 text-red-500 hover:text-red-600" onclick={handleDelete} disabled={isDeleting}>
        <TrashBinSolid />
      </button>
    {/if}
  </Card>
</div>

<Drawer placement="right" bind:hidden={hiddenDrawer}>
  <EntryDrawer bind:hidden={hiddenDrawer} {entryUiId} />
</Drawer>
<RecurringDialog />
<DeleteRecurringDialog />