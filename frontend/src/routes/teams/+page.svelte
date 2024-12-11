<script lang="ts">
    import type { PageData } from './$types';
    import type { Team } from '$lib/types/team';
    import { teams, setTeams } from '$stores/teams';
    import TeamsDropdown from '$lib/components/TeamsDropdown.svelte';
    import TeamCard from '$lib/components/TeamCard.svelte';
    import { dropdownState } from '$stores/teamDropdownState';
    
    let { data } = $props();
    
    $effect(() => {
        if (data.teams) {
            setTeams(data.teams);
        }
    });
</script>

<div class="flex flex-col gap-4">
    <div class="sidebar-container">
        <TeamsDropdown teams={$teams} />
    </div>

    {#if $dropdownState.selectedTeam || $dropdownState.showCreateTeam}
        <div class="detail-card-container">
            <TeamCard 
                team={$dropdownState.selectedTeam} 
                isCreateMode={$dropdownState.showCreateTeam}
                form={data.form}
            />
        </div>
    {:else}
        <div class="text-center p-8 text-sage-500">
            Please select a team to view details
        </div>
    {/if}
</div>