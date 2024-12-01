import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const protectedRoutes = ['/dashboard'];
  const isProtectedRoute = protectedRoutes.some(route => 
    event.url.pathname.startsWith(route)
  );

  if (isProtectedRoute) {
    const token = event.cookies.get('token');
    
    if (!token) {
      return new Response('Redirect', {
        status: 303,
        headers: { Location: '/login' }
      });
    }

    try {
      const response = await fetch('http://localhost:8000/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Invalid token');
    } catch (e) {
      event.cookies.delete('token', { path: '/' });
      return new Response('Redirect', {
        status: 303,
        headers: { Location: '/login' }
      });
    }
  }

  return resolve(event);
};