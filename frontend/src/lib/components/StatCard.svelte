<script lang="ts">
    import { dropdownState } from '../../stores/ScheduleDropdownState';
    
    let { team } = $props();
    
    const daysOfWeek = ['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su'];
    
    let trainingDays = $state(new Set<number>());
    let progressPercentage = $state(0);
    let progressColor = $state('#10b981');
    
    // Update training days whenever the selected schedule or team changes
    $effect(() => {
        if ($dropdownState.selectedSchedule && team) {
            const newTrainingDays = new Set<number>();
            const teamEntries = $dropdownState.selectedSchedule.entries.filter(
                entry => entry.team_id === team.team_id
            );
            
            teamEntries.forEach(entry => {
                if (entry.week_day !== null && entry.week_day !== undefined) {
                    newTrainingDays.add(entry.week_day);
                }
            });
            
            trainingDays = newTrainingDays;
            
            const actualSessions = newTrainingDays.size;
            const targetSessions = team.weekly_trainings || 1;
            progressPercentage = Math.min((actualSessions / targetSessions) * 100, 100);
            
            if (actualSessions > targetSessions) {
                progressColor = '#ef4444';
            } else if (actualSessions === targetSessions) {
                progressColor = '#10b981';
            } else if (actualSessions >= targetSessions * 0.75) {
                progressColor = '#f59e0b';
            } else {
                progressColor = '#ef4444';
            }
        }
    });
    
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
        
        <div class="detail-card-content flex justify-center items-center py-8">
            <div class="progress-circle-container">
                <div class="progress-circle">
                    <div class="progress-bar" style="--progress: {progressPercentage}%; --progress-color: {progressColor};"></div>
                    <div class="progress-content">
                        <div class="progress-value">{trainingDays.size}/{team.weekly_trainings}</div>
                        <div class="progress-label">Sessions</div>
                    </div>
                </div>
            </div>
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
