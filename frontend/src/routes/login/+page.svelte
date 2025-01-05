<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { loginSchema } from '$lib/schemas/user';

    let { data } = $props();
    
    const { form, errors, enhance, message } = superForm(data.form, {
        validators: zodClient(loginSchema),
        resetForm: false,
        taintedMessage: null
    });
</script>

<div class="min-h-[80vh] flex items-center justify-center">
    <div class="w-full max-w-md">
        <div class="bg-white px-8 py-6 shadow-sm rounded-lg border border-sage-200">
            <h2 class="text-2xl font-semibold text-sage-900 mb-6">Welcome back</h2>
            
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

                <button 
                    type="submit" 
                    class="w-full mt-6 bg-mint-500 hover:bg-mint-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                >
                    Log in
                </button>
            </form>

            <p class="mt-4 text-center text-sm text-sage-600">
                Don't have an account? 
                <a href="/register" class="text-mint-600 hover:text-mint-700 font-medium">
                    Sign up
                </a>
            </p>
        </div>
    </div>
</div>
