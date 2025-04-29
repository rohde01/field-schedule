<script lang="ts">
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell, Checkbox, Card } from 'flowbite-svelte';
    import { teams } from '$lib/stores/teams';
    import { constraints, selectedConstraints } from '$lib/stores/constraints';
    import type { Team } from '$lib/schemas/team';
    import type { Constraint } from '$lib/schemas/constraint';
    import { get } from 'svelte/store';
    import { fields, getFlattenedFields } from '$lib/stores/fields';
    import { Badge } from 'flowbite-svelte';
    
    let teamItems: Team[] = [];
    let openTeam: number | null = null;

    // Remove selections if constraints list changes
    constraints.subscribe(list => {
      selectedConstraints.update(current => current.filter(c => list.some(gc => gc.uid === c.uid)));
    });

    // Log selectedConstraints changes
    selectedConstraints.subscribe(list => console.log('selectedConstraints changed:', list));

    function toggleRow(teamId: number) {
        openTeam = openTeam === teamId ? null : teamId;
    }
    
    teams.subscribe(value => {
        teamItems = value;
    });
    
    // Array to track selected team IDs
    let selectedTeamIds: number[] = [];
    
    // Handle checkbox changes by updating selectedConstraints only
    function handleCheckboxChange(teamId: number, checked: boolean) {
        if (checked) {
            selectedConstraints.update(list => {
                const teamCons = get(constraints).filter(c => c.team_id === teamId);
                const newCons = teamCons.filter(tc => !list.some(lc => lc.uid === tc.uid));
                return [...list, ...newCons];
            });
        } else {
            selectedConstraints.update(list => list.filter(c => c.team_id !== teamId));
        }
    }
    
    // New handler for constraint checkbox changes
    function handleConstraintCheckboxChange(constraint: Constraint, checked: boolean) {
      selectedConstraints.update(list => {
        if (checked) {
          return list.some(c => c.uid === constraint.uid) ? list : [...list, constraint];
        }
        return list.filter(c => c.uid !== constraint.uid);
      });
    }

    // Handle "select all" by toggling all constraints
    function handleSelectAll(checked: boolean) {
        if (checked) {
            selectedConstraints.set(get(constraints));
        } else {
            selectedConstraints.set([]);
        }
    }
    
    $: allSelected = teamItems.length > 0 && selectedTeamIds.length === teamItems.length;

    // Derive selected teams from selected constraints
    $: {
      const teamIds = Array.from(new Set($selectedConstraints.map(c => c.team_id)));
      selectedTeamIds = teamIds;
    }

    // Return field name from id
    function getFieldName(fieldId: number | null | undefined): string {
      if (!fieldId) return '—';
      
      // Use the getFlattenedFields helper for all fields (main, half, and quarter)
      const flattenedFields = getFlattenedFields();
      const field = flattenedFields.find(f => f.field_id === fieldId);
      
      return field?.name ?? '—';
    }
    
    // Convert field size to badges labels
    function formatFieldSize(size: number): string[] {
      switch (size) {
        case 1000: return ['11v11'];
        case 500: return ['8v8', 'Half 11v11'];
        case 250: return ['5v5', 'Half 8v8', 'Quarter 11v11'];
        case 125: return ['3v3', 'Half 5v5', 'Quarter 8v8'];
        default: return [String(size)];
      }
    }
    
    // Convert length units (1 unit = 15min) to human-readable
    function formatLength(units: number): string {
      const mins = units * 15;
      const h = Math.floor(mins / 60);
      const m = mins % 60;
      let parts = [];
      if (h > 0) parts.push(h === 1 ? '1 hour' : `${h} hours`);
      if (m > 0) parts.push(m < 60 ? `${m} min` : '');
      if (parts.length === 0) return '0 min';
      return parts.join(' ');
    }

    const weekdayNames = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
    function formatDay(day: number | null | undefined): string {
      if (day == null) return '—';
      const idx = (day + 6) % 7;
      return weekdayNames[idx] || '—';
    }
</script>


  <Card size="xl" class="mb-4 h-[24rem] w-full overflow-hidden">
    <div class="h-full overflow-y-auto">
      <Table shadow >
        <TableHead>
          <TableHeadCell>
            <Checkbox checked={allSelected} on:change={(e) => {
              if (e.target && 'checked' in e.target) {
                handleSelectAll((e.target as HTMLInputElement).checked);
              }
            }} />
          </TableHeadCell>
          <TableHeadCell>Name</TableHeadCell>
          <TableHeadCell>Year</TableHeadCell>
          <TableHeadCell>Level</TableHeadCell>
        </TableHead>
        <TableBody tableBodyClass="divide-y">
          {#each teamItems as team}
            <TableBodyRow on:click={() => toggleRow(team.team_id!)}>
              <TableBodyCell class="p-4!">
                <Checkbox
                  checked={selectedTeamIds.includes(team.team_id!)}
                  on:change={(e) => handleCheckboxChange(team.team_id!, (e.target as HTMLInputElement).checked)}
                />
              </TableBodyCell>
              <TableBodyCell>{team.name}</TableBodyCell>
              <TableBodyCell>{team.year}</TableBodyCell>
              <TableBodyCell>{team.level}</TableBodyCell>
            </TableBodyRow>
            {#if openTeam === team.team_id}
              <TableBodyRow>
                <TableBodyCell colspan={5} class="p-0">
                  <Table noborder={true} divClass="relative overflow-x-auto pl-8">
                    <TableHead theadClass="text-xs uppercase">
                      <TableHeadCell class="text-xs"></TableHeadCell>
                      <TableHeadCell class="text-xs">Day</TableHeadCell>
                      <TableHeadCell class="text-xs">Start Time</TableHeadCell>
                      <TableHeadCell class="text-xs">Field ID</TableHeadCell>
                      <TableHeadCell class="text-xs">Length</TableHeadCell>
                      <TableHeadCell class="text-xs">Required Cost</TableHeadCell>
                    </TableHead>
                    <TableBody tableBodyClass="divide-y">
                      {#each $constraints.filter(c => c.team_id === team.team_id) as c}
                        <TableBodyRow>
                          <TableBodyCell class="p-4!">
                            <Checkbox
                              checked={$selectedConstraints.some(sc => sc.uid === c.uid)}
                              on:change={(e) => handleConstraintCheckboxChange(c, (e.target as HTMLInputElement).checked)}
                            />
                          </TableBodyCell>
                          <TableBodyCell>{formatDay(c.day_of_week)}</TableBodyCell>
                          <TableBodyCell>{c.start_time ?? '—'}</TableBodyCell>
                          <TableBodyCell>
                            {#if c.field_id}
                              <Badge border color="blue" class="mr-2">{getFieldName(c.field_id)}</Badge>
                            {:else}
                              —
                            {/if}
                          </TableBodyCell>
                          <TableBodyCell>{formatLength(c.length)}</TableBodyCell>
                          <TableBodyCell>
                            {#if c.required_cost}
                              {#each formatFieldSize(c.required_cost) as size}
                                <Badge border color="green" class="mr-2">{size}</Badge>
                              {/each}
                            {:else}
                              —
                            {/if}
                          </TableBodyCell>
                        </TableBodyRow>
                      {/each}
                    </TableBody>
                  </Table>
                </TableBodyCell>
              </TableBodyRow>
            {/if}
          {/each}
        </TableBody>
      </Table>
    </div>
  </Card>
