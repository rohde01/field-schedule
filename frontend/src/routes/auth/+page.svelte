<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { createUserSchema, loginSchema } from '$lib/schemas/user';
    import { goto } from '$app/navigation';
    import type { PageData } from './$types';
    import { A, Button, Card, Checkbox } from 'flowbite-svelte';

    let { data } = $props<{ data: PageData }>();
    let isLogin = $state(true);
    let showConfirmation = $state(false);
    let userEmail = $state('');
    
    const { form: signupForm, errors: signupErrors, enhance: signupEnhance, message: signupMessage } = superForm(data.signupForm, {
        validators: zodClient(createUserSchema),
        resetForm: false,
        taintedMessage: null,
        onResult: ({ result }) => {
            if (result.type === 'success') {
                if (result.data?.confirmationEmailSent) {
                    userEmail = $signupForm.email;
                    showConfirmation = true;
                } else {
                    goto('/schedules');
                }
            }
            return result;
        }
    });

    const { form: loginForm, errors: loginErrors, enhance: loginEnhance, message: loginMessage } = superForm(data.loginForm, {
        validators: zodClient(loginSchema),
        resetForm: false,
        taintedMessage: null,
        onResult: ({ result }) => {
            if (result.type === 'success') {
                goto('/schedules');
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
        $signupForm.email = '';
        $signupForm.password = '';
        $signupForm.passwordConfirm = '';
    }
</script>

<main class="bg-gray-50 dark:bg-gray-900 w-full">
    <div class="flex flex-col items-center justify-center px-6 pt-8 mx-auto md:h-screen pt:mt-0 dark:bg-gray-900">
        
        {#if showConfirmation}
            <Card class="w-full p-4 sm:p-6" size="md">
                <div class="text-center space-y-4">
                    <h1 class="mb-3 text-2xl font-bold text-gray-900 dark:text-white">Check Your Email!</h1>
                    <div class="text-gray-600 dark:text-gray-300">
                        We've sent you a confirmation email to <span class="font-medium">{userEmail}</span>. Please check your inbox and click the link to verify your account.
                    </div>
                    <div class="text-sm text-gray-500 dark:text-gray-400 mt-4">
                        Didn't receive the email? Check your spam folder or <button onclick={resetForm} class="text-primary-600 hover:underline dark:text-primary-500">try signing up again</button>.
                    </div>
                </div>
            </Card>
        {:else}
            <Card class="w-full p-4 sm:p-6" size="md">
                <h1 class="mb-3 text-2xl font-bold text-gray-900 dark:text-white">
                    {isLogin ? 'Sign in' : 'Create a Free Account'}
                </h1>

                {#if isLogin}
                    <!-- LOGIN FORM -->
                    {#if $loginMessage}
                        <div class="mb-4 p-3 rounded-sm bg-red-50 text-red-600 text-sm" role="alert">
                            {$loginMessage}
                        </div>
                    {/if}

                    {#if $loginErrors._errors}
                        <div class="mb-4 p-3 rounded-sm bg-red-50 text-red-600 text-sm" role="alert">
                            {$loginErrors._errors.join(', ')}
                        </div>
                    {/if}

                    <form method="POST" class="mt-8 space-y-6" use:loginEnhance>
                        <div>
                            <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="login-email">
                                Email
                            </label>
                            <input 
                                id="login-email"
                                name="email" 
                                type="email" 
                                bind:value={$loginForm.email}
                                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                                placeholder="Messi@b93.com"
                            >
                            {#if $loginErrors.email}
                                <span class="text-red-500 text-sm">{$loginErrors.email}</span>
                            {/if}
                        </div>

                        <div>
                            <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="login-password">
                                Password
                            </label>
                            <input 
                                id="login-password"
                                name="password" 
                                type="password" 
                                bind:value={$loginForm.password}
                                placeholder="••••••••"
                                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                            >
                            {#if $loginErrors.password}
                                <span class="text-red-500 text-sm">{$loginErrors.password}</span>
                            {/if}
                        </div>

                        <div class="flex items-start">
                            <Checkbox class="accent-primary-600" name="remember">Remember me</Checkbox>
                        </div>

                        <Button 
                            type="submit"
                            size="lg" 
                            formaction="?/login"
                            class="w-full"
                        >
                            Login to your account
                        </Button>

                        <div class="text-sm font-medium text-gray-500 dark:text-gray-300">
                            Not registered? <A href="#" onclick={(e) => { e.preventDefault(); toggleMode(); }}>Create account</A>
                        </div>
                    </form>
                {:else}
                    <!-- SIGNUP FORM -->
                    {#if $signupMessage}
                        <div class="mb-4 p-3 rounded-sm bg-red-50 text-red-600 text-sm" role="alert">
                            {$signupMessage}
                        </div>
                    {/if}

                    {#if $signupErrors._errors}
                        <div class="mb-4 p-3 rounded-sm bg-red-50 text-red-600 text-sm" role="alert">
                            {$signupErrors._errors.join(', ')}
                        </div>
                    {/if}

                    <form method="POST" class="mt-8 space-y-6" use:signupEnhance>
                        <div>
                            <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="signup-email">
                                Email
                            </label>
                            <input 
                                id="signup-email"
                                name="email" 
                                type="email" 
                                bind:value={$signupForm.email}
                                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                                placeholder="Messi@b93.com"
                            >
                            {#if $signupErrors.email}
                                <span class="text-red-500 text-sm">{$signupErrors.email}</span>
                            {/if}
                        </div>

                        <div>
                            <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="signup-password">
                                Password
                            </label>
                            <input 
                                id="signup-password"
                                name="password" 
                                type="password" 
                                bind:value={$signupForm.password}
                                placeholder="••••••••"
                                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                            >
                            {#if $signupErrors.password}
                                <span class="text-red-500 text-sm">{$signupErrors.password}</span>
                            {/if}
                        </div>

                        <div>
                            <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="signup-password-confirm">
                                Confirm Password
                            </label>
                            <input 
                                id="signup-password-confirm"
                                name="passwordConfirm" 
                                type="password" 
                                bind:value={$signupForm.passwordConfirm}
                                placeholder="••••••••"
                                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                            >
                            {#if $signupErrors.passwordConfirm}
                                <span class="text-red-500 text-sm">{$signupErrors.passwordConfirm}</span>
                            {/if}
                        </div>

                        <Button 
                            type="submit"
                            size="lg" 
                            formaction="?/signup"
                            class="w-full"
                        >
                            Create account
                        </Button>

                        <div class="text-sm font-medium text-gray-500 dark:text-gray-300">
                            Already have an account? <A href="#" onclick={(e) => { e.preventDefault(); toggleMode(); }}>Login here</A>
                        </div>
                    </form>
                {/if}
            </Card>
        {/if}
    </div>
</main>