<script lang="ts">
    import { user, token } from '../../stores/auth';
    import { goto } from '$app/navigation';
  
    let username = '';
    let email = '';
    let password = '';
    let first_name = '';
    let last_name = '';
    let error = '';
  
    const handleRegister = async () => {
      error = '';
      try {
        const response = await fetch('http://localhost:8000/users/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username,
            email,
            password,
            first_name,
            last_name
          })
        });
  
        if (response.ok) {
          const loginResponse = await fetch('http://localhost:8000/users/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
              username,
              password
            })
          });
  
          if (loginResponse.ok) {
            const data = await loginResponse.json();
            token.set(data.access_token);
  
            // Fetch the user data
            const userResponse = await fetch('http://localhost:8000/users/me', {
              headers: {
                'Authorization': `Bearer ${data.access_token}`
              }
            });
  
            if (userResponse.ok) {
              const userData = await userResponse.json();
              user.set(userData);
              // Redirect to the dashboard or home page
              goto('/');
            } else {
              error = 'Failed to fetch user data.';
            }
          } else {
            error = 'Registration successful but failed to log in.';
          }
        } else {
          const errorData = await response.json();
          error = errorData.detail || 'Registration failed.';
        }
      } catch (err) {
        console.error(err);
        error = 'An error occurred.';
      }
    };
  </script>
  
  <h1>Register</h1>
  
  {#if error}
    <p style="color: red;">{error}</p>
  {/if}
  
  <form on:submit|preventDefault={handleRegister}>
    <div>
      <label for="reg-username">Username:</label>
      <input id="reg-username" type="text" bind:value={username} required />
    </div>
    <div>
      <label for="reg-email">Email:</label>
      <input id="reg-email" type="email" bind:value={email} required />
    </div>
    <div>
      <label for="reg-password">Password:</label>
      <input id="reg-password" type="password" bind:value={password} required />
    </div>
    <div>
      <label for="reg-firstname">First Name:</label>
      <input id="reg-firstname" type="text" bind:value={first_name} />
    </div>
    <div>
      <label for="reg-lastname">Last Name:</label>
      <input id="reg-lastname" type="text" bind:value={last_name} />
    </div>
    <button type="submit">Register</button>
  </form>
