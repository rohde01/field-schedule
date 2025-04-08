<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { createUserSchema } from '$lib/schemas/user';
    import { goto } from '$app/navigation';
    import type { PageData } from './$types';

    let { data } = $props<{ data: PageData }>();
    let showSuccessModal = $state(false);
    
    const { form, errors, enhance, message } = superForm(data.form, {
        validators: zodClient(createUserSchema),
        resetForm: false,
        taintedMessage: null,
        onResult: ({ result }) => {
            if (result.type === 'success') {
                if (result.data?.confirmationEmailSent) {
                    showSuccessModal = true;
                } else {
                    goto('/dashboard');
                }
            }
            return result;
        }
    });
</script>

<div class="min-h-[80vh] flex items-center justify-center py-12">
    <div class="w-full max-w-md">
        <div class="bg-white px-8 py-6 shadow-sm rounded-lg border border-sage-200">
            <h2 class="text-2xl font-semibold text-sage-900 mb-6">Sign In or Create Account</h2>

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

                <div class="flex gap-2">
                    <button 
                        formaction="?/login"
                        class="flex-1 bg-mint-500 hover:bg-mint-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                    >
                        Login
                    </button>
                    <button 
                        formaction="?/signup"
                        class="flex-1 bg-mint-500 hover:bg-mint-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                    >
                        Sign up
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

{#if showSuccessModal}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div class="bg-white p-6 rounded-lg shadow-xl">
            <div class="text-xl font-bold text-mint-600 mb-2">Check Your Email!</div>
            <div class="text-sage-600">
                We've sent you a confirmation email. Please check your inbox and click the link to verify your account.
            </div>
        </div>
    </div>
{/if}