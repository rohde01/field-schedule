<script lang="ts">
    import { user, token } from '../../stores/auth';
    import { goto } from '$app/navigation';
  
    let username = '';
    let password = '';
    let error = '';
  
    const handleLogin = async () => {
      error = '';
      try {
        const response = await fetch('http://localhost:8000/users/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: new URLSearchParams({
            username,
            password
          })
        });
  
        if (response.ok) {
          const data = await response.json();
          token.set(data.access_token);
  
          const userResponse = await fetch('http://localhost:8000/users/me', {
            headers: {
              'Authorization': `Bearer ${data.access_token}`
            }
          });
  
          if (userResponse.ok) {
            const userData = await userResponse.json();
            user.set(userData);
            goto('/');
          } else {
            error = 'Failed to fetch user data.';
          }
        } else {
          const errorData = await response.json();
          error = errorData.detail || 'Login failed.';
        }
      } catch (err) {
        console.error(err);
        error = 'An error occurred.';
      }
    };
  </script>
  
  <h1>Login</h1>
  
  {#if error}
    <p style="color: red;">{error}</p>
  {/if}
  
  <form on:submit|preventDefault={handleLogin}>
    <div>
      <label for="username">Username:</label>
      <input id="username" type="text" bind:value={username} required />
    </div>
    <div>
      <label for="password">Password:</label>
      <input id="password" type="password" bind:value={password} required />
    </div>
    <button type="submit">Login</button>
  </form>
