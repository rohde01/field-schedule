<script lang="ts">
    import { Heading, P, Button, Dropdown, DropdownItem, DropdownHeader, Checkbox, Search, Spinner } from 'flowbite-svelte';
    import { ArrowRightOutline, ChevronDownOutline } from 'flowbite-svelte-icons';
    import { onMount } from 'svelte';
    import ClubSchedule from './ClubSchedule.svelte';
    import { setSchedules } from '$lib/stores/schedules';
    import { setTeams } from '$lib/stores/teams';
    import { setFields } from '$lib/stores/fields';
    import type { PageData } from './$types';

    let { data }: { data: PageData } = $props();
    
    let searchTerm = $state("");
    let authLoading = $state(false);
    let filteredClubs = $derived(data.clubs.filter((club) => 
        club.name.toLowerCase().indexOf(searchTerm?.toLowerCase()) !== -1
    ));

    function navigateToClub(clubName: string) {
        const currentUrl = new URL(window.location.href);
        const protocol = currentUrl.protocol;
        const hostname = currentUrl.hostname;
        
        // Handle localhost and production domains
        if (hostname === 'localhost') {
            window.location.href = `${protocol}//${clubName}.localhost:${currentUrl.port}`;
        } else {
            // For production, determine the main domain
            let mainDomain;
            if (hostname === 'baneplanen.info' || hostname === 'www.baneplanen.info') {
                mainDomain = 'baneplanen.info';
            } else if (hostname.endsWith('.baneplanen.info')) {
                mainDomain = 'baneplanen.info';
            } else {
                // Fallback: extract main domain by removing subdomain
                mainDomain = hostname.replace(/^[^.]+\./, '');
            }
            window.location.href = `${protocol}//${clubName}.${mainDomain}`;
        }
    }

    onMount(() => {
        if (data.hasSubdomain && data.schedules) {
            setSchedules(data.schedules);
        }
        if (data.hasSubdomain && data.teams) {
            setTeams(data.teams);
        }
        if (data.hasSubdomain && data.fields) {
            setFields(data.fields);
        }
    });
</script>

{#if data.hasSubdomain}
    {#if data.invalidSubdomain}
        <div class="flex items-center justify-center min-h-screen dark:bg-gray-900">
            <div class="container max-w-4xl mx-auto px-8 py-24 text-center">
                <Heading tag="h1" class="mb-6 text-center" customSize="text-5xl font-extrabold md:text-6xl lg:text-7xl">Ups!</Heading>
                
                <P class="mb-8 text-xl lg:text-2xl dark:text-gray-400 text-center">
                    Vi kunne ikke finde en klub med navnet <span class="font-bold text-red-500">"{data.invalidSubdomain}"</span>
                </P>
                
                <P class="mb-12 text-lg lg:text-xl dark:text-gray-400 text-center">
                    Prøv at tjekke stavemåden eller vælg en klub fra listen nedenfor
                </P>
                
                <div class="mb-8 flex justify-center">
                    <Button size="lg">Find din klub<ChevronDownOutline class="ms-2 h-6 w-6 text-white dark:text-white" /></Button>
                    <Dropdown>
                        <div class="p-3">
                            <Search size="md" bind:value={searchTerm} placeholder="Søg efter klub..." />
                        </div>
                        <div class="h-48 overflow-y-auto">
                            {#each filteredClubs as club (club.club_id)}
                                <button 
                                    type="button"
                                    class="w-full text-left rounded-sm p-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer focus:bg-gray-100 dark:focus:bg-gray-600 focus:outline-none" 
                                    onclick={() => navigateToClub(club.name)}>
                                    <div class="px-2 py-1 text-sm text-gray-900 dark:text-white">
                                        {club.name}
                                    </div>
                                </button>
                            {/each}
                            {#if filteredClubs.length === 0}
                                <div class="rounded-sm p-2 text-gray-500 dark:text-gray-400">
                                    <div class="px-2 py-1 text-sm">
                                        Ingen klubber fundet
                                    </div>
                                </div>
                            {/if}
                        </div>
                    </Dropdown>
                </div>
            </div>
        </div>
    {:else}
        <ClubSchedule />
    {/if}
{:else}
    <div class="flex items-center justify-center min-h-screen dark:bg-gray-900">
        <div class="container max-w-6xl mx-auto px-8 py-24">
            <div class="text-center">
                <Heading tag="h1" class="mb-10" customSize="text-6xl font-extrabold md:text-7xl lg:text-8xl">Baneplanen.</Heading>
                
                <P class="mb-12 text-2xl lg:text-3xl sm:px-16 xl:px-40 dark:text-gray-400">
                    En tidlig prototype udviklet i samarbejde med og for <span class="font-bold bg-gradient-to-r from-[#C8102E] to-blue-800 text-transparent bg-clip-text">Boldklubben af 1893</span>
                </P>
                
                <div class="mb-8 flex justify-center">
                    <Button size="xl">Find din klub<ChevronDownOutline class="ms-2 h-6 w-6 text-white dark:text-white" /></Button>
                    <Dropdown>
                        <div class="p-3">
                            <Search size="md" bind:value={searchTerm} placeholder="Søg efter klub..." />
                        </div>
                        <div class="h-48 overflow-y-auto">
                            {#each filteredClubs as club (club.club_id)}
                                <button 
                                    type="button"
                                    class="w-full text-left rounded-sm p-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer focus:bg-gray-100 dark:focus:bg-gray-600 focus:outline-none" 
                                    onclick={() => navigateToClub(club.name)}>
                                    <div class="px-2 py-1 text-sm text-gray-900 dark:text-white">
                                        {club.name}
                                    </div>
                                </button>
                            {/each}
                            {#if filteredClubs.length === 0}
                                <div class="rounded-sm p-2 text-gray-500 dark:text-gray-400">
                                    <div class="px-2 py-1 text-sm">
                                        Ingen klubber fundet
                                    </div>
                                </div>
                            {/if}
                        </div>
                    </Dropdown>
                </div>
                
                <div class="mt-24">
                    <P class="mb-4 text-2xl lg:text-3xl sm:px-16 xl:px-40 dark:text-gray-400 text-center">
                        Administrerer du en klub?
                    </P>
                    <Button outline size="sm" href="/auth" class="px-6 py-2" disabled={authLoading} onclick={() => authLoading = true}>
                        {#if authLoading}
                            <Spinner class="me-3" size="4" />Var check...
                        {:else}
                            Opret/login
                            <ArrowRightOutline class="w-4 h-4 ms-2" />
                        {/if}
                    </Button>
                </div>
            </div>
        </div>
    </div>
{/if}