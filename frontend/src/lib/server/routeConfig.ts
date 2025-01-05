export const routeConfig = {
    '/dashboard': { requiresAuth: true, requiresClub: false },
    '/schedules': { requiresAuth: true, requiresClub: true },
    '/club/create': { requiresAuth: true, requiresClub: false },
    '/fields': { requiresAuth: true, requiresClub: true },
    '/teams': { requiresAuth: true, requiresClub: true },

};
