<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { createUserSchema } from '$lib/schemas/user';
    import { goto } from '$app/navigation';

    let { data } = $props();
    let showSuccessModal = $state(false);
    
    const { form, errors, enhance, message } = superForm(data.form, {
        validators: zodClient(createUserSchema),
        resetForm: false,
        taintedMessage: null,
        onResult: ({ result }) => {
            if (result.type === 'success') {
                showSuccessModal = true;
                setTimeout(() => {
                    goto('/login');
                }, 4000);
            }
            return result;
        }
    });
</script>

<div class="min-h-[80vh] flex items-center justify-center py-12">
    <div class="w-full max-w-md">
        <div class="bg-white px-8 py-6 shadow-sm rounded-lg border border-sage-200">
            <h2 class="text-2xl font-semibold text-sage-900 mb-6">Create your account</h2>

            {#if $message}
                <div class="mb-4 p-3 rounded bg-red-50 text-red-600 text-sm" role="alert">
                    {$message}
                </div>
            {/if}

            {#if $errors._errors}
                <div class="mb-4 p-3 rounded bg-red-50 text-red-600 text-sm" role="alert">
                    {$errors._errors.join(', ')}
                </div>
            {/if}

            <form method="POST" class="space-y-4" use:enhance>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-sage-700 mb-2" for="first_name">
                            First Name
                        </label>
                        <input 
                            id="first_name"
                            name="first_name" 
                            type="text" 
                            bind:value={$form.first_name}
                            class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                        >
                        {#if $errors.first_name}
                            <span class="text-red-500 text-sm">{$errors.first_name}</span>
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
                            bind:value={$form.last_name}
                            class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                        >
                        {#if $errors.last_name}
                            <span class="text-red-500 text-sm">{$errors.last_name}</span>
                        {/if}
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-sage-700 mb-2" for="email">
                        Email
                    </label>
                    <input 
                        id="email"
                        name="email" 
                        type="email" 
                        bind:value={$form.email}
                        class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                    >
                    {#if $errors.email}
                        <span class="text-red-500 text-sm">{$errors.email}</span>
                    {/if}
                </div>

                <div>
                    <label class="block text-sm font-medium text-sage-700 mb-2" for="password">
                        Password
                    </label>
                    <input 
                        id="password"
                        name="password" 
                        type="password" 
                        bind:value={$form.password}
                        class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                    >
                    {#if $errors.password}
                        <span class="text-red-500 text-sm">{$errors.password}</span>
                    {/if}
                </div>

                <button 
                    type="submit" 
                    class="w-full mt-6 bg-mint-500 hover:bg-mint-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                >
                    Create Account
                </button>
            </form>

            <p class="mt-4 text-center text-sm text-sage-600">
                Already have an account? 
                <a href="/login" class="text-mint-600 hover:text-mint-700 font-medium">
                    Sign in
                </a>
            </p>
        </div>
    </div>
</div>

{#if showSuccessModal}
    <div class="modal-overlay">
        <div class="modal-container">
            <div class="modal-title text-mint-600">Registration Successful!</div>
            <div class="modal-description">
                Your account has been created. Redirecting to login page...
            </div>
        </div>
    </div>
{/if}