<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { createUserSchema } from '$lib/schemas/user';
    import { goto } from '$app/navigation';
    import type { PageData } from './$types';

    let { data } = $props<{ data: PageData }>();
    let isLogin = $state(true);
    let showConfirmation = $state(false);
    let userEmail = $state('');
    
    const { form, errors, enhance, message } = superForm(data.form, {
        validators: zodClient(createUserSchema),
        resetForm: false,
        taintedMessage: null,
        onResult: ({ result }) => {
            if (result.type === 'success') {
                if (result.data?.confirmationEmailSent) {
                    userEmail = $form.email;
                    showConfirmation = true;
                } else {
                    goto('/dashboard');
                }
            }
            return result;
        }
    });

    function toggleMode() {
        isLogin = !isLogin;
    }

    function resetForm() {
        showConfirmation = false;
        userEmail = '';
        $form.email = '';
        $form.password = '';
    }
</script>

<div class="min-h-[80vh] flex items-center justify-center py-12">
    <div class="w-full max-w-md">
        {#if showConfirmation}
            <div class="bg-white px-8 py-6 rounded-2xl shadow-lg border border-sage-200 text-center space-y-4">
                <div class="text-2xl font-semibold text-mint-600 mb-2">Check Your Email!</div>
                <div class="text-sage-600">
                    We've sent you a confirmation email to <span class="font-medium text-sage-700">{userEmail}</span>. Please check your inbox and click the link to verify your account.
                </div>
                <div class="text-sm text-sage-500 mt-4">
                    Didn't receive the email? Check your spam folder or <button onclick={resetForm} class="text-mint-600 hover:text-mint-700 underline">try signing up again</button>.
                </div>
            </div>
        {:else}
            <div class="bg-white px-8 py-6 rounded-2xl shadow-lg border border-sage-200">
                <h2 class="text-2xl font-semibold text-sage-900 mb-6">{isLogin ? 'Welcome back!' : 'Create Account'}</h2>

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

                    <div class="space-y-3">
                        <button 
                            formaction={isLogin ? "?/login" : "?/signup"}
                            class="w-full bg-mint-500 hover:bg-mint-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                        >
                            {isLogin ? 'Login' : 'Sign up'}
                        </button>
                        <button 
                            type="button"
                            onclick={toggleMode}
                            class="w-full text-sm text-mint-600 hover:text-mint-700 transition-colors duration-200"
                        >
                            {isLogin ? 'Need to register?' : 'Already have an account?'}
                        </button>
                    </div>
                </form>
            </div>
        {/if}
    </div>
</div>