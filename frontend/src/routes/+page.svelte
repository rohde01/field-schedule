<script lang="ts">
    import { fly } from 'svelte/transition';
</script>

<div class="flex flex-col">
    <!-- Hero Section -->
    <div class="px-4 py-8">
        <div class="flex flex-col justify-center items-center py-32 bg-linear-to-br from-mint-500 to-sage-500 rounded-3xl shadow-lg">
            <div class="w-full max-w-4xl mx-auto text-center px-4" in:fly="{{ y: 50, duration: 1000 }}">
                <h1 class="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-8">
                    Baneplanen.
                </h1>
                <p class="text-xl sm:text-2xl text-white/90 mb-12">
                    En tidlig prototype udviklet i samarbejde med og for <span class="font-bold bg-linear-to-r from-[#C8102E] to-blue-800 text-transparent bg-clip-text">Boldklubben af 1893</span>
                </p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="/register" class="btn-primary text-lg px-8 py-3 bg-white text-mint-600 hover:bg-mint-50">
                        Get Started
                    </a>
                    <a href="/login" class="btn-secondary text-lg px-8 py-3 bg-transparent border-2 border-white text-white hover:bg-white/10">
                        Sign In
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Features Section -->
    <div class="w-full py-24">
        <div class="max-w-7xl mx-auto px-4">
            <div class="bg-white rounded-2xl shadow-lg p-12">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-12">
                    <div class="text-center p-6" in:fly="{{ y: 50, duration: 1000, delay: 200 }}">
                        <div class="w-16 h-16 mx-auto mb-6 bg-mint-100 rounded-full flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-mint-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <h3 class="text-xl font-semibold text-sage-800 mb-4">Smart Scheduling</h3>
                        <p class="text-sage-600">A constraint model to solve soccer field scheduling problems for local soccer clubs</p>
                    </div>

                    <div class="text-center p-6" in:fly="{{ y: 50, duration: 1000, delay: 400 }}">
                        <div class="w-16 h-16 mx-auto mb-6 bg-mint-100 rounded-full flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-mint-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                            </svg>
                        </div>
                        <h3 class="text-xl font-semibold text-sage-800 mb-4">Team Management</h3>
                        <p class="text-sage-600">Easily manage teams and their training needs in one place</p>
                    </div>

                    <div class="text-center p-6" in:fly="{{ y: 50, duration: 1000, delay: 600 }}">
                        <div class="w-16 h-16 mx-auto mb-6 bg-mint-100 rounded-full flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-mint-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                        </div>
                        <h3 class="text-xl font-semibold text-sage-800 mb-4">Field Management</h3>
                        <p class="text-sage-600">Build out your facility and map your field resources. Let the model do the rest</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
