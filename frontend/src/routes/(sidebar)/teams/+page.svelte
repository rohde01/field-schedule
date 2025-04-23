<script lang="ts">
    import { teams, setTeams } from '$stores/teams';
    import TeamsDropdown from '$lib/components/TeamsDropdown.svelte';
    import DisplayCard from '$lib/components/DisplayCard.svelte';
    import CreateTeam from '$lib/components/CreateTeam.svelte';
    import { dropdownState } from '$stores/teamDropdownState';
    import type { Column } from '$lib/components/DisplayCard.svelte';

    export let data;

    if (data.teams) {
        setTeams(data.teams);
    }

    let displayColumns: Column[] = [];

    const handleTeamDelete = (teamId: number) => {
        teams.update(t => t.filter(item => item.team_id !== teamId));
        dropdownState.update(state => ({ ...state, selectedTeam: null }));
    };

    function formatFieldSize(size: number): string {
        switch (size) {
            case 1000:
                return '11v11';
            case 500:
                return '8v8, Half 11v11';
            case 250:
                return '5v5, Half 8v8, Quarter 11v11';
            case 125:
                return '3v3, Half 5v5, Quarter 8v8';
            default:
                return `${size}`;
        }
    }

    $: if ($dropdownState.selectedTeam) {
        const team = $dropdownState.selectedTeam;
        displayColumns = [
            {
                fields: [
                    { label: 'Year', value: team.year },
                    { label: 'Gender', value: team.gender },
                    { label: 'Level', value: team.level },
                    { label: 'Academy Team', value: team.is_academy ? 'Yes' : 'No' }
                ]
            },
            {
                fields: [
                    { label: 'Weekly Trainings', value: team.weekly_trainings },
                    { label: 'Minimum Field Size', value: formatFieldSize(team.minimum_field_size), style: 'pill' },
                    { label: 'Preferred Size', value: team.preferred_field_size ? formatFieldSize(team.preferred_field_size) : 'Not set', style: 'pill' }
                ]
            }
        ];
    }
</script>

<div class="page-container">
    <div class="sidebar">
        <div class="sidebar-content">
            <TeamsDropdown teams={$teams} />
        </div>
    </div>

    {#if $dropdownState.selectedTeam || $dropdownState.showCreateTeam}
        <div class="main-content">
            {#if $dropdownState.showCreateTeam}
                <CreateTeam form={data.createForm} />
            {:else if $dropdownState.selectedTeam}
                <DisplayCard 
                    title={$dropdownState.selectedTeam?.name}
                    columns={displayColumns}
                    deleteConfig={{
                        enabled: true,
                        itemId: $dropdownState.selectedTeam?.team_id || 0,
                        itemName: $dropdownState.selectedTeam?.name || '',
                        onDelete: handleTeamDelete,
                        actionPath: "?/deleteTeam",
                        formField: "team_id"
                    }}
                />
            {/if}
        </div>
    {:else}
        <div class="main-content text-center p-8 text-sage-500">
            Please select a team to view details
        </div>
    {/if}
</div>
