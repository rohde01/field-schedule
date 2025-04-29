<script lang="ts">
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell, Checkbox } from 'flowbite-svelte';
    import { teams } from '$lib/stores/teams';
    import { selectedSchedule } from '$lib/stores/schedules';
    import { constraints } from '$lib/stores/constraints';
    import type { Team } from '$lib/schemas/team';
    
    let teamItems: Team[] = [];
    let openTeam: number | null = null;

    function toggleRow(teamId: number) {
        openTeam = openTeam === teamId ? null : teamId;
    }
    
    teams.subscribe(value => {
        teamItems = value;
    });
    
    // Array to track selected team IDs
    let selectedTeamIds: number[] = [];
    
    // Handle checkbox changes
    function handleCheckboxChange(teamId: number, checked: boolean) {
        if (checked) {
            if (!selectedTeamIds.includes(teamId)) {
                selectedTeamIds = [...selectedTeamIds, teamId];
            }
        } else {
            selectedTeamIds = selectedTeamIds.filter(id => id !== teamId);
        }
        console.log('Selected team IDs:', selectedTeamIds);
    }
    
    // Handle "select all" checkbox
    function handleSelectAll(checked: boolean) {
        if (checked) {
            selectedTeamIds = teamItems
                .filter(team => team.team_id !== undefined)
                .map(team => team.team_id as number);
        } else {
            selectedTeamIds = [];
        }
        console.log('Selected team IDs:', selectedTeamIds);
    }
    
    $: allSelected = teamItems.length > 0 && selectedTeamIds.length === teamItems.length;

    // Auto-select team IDs from selectedSchedule entries
    $: if ($selectedSchedule) {
      selectedTeamIds = $selectedSchedule.schedule_entries
        .map(e => e.team_id)
        .filter((tid): tid is number => tid != null);
    }
</script>


  <Table shadow >
    <TableHead theadClass="text-base uppercase">
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
              <Table noborder={true} >
                <TableHead theadClass="text-xs uppercase">
                  <TableHeadCell class="text-xs"></TableHeadCell>
                  <TableHeadCell class="text-xs">Day</TableHeadCell>
                  <TableHeadCell class="text-xs">Start Time</TableHeadCell>
                  <TableHeadCell class="text-xs">Length</TableHeadCell>
                  <TableHeadCell class="text-xs">Field ID</TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                  {#each $constraints.filter(c => c.team_id === team.team_id) as c}
                    <TableBodyRow>
                      <TableBodyCell class="p-4!"><Checkbox /></TableBodyCell>
                      <TableBodyCell>{c.day_of_week}</TableBodyCell>
                      <TableBodyCell>{c.start_time}</TableBodyCell>
                      <TableBodyCell>{c.length}</TableBodyCell>
                      <TableBodyCell>{c.field_id}</TableBodyCell>
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
