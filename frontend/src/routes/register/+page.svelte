<script lang="ts">
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';
    import type { ActionData } from './$types';
    export let form: ActionData;
</script>

<div class="min-h-[80vh] flex items-center justify-center py-12">
    <div class="w-full max-w-md">
        <div class="bg-white px-8 py-6 shadow-sm rounded-lg border border-sage-200">
            <h2 class="text-2xl font-semibold text-sage-900 mb-6">Create your account</h2>

            {#if form?.error}
                <div class="mb-4 p-3 rounded bg-red-50 text-red-600 text-sm">
                    {form.error}
                </div>
            {/if}

            <form 
                method="POST" 
                class="space-y-4"
                use:enhance={({ formElement, formData, action, cancel }) => {
                    return async ({ result }) => {
                        if (result.type === 'redirect') {
                            goto(result.location);
                        }
                    };
                }}
            >
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-sage-700 mb-2" for="first_name">
                            First Name
                        </label>
                        <input 
                            id="first_name"
                            name="first_name" 
                            type="text" 
                            value={form?.firstName ?? ''} 
                            required
                            class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                        >
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-sage-700 mb-2" for="last_name">
                            Last Name
                        </label>
                        <input 
                            id="last_name"
                            name="last_name" 
                            type="text" 
                            value={form?.lastName ?? ''} 
                            required
                            class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                        >
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-sage-700 mb-2" for="username">
                        Username
                    </label>
                    <input 
                        id="username"
                        name="username" 
                        type="text" 
                        value={form?.username ?? ''} 
                        required
                        class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                    >
                </div>

                <div>
                    <label class="block text-sm font-medium text-sage-700 mb-2" for="email">
                        Email
                    </label>
                    <input 
                        id="email"
                        name="email" 
                        type="email" 
                        value={form?.email ?? ''} 
                        required
                        class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                    >
                </div>

                <div>
                    <label class="block text-sm font-medium text-sage-700 mb-2" for="password">
                        Password
                    </label>
                    <input 
                        id="password"
                        name="password" 
                        type="password" 
                        required
                        class="block w-full p-2 text-sm text-sage-700 rounded-lg border border-sage-200 focus:ring-mint-500 focus:border-mint-500"
                    >
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