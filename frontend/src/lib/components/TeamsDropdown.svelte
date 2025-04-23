<script lang="ts">
    import { dropdownState, toggleDropdown, selectTeam, setDefaultTeam, toggleCreateTeam } from '../stores/teamDropdownState';
    import type { Team } from '$lib/schemas/team';
    
    let { teams } = $props<{ teams: Team[] }>();

    const yearOrder = (a: string, b: string) => {
        const numA = parseInt(a.replace('U', ''));
        const numB = parseInt(b.replace('U', ''));
        return numB - numA;
    };

    const groupedTeams = $derived(
        Object.entries(
            teams.filter((team: Team) => team.is_active).reduce((groups: Record<string, Team[]>, team: Team) => {
                const year = team.year;
                if (!groups[year]) {
                    groups[year] = [];
                }
                groups[year].push(team);
                return groups;
            }, {})
        ).sort(([yearA], [yearB]) => yearOrder(yearA, yearB)) as [string, Team[]][]
    );

    $effect(() => {
        if (teams.length > 0) {
            setDefaultTeam(teams);
        }
    });

    function handleClickOutside(event: MouseEvent) {
        const target = event.target as HTMLElement;
        const isClickInsideDropdown = target.closest('.teams-dropdown');
        const isClickInsideCreateCard = target.closest('.team-card');
        const isClickInsideInput = target.closest('input, select, button');
        
        if (!isClickInsideDropdown && !isClickInsideCreateCard && !isClickInsideInput) {
            $dropdownState.teamsOpen = false;
            $dropdownState.showCreateTeam = false;
        }
    }
</script>



<div class="teams-dropdown">
    <div class="bg-white rounded-2xl shadow-xl border border-mint-100 overflow-hidden">
        <div class="flex items-center">
            <div class="flex-1 flex items-center">
                <h2 class="text-sm font-medium text-sage-700 pl-4">Teams</h2>
                <button
                    class="p-2 ml-2"
                    onclick={() => toggleDropdown('teamsOpen')}
                    aria-label="Toggle teams dropdown"
                >
                    <svg
                        class="w-5 h-5 transition-transform duration-200 text-sage-600"
                        class:rotate-180={$dropdownState.teamsOpen}
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a 1 1 0 111.414 1.414l-4 4a 1 1 0 01-1.414 0l-4-4a 1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
            <button 
                class="btn-primary text-sm py-1.5 m-2"
                onclick={toggleCreateTeam}
            >
                Create Team
            </button>
        </div>
        {#if $dropdownState.teamsOpen}
            <div class="dropdown-content border-t border-mint-100">
                {#if teams && teams.length > 0}
                    <div class="p-1 space-y-3">
                        {#each groupedTeams as [year, yearTeams]}
                            <div class="space-y-1">
                                <h3 class="text-xs font-medium text-sage-600 px-2">{year}</h3>
                                {#each yearTeams as team}
                                <button
                                    class="dropdown-item {$dropdownState.selectedTeam?.team_id === team.team_id ? 'dropdown-item-selected' : ''}"
                                    onclick={() => selectTeam(team)}
                                >
                                    <span class="font-medium">{team.name}</span>
                                    <span class="text-xs text-sage-500">{team.gender}</span>
                                </button>
                                {/each}
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="p-4 text-sage-500 text-center text-sm">
                        <p>No teams available</p>
                        <p class="mt-1 text-xs">Click 'Create Team' to add one</p>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>
