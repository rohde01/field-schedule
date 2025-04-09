<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { updateNameSchema } from '$lib/schemas/user';
    import { createClubSchema } from '$lib/schemas/club';
    import type { PageData } from './$types';

    let { data } = $props<{ data: PageData }>();
    
    const { form: nameForm, errors: nameErrors, enhance: nameEnhance, message: nameMessage } = superForm(data.nameForm, {
        validators: zodClient(updateNameSchema),
        resetForm: false,
        taintedMessage: null
    });

    const { form: clubForm, errors: clubErrors, enhance: clubEnhance, message: clubMessage } = superForm(data.clubForm, {
        validators: zodClient(createClubSchema),
        resetForm: false,
        taintedMessage: null
    });
</script>

<div class="min-h-[80vh] flex items-center justify-center py-12">
    <div class="w-full max-w-md">
        {#if !data.user?.first_name || !data.user?.last_name}
            <div class="bg-white px-8 py-6 rounded-2xl shadow-lg border border-sage-200">
                <h2 class="text-2xl font-semibold text-sage-900 mb-6">Complete Your Profile</h2>
                
                {#if $nameMessage}
                    <div class="mb-4 p-3 rounded bg-red-50 text-red-600 text-sm" role="alert">
                        {$nameMessage}
                    </div>
                {/if}

                <form method="POST" action="?/updateName" class="space-y-4" use:nameEnhance>
                    <div>
                        <label class="block text-sm font-medium text-sage-700 mb-2" for="first_name">
                            First Name
                        </label>
                        <input 
                            id="first_name"
                            name="first_name" 
                            type="text" 
                            bind:value={$nameForm.first_name}
                            class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                        >
                        {#if $nameErrors.first_name}
                            <span class="text-red-500 text-sm">{$nameErrors.first_name}</span>
                        {/if}
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-sage-700 mb-2" for="last_name">
                            Last Name
                        </label>
                        <input 
                            id="last_name"
                            name="last_name" 
                            type="text" 
                            bind:value={$nameForm.last_name}
                            class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                        >
                        {#if $nameErrors.last_name}
                            <span class="text-red-500 text-sm">{$nameErrors.last_name}</span>
                        {/if}
                    </div>

                    <button 
                        type="submit"
                        class="w-full bg-mint-500 hover:bg-mint-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                    >
                        Save Profile
                    </button>
                </form>
            </div>
        {:else}
            <div class="bg-white px-8 py-6 rounded-2xl shadow-lg border border-sage-200">
                <h2 class="text-2xl font-semibold text-sage-900 mb-6">Create Your Club</h2>
                
                {#if $clubMessage}
                    <div class="mb-4 p-3 rounded bg-red-50 text-red-600 text-sm" role="alert">
                        {$clubMessage}
                    </div>
                {/if}

                <form method="POST" action="?/createClub" class="space-y-4" use:clubEnhance>
                    <div>
                        <label class="block text-sm font-medium text-sage-700 mb-2" for="name">
                            Club Name
                        </label>
                        <input 
                            id="name"
                            name="name" 
                            type="text" 
                            bind:value={$clubForm.name}
                            class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                        >
                        {#if $clubErrors.name}
                            <span class="text-red-500 text-sm">{$clubErrors.name}</span>
                        {/if}
                    </div>

                    <button 
                        type="submit"
                        class="w-full bg-mint-500 hover:bg-mint-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                    >
                        Create Club
                    </button>
                </form>
            </div>
        {/if}
    </div>
</div>