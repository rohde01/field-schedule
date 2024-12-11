<script lang="ts">
    import type { Team } from '$lib/types/team';
    import TeamForm from './CreateTeam.svelte';
    import { fade } from 'svelte/transition';
    import { enhance } from '$app/forms';
    import type { SubmitFunction } from '@sveltejs/kit';
    import { teams } from '$stores/teams';
    import { dropdownState } from '$stores/teamDropdownState';

    let { team, isCreateMode, form } = $props<{
        team: Team | null;
        isCreateMode: boolean;
        form?: any;
    }>();

    let showDeleteConfirm = $state(false);
    let isDeleting = $state(false);

    const handleDelete: SubmitFunction = () => {
        isDeleting = true;
        return async ({ result }) => {
            if (result.type === 'success') {
                showDeleteConfirm = false;
                if (team?.team_id) {
                    teams.update(t => t.filter(item => item.team_id !== team?.team_id));
                    dropdownState.update(state => ({ ...state, selectedTeam: null }));
                }
            }
            isDeleting = false;
        };
    };
</script>

<div class="team-card" role="presentation" onclick={(e) => e.stopPropagation()}>
    {#if isCreateMode && form}
        <TeamForm {form} />
    {:else if team}
        <div class="detail-card">
            <div class="relative">
                <h2 class="detail-card-title">{team.name}</h2>
                
                <div class="detail-card-content">
                    <div class="two-column-grid">
                        <!-- Left Column -->
                        <div class="column">
                            <div>
                                <p class="detail-card-label">Year</p>
                                <p class="detail-card-value">{team.year}</p>
                            </div>
                            <div>
                                <p class="detail-card-label">Gender</p>
                                <p class="detail-card-value">{team.gender}</p>
                            </div>
                            <div>
                                <p class="detail-card-label">Level</p>
                                <p class="detail-card-value">{team.level}</p>
                            </div>
                            <div>
                                <p class="detail-card-label">Academy Team</p>
                                <p class="detail-card-value">{team.is_academy ? 'Yes' : 'No'}</p>
                            </div>
                        </div>
                        
                        <!-- Right Column -->
                        <div class="column">
                            <div>
                                <p class="detail-card-label">Weekly Trainings</p>
                                <p class="detail-card-value">{team.weekly_trainings}</p>
                            </div>
                            <div>
                                <p class="detail-card-label">Min Field Size</p>
                                <div class="flex flex-wrap gap-2 mt-1">
                                    <span class="field-tag">
                                        {team.minimum_field_size}
                                    </span>
                                </div>
                            </div>
                            <div>
                                <p class="detail-card-label">Preferred Size</p>
                                <div class="flex flex-wrap gap-2 mt-1">
                                    <span class="field-tag">
                                        {team.preferred_field_size || 'Not set'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Delete Button -->
                <button
                    type="button"
                    class="btn-trash"
                    onclick={() => showDeleteConfirm = true}
                    aria-label="Delete team"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </button>

                <!-- Delete Confirmation Modal -->
                {#if showDeleteConfirm}
                    <div class="modal-overlay" transition:fade={{ duration: 200 }}>
                        <div class="modal-container"
                             role="dialog"
                             aria-labelledby="delete-modal-title"
                             aria-describedby="delete-modal-description">
                            <h3 id="delete-modal-title" class="modal-title">Delete Team</h3>
                            <p id="delete-modal-description" class="modal-description">
                                Are you sure you want to delete {team.name}? This action cannot be undone.
                            </p>
                            <div class="modal-actions">
                                <button
                                    type="button"
                                    class="btn-secondary"
                                    onclick={() => showDeleteConfirm = false}
                                    disabled={isDeleting}
                                >
                                    Cancel
                                </button>
                                <form
                                    method="POST"
                                    action="?/delete"
                                    use:enhance={handleDelete}
                                    class="inline"
                                >
                                    <input type="hidden" name="team_id" value={team.team_id} />
                                    <button
                                        type="submit"
                                        class="btn-danger"
                                        disabled={isDeleting}
                                    >
                                        {isDeleting ? 'Deleting...' : 'Delete'}
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</div>

<style>
    .team-card {
        width: 100%;
    }
    
    .two-column-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }

    .column {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
</style>
