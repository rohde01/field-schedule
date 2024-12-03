export const routeConfig = {
    '/settings': { requiresAuth: true, requiresClub: false },
    '/dashboard': { requiresAuth: true, requiresClub: true },
    '/profile': { requiresAuth: true, requiresClub: false },
    '/some-other-route': { requiresAuth: false, requiresClub: false },
};
