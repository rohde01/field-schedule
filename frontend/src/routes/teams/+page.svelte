<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import type { PageData } from './$types';
    import type { TeamSchema } from '$lib/schemas/team';
    import { teamSchema } from '$lib/schemas/team';
    import { zod } from 'sveltekit-superforms/adapters';
    import { page } from '$app/stores';
    
    export let data: PageData;
    
    const { form, errors, enhance, message } = superForm<TeamSchema>(data.form, {
        taintedMessage: null,
        validators: zod(teamSchema),
        onUpdate: ({ form }) => {
            console.log('Form data being submitted:', form.data);
        },
        onResult: ({ result }) => {
            console.log('Form submission result:', result);
            if (result.type === 'success') {
                console.log('Team created successfully');
            }
            return undefined;
        },
        onError: (err) => {
            console.error('Form submission error:', err);
        }
    });

    // Set default values
    $form.is_active = true;
</script>

<div class="container mx-auto p-4">
    <h1 class="text-2xl mb-4">Teams</h1>
    
    <!-- Teams List -->
    {#if data.teams.length > 0}
        <ul class="mb-8">
            {#each data.teams as team}
                <li class="border p-4 mb-2">
                    <h3>{team.name} ({team.year})</h3>
                    <p>Gender: {team.gender}</p>
                    <p>Level: {team.level}</p>
                </li>
            {/each}
        </ul>
    {:else}
        <p class="mb-8">No teams found.</p>
    {/if}

    <!-- Create Team Form -->
    <h2 class="text-xl mb-4">Create New Team</h2>
    {#if $page.status === 400 && $page.form?.error}
        <div class="mb-4 p-4 rounded bg-red-100 text-red-700">
            {$page.form.error}
        </div>
    {/if}
    {#if $message}
        <div class="mb-4 p-4 rounded {$message.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}">
            {$message.text}
        </div>
    {/if}
    <form method="POST" action="?/create" use:enhance>
        <div class="grid gap-4 max-w-md">
            <div>
                <label for="name">Team Name:</label>
                <input 
                    type="text" 
                    id="name" 
                    name="name"
                    bind:value={$form.name}
                    class="border p-2 w-full"
                    required
                >
                {#if $errors.name}<span class="text-red-500">{$errors.name}</span>{/if}
            </div>

            <div>
                <label for="year">Year (e.g., U10):</label>
                <input 
                    type="text" 
                    id="year" 
                    name="year"
                    bind:value={$form.year}
                    class="border p-2 w-full"
                    required
                    pattern="^U([4-9]|1[0-9]|2[0-4])$"
                    title="Must be in format U4-U24"
                >
                {#if $errors.year}<span class="text-red-500">{$errors.year}</span>{/if}
            </div>

            <div>
                <label for="gender">Gender:</label>
                <select 
                    id="gender" 
                    name="gender"
                    bind:value={$form.gender}
                    class="border p-2 w-full"
                    required
                >
                    <option value="boys">Boys</option>
                    <option value="girls">Girls</option>
                </select>
                {#if $errors.gender}<span class="text-red-500">{$errors.gender}</span>{/if}
            </div>

            <div>
                <label>
                    <input 
                        type="checkbox" 
                        name="is_academy"
                        bind:checked={$form.is_academy}
                        class="mr-2"
                    >
                    Academy Team
                </label>
            </div>

            <div>
                <label for="minimum_field_size">Minimum Field Size:</label>
                <select 
                    id="minimum_field_size" 
                    name="minimum_field_size"
                    bind:value={$form.minimum_field_size}
                    class="border p-2 w-full"
                    required
                >
                    <option value={125}>125</option>
                    <option value={250}>250</option>
                    <option value={500}>500</option>
                    <option value={1000}>1000</option>
                </select>
                {#if $errors.minimum_field_size}<span class="text-red-500">{$errors.minimum_field_size}</span>{/if}
            </div>

            <div>
                <label for="preferred_field_size">Preferred Field Size:</label>
                <select 
                    id="preferred_field_size" 
                    name="preferred_field_size"
                    bind:value={$form.preferred_field_size}
                    class="border p-2 w-full"
                >
                    <option value={null}>None</option>
                    <option value={125}>125</option>
                    <option value={250}>250</option>
                    <option value={500}>500</option>
                    <option value={1000}>1000</option>
                </select>
                {#if $errors.preferred_field_size}<span class="text-red-500">{$errors.preferred_field_size}</span>{/if}
            </div>

            <div>
                <label for="level">Level (1-5):</label>
                <input 
                    type="number" 
                    id="level" 
                    name="level"
                    bind:value={$form.level}
                    min="1"
                    max="5"
                    class="border p-2 w-full"
                    required
                >
                {#if $errors.level}<span class="text-red-500">{$errors.level}</span>{/if}
            </div>

            <input type="hidden" name="is_active" value="true">

            <button type="submit" class="bg-green-500 text-white px-4 py-2 rounded">
                Create Team
            </button>
        </div>
    </form>
</div>