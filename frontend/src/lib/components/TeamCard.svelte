<script lang="ts">
    import type { Team } from '$lib/types/team';
    import TeamForm from './CreateTeam.svelte';

    let { team, isCreateMode, form } = $props<{
        team: Team | null;
        isCreateMode: boolean;
        form?: any;
    }>();
</script>

<div class="team-card" role="presentation" onmousedown={(e) => e.stopPropagation()}>
    {#if isCreateMode && form}
        <TeamForm {form} />
    {:else if team}
        <div class="detail-card">
            <h2 class="detail-card-title">{team.name}</h2>
            
            <div class="detail-card-content">
                <div class="detail-card-grid">
                    <div>
                        <p class="detail-card-label">Year</p>
                        <p class="detail-card-value">{team.year}</p>
                    </div>
                    <div>
                        <p class="detail-card-label">Gender</p>
                        <p class="detail-card-value">{team.gender}</p>
                    </div>
                </div>
                
                <div>
                    <p class="detail-card-label">Level</p>
                    <p class="detail-card-value">{team.level}</p>
                </div>
                
                <div class="detail-card-grid">
                    <div>
                        <p class="detail-card-label">Min Field Size</p>
                        <p class="detail-card-value">{team.minimum_field_size}</p>
                    </div>
                    <div>
                        <p class="detail-card-label">Preferred Size</p>
                        <p class="detail-card-value">{team.preferred_field_size || 'Not set'}</p>
                    </div>
                </div>
                
                <div class="detail-card-grid">
                    <div>
                        <p class="detail-card-label">Academy Team</p>
                        <p class="detail-card-value">{team.is_academy ? 'Yes' : 'No'}</p>
                    </div>
                    <div>
                        <p class="detail-card-label">Status</p>
                        <p class="detail-card-value">{team.is_active ? 'Active' : 'Inactive'}</p>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>

<style>
    .team-card {
        width: 100%;
    }
</style>
