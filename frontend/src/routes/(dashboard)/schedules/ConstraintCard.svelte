<script lang="ts">
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell, Checkbox } from 'flowbite-svelte';
    import { teams } from '$lib/stores/teams';
    import { selectedSchedule } from '$lib/stores/schedules';
    import type { Team } from '$lib/schemas/team';
    
    // Get a numeric value from the UXX year format for sorting
    function getYearValue(yearString: string): number {
        const match = yearString.match(/^U(\d+)$/);
        if (match && match[1]) {
            return parseInt(match[1], 10);
        }
        return 0;
    }
    
    // Sort functions for each column
    const sortByName = (a: Team, b: Team) => a.name.localeCompare(b.name);
    const sortByYear = (a: Team, b: Team) => getYearValue(a.year) - getYearValue(b.year);
    const sortByLevel = (a: Team, b: Team) => a.level - b.level;
    
    let teamItems: Team[] = [];
    
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

<div class="rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden">
  <Table hoverable={true} items={teamItems}>
    <TableHead>
      <TableHeadCell>
        <Checkbox checked={allSelected} on:change={(e) => {
          if (e.target && 'checked' in e.target) {
            handleSelectAll((e.target as HTMLInputElement).checked);
          }
        }} />
      </TableHeadCell>
      <TableHeadCell sort={sortByName}>Name</TableHeadCell>
      <TableHeadCell sort={sortByYear}>Year</TableHeadCell>
      <TableHeadCell sort={sortByLevel}>Level</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
      <TableBodyRow slot="row" let:item>
        {@const team = item as Team}
        <TableBodyCell class="p-4!">
          <Checkbox 
            checked={team.team_id ? selectedTeamIds.includes(team.team_id) : false}
            on:change={(e) => {
              if (e.target && 'checked' in e.target && team.team_id) {
                handleCheckboxChange(team.team_id, (e.target as HTMLInputElement).checked);
              }
            }}
          />
        </TableBodyCell>
        <TableBodyCell>{team.name}</TableBodyCell>
        <TableBodyCell>{team.year}</TableBodyCell>
        <TableBodyCell>{team.level}</TableBodyCell>
      </TableBodyRow>
    </TableBody>
  </Table>
</div>