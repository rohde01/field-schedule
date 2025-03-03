<script lang="ts">
    import type { Team } from '$lib/schemas/team';
    import { dropdownState } from '../../stores/ScheduleDropdownState';
    
    let { team } = $props();
    
    const daysOfWeek = ['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su'];
    
    let trainingDays = $state(new Set<number>());
    
    // Update training days whenever the selected schedule or team changes
    $effect(() => {
        if ($dropdownState.selectedSchedule && team) {
            updateTrainingDays();
        }
    });

    function updateTrainingDays() {
        const newTrainingDays = new Set<number>();
        
        if ($dropdownState.selectedSchedule && team && team.team_id) {
            const teamEntries = $dropdownState.selectedSchedule.entries.filter(
                entry => entry.team_id === team.team_id
            );
            
            teamEntries.forEach(entry => {
                if (entry.week_day !== null && entry.week_day !== undefined) {
                    newTrainingDays.add(entry.week_day);
                }
            });
        }
        trainingDays = newTrainingDays;
    }
    
    function hasTraining(day: number): boolean {
        return trainingDays.has(day);
    }
</script>

<div class="detail-card mt-4">
    <div class="relative">
        <h2 class="detail-card-title">{team.name} Statistics</h2>
        <div class="absolute top-2 right-2">
            <div class="flex items-center gap-1">
                {#each daysOfWeek as day, index}
                    <div class="flex flex-col items-center">
                        <span class="text-xs text-sage-500">{day}</span>
                        <div 
                            class="w-4 h-4 rounded-full mt-1 border border-sage-200" 
                            class:bg-emerald-500={hasTraining(index)}
                            class:bg-gray-100={!hasTraining(index)}
                        ></div>
                    </div>
                {/each}
            </div>
        </div>
        
        <div class="detail-card-content">

        </div>
    </div>
</div>

<style>
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
