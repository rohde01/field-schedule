<script lang="ts">
    import type { PageData } from './$types';
    import { goto } from '$app/navigation';
    import DashboardSidebar from '$lib/components/DashboardSidebar.svelte';

    let { data }: { data: PageData } = $props();
    const { user } = data;

    function getGreeting(): string {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good morning';
        if (hour < 17) return 'Good afternoon';
        return 'Good evening';
    }

    function navigateTo(path: string) {
        goto(path);
    }

    function handleKeyDown(event: KeyboardEvent, path: string) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            navigateTo(path);
        }
    }
</script>

<div class="page-container">
    <DashboardSidebar />
    
    <div class="main-content">
        <h1 class="text-3xl font-bold text-mint-600 mb-6">
            {getGreeting()}, <span class="text-sage-800">{user.first_name ?? 'User'}</span>!
        </h1>

        <div class="dashboard-welcome">
            <div class="dashboard-welcome-text">
                <p>
                    This is the Dashboard page. For now this is a quiet place, but in the future this will be the place to 
                    <span class="dashboard-welcome-highlight">manage details about your club</span> and make plans for when the schedules 
                    you create should go live.
                </p>
                <p>
                    You will be able to create a calendar with field-schedules for the year round, and have it 
                    <span class="dashboard-welcome-highlight">published and updated automatically</span> on a custom URL or your club's homepage. 
                    This will be an easy way for your club to always keep up to date with the current schedule, and what's coming up later in the year.
                </p>
                <p>
                    No more messy Google Sheets, or repetitive downloading of Excel files. Your fellow club members may even 
                    <span class="dashboard-welcome-highlight">subscribe to changes</span> you make throughout the year or submit comments 
                    to the schedules for you to review directly in the dashboard. Maybe something third? Or perhaps completely else?
                </p>
            </div>
        </div>

        <div class="shortcut-container">
            <button 
                type="button"
                class="shortcut-box"
                onclick={() => navigateTo('/schedules')}
                onkeydown={(e) => handleKeyDown(e, '/schedules')}
                role="link"
                tabindex="0">
                <span class="shortcut-icon">📅</span>
                <h2 class="shortcut-title">Schedules</h2>
                <p class="shortcut-description">View and manage your field schedules</p>
            </button>
            
            <button 
                type="button"
                class="shortcut-box"
                onclick={() => navigateTo('/fields')}
                onkeydown={(e) => handleKeyDown(e, '/fields')}
                role="link"
                tabindex="0">
                <span class="shortcut-icon">🏟️</span>
                <h2 class="shortcut-title">Fields</h2>
                <p class="shortcut-description">Manage your sports fields</p>
            </button>
            
            <button 
                type="button"
                class="shortcut-box"
                onclick={() => navigateTo('/teams')}
                onkeydown={(e) => handleKeyDown(e, '/teams')}
                role="link"
                tabindex="0">
                <span class="shortcut-icon">👥</span>
                <h2 class="shortcut-title">Teams</h2>
                <p class="shortcut-description">Organize and view team information</p>
            </button>
        </div>
    </div>
</div>