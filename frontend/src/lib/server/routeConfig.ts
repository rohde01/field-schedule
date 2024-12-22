export const routeConfig = {
    '/dashboard': { requiresAuth: true, requiresClub: true },
    '/schedules': { requiresAuth: true, requiresClub: true },
    '/club/create': { requiresAuth: true, requiresClub: false },
    '/facilities': { requiresAuth: true, requiresClub: true },
    '/teams': { requiresAuth: true, requiresClub: true },
};
