<script lang="ts">
    import { SidebarDropdownState as teamDropdownState, toggleDropdown, selectTeam, toggleCreateSchedule } from '../../stores/ScheduleSidebarState';
    import { dropdownState } from '../../stores/ScheduleDropdownState';
    import { facilities } from '$stores/facilities';
    import type { Team } from '$lib/schemas/team';
    import type { SuperForm } from 'sveltekit-superforms';
    import type { GenerateScheduleRequest } from '$lib/schemas/schedule';
    import { page } from '$app/stores';
    
    let { teams, form } = $props<{ 
        teams: Team[], 
        form: SuperForm<GenerateScheduleRequest>['form']
    }>();

    let showFacilityMenu = $state(false);

    const filteredTeams = $derived(
        $dropdownState.selectedSchedule
            ? teams.filter((team: Team) => 
                $dropdownState.selectedSchedule?.entries.some(
                    entry => entry.team_id === team.team_id
                )
            )
            : teams
    );

    const yearOrder = (a: string, b: string) => {
        const numA = parseInt(a.replace('U', ''));
        const numB = parseInt(b.replace('U', ''));
        return numB - numA;
    };

    const groupedTeams = $derived(
        Object.entries(
            filteredTeams.reduce((groups: Record<string, Team[]>, team: Team) => {
                const year = team.year;
                if (!groups[year]) {
                    groups[year] = [];
                }
                groups[year].push(team);
                return groups;
            }, {})
        ).sort(([yearA], [yearB]) => yearOrder(yearA, yearB)) as [string, Team[]][]
    );

    function handleClickOutside(event: MouseEvent) {
        const target = event.target as HTMLElement;
        const isClickInsideDropdown = target.closest('.teams-dropdown');
        const isClickInsideCreateCard = target.closest('.team-card');
        const isClickInsideInput = target.closest('input, select, button');
        
        if (!isClickInsideDropdown && !isClickInsideCreateCard && !isClickInsideInput) {
            $teamDropdownState.teamsOpen = false;
            $teamDropdownState.showCreateSchedule = false;
        }
    }

    function handleTeamSelection(teamId: number | undefined, event: MouseEvent) {
        event.stopPropagation();
        if (typeof teamId === 'number') {
            const currentTeamIds = $form.team_ids || [];
            const teamIds = new Set(currentTeamIds);
            
            if (teamIds.has(teamId)) {
                teamIds.delete(teamId);
            } else {
                teamIds.add(teamId);
            }
            
            form.set({
                ...$form,
                team_ids: Array.from(teamIds)
            });
        }
    }

    function handleKeydown(teamId: number | undefined, event: KeyboardEvent) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            if (typeof teamId === 'number') {
                handleTeamSelection(teamId, event as unknown as MouseEvent);
            }
        }
    }

    function handleCreateScheduleClick() {
        if ($teamDropdownState.showCreateSchedule) {
            form.set({
                facility_id: 0,
                team_ids: [],
                constraints: [],
                club_id: $page.data.user?.primary_club_id ?? 0,
                schedule_name: 'Generated Schedule'
            });
            showFacilityMenu = false;
        } else {
            showFacilityMenu = true;
        }
        toggleCreateSchedule();
    }

    function handleFacilitySelect(facilityId: number) {
        $form.facility_id = facilityId;
        showFacilityMenu = false;
    }
</script>

<div class="fixed left-[max(1rem,calc((100%-80rem)/2+1rem))] top-32 z-40 w-72 teams-dropdown">
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
                        class:rotate-180={$teamDropdownState.teamsOpen}
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
                onclick={handleCreateScheduleClick}
            >
                {$teamDropdownState.showCreateSchedule ? 'Cancel' : 'Create Schedule'}
            </button>
        </div>
        {#if $teamDropdownState.teamsOpen}
            <div class="dropdown-content border-t border-mint-100">
                {#if filteredTeams && filteredTeams.length > 0}
                    <div class="p-1 space-y-3">
                        {#each groupedTeams as [year, yearTeams]}
                            <div class="space-y-1">
                                <h3 class="text-xs font-medium text-sage-600 px-2">{year}</h3>
                                {#each yearTeams as team}
                                <button
                                    class="dropdown-item flex items-center justify-between {$teamDropdownState.selectedTeam?.team_id === team.team_id ? 'dropdown-item-selected' : ''}"
                                    onclick={() => selectTeam(team)}
                                >
                                    <div>
                                        <span class="font-medium">{team.name}</span>
                                        <span class="text-xs text-sage-500">{team.gender}</span>
                                    </div>
                                    <div
                                        role="checkbox"
                                        tabindex="0"
                                        aria-checked={$form.team_ids.includes(team.team_id ?? -1)}
                                        class="w-6 h-6 rounded-full border-2 border-sage-400 flex items-center justify-center hover:bg-sage-100 cursor-pointer"
                                        onclick={(e) => handleTeamSelection(team.team_id, e)}
                                        onkeydown={(e) => handleKeydown(team.team_id, e)}
                                        class:bg-sage-500={$form.team_ids.includes(team.team_id ?? -1)}
                                        class:border-sage-500={$form.team_ids.includes(team.team_id ?? -1)}
                                    >
                                        {#if $form.team_ids.includes(team.team_id ?? -1)}
                                            <svg class="w-4 h-4 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a 1 1 0 01-1.414 0l-4-4a 1 1 0 011.414-1.414L8 12.586l7.293-7.293a 1 1 0 011.414 0z" clip-rule="evenodd" />
                                            </svg>
                                        {/if}
                                    </div>
                                </button>
                                {/each}
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="p-4 text-sage-500 text-center text-sm">
                        <p>No teams in this schedule</p>
                        <p class="mt-1 text-xs">Select a different schedule or go to the teams page to create one</p>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>

{#if showFacilityMenu}
    <div class="fixed left-[calc(max(1rem,calc((100%-80rem)/2+1rem))+19rem)] top-32 z-50 w-72">
        <div class="bg-white rounded-2xl shadow-xl border border-mint-100 overflow-hidden">
            <div class="p-4">
                <h2 class="text-sm font-medium text-sage-700 mb-2">Select Facility</h2>
                <div class="space-y-2 max-h-64 overflow-y-auto">
                    {#each $facilities as facility}
                        <button
                            class="w-full text-left px-4 py-2 text-sm text-sage-700 hover:bg-mint-50 rounded-lg"
                            onclick={() => handleFacilitySelect(facility.facility_id)}
                        >
                            {facility.name}
                        </button>
                    {/each}
                </div>
            </div>
        </div>
    </div>
{/if}
