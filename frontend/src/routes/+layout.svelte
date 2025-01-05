<script lang="ts">
    import '../app.css';
    import { setFacilities } from '$stores/facilities';
    import { setFields } from '$stores/fields';
    import { setTeams } from '$stores/teams';
    import { setConstraints } from '$stores/constraints';

    let { data } = $props();

    $effect(() => {
        if (data.facilities) {
            setFacilities(data.facilities);
        }
    });

    $effect(() => {
        if (data.fields) {
            setFields(data.fields);
        }
    });

    $effect(() => {
        if (data.teams) {
            setTeams(data.teams);
        }
    });

    $effect(() => {
        if (data.constraints) {
            setConstraints(data.constraints);
        }
    });
</script>

<div class="min-h-screen bg-sage-50 relative pt-16"> 
    <nav class="nav-container">
        <div class="max-w-[90%] mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center space-x-4">
                    <a href="/" class="nav-link">Home</a>
                    {#if data.user}
                        <a href="/dashboard" class="nav-link">Dashboard</a>
                        <a href="/schedules" class="nav-link">Schedules</a>
                        <a href="/teams" class="nav-link">Teams</a>
                        <a href="/fields" class="nav-link">Fields</a>
                    {/if}
                </div>
                <div class="flex items-center space-x-4">
                    {#if data.user}
                        <form action="/logout" method="POST">
                            <button type="submit" class="btn-secondary">Logout</button>
                        </form>
                    {:else}
                        <a href="/login" class="nav-link">Login</a>
                        <a href="/register" class="btn-primary">Register</a>
                    {/if}
                </div>
            </div>
        </div>
    </nav>
    <div class="max-w-[90%] mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <slot />
    </div>
</div>