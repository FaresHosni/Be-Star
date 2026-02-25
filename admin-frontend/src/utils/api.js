/**
 * API Helper - wraps fetch with automatic 401 handling.
 * When any API call returns 401, the user is automatically logged out
 * and redirected to the login page instead of showing a cryptic error.
 */

export async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('token')

    const headers = {
        ...options.headers,
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`
    }

    const res = await fetch(url, { ...options, headers })

    if (res.status === 401 || res.status === 403) {
        // Token expired or invalid — auto logout & redirect (no throw)
        localStorage.removeItem('token')
        localStorage.removeItem('admin')
        window.location.href = '/'
        // Return a fake OK response so calling code doesn't crash during redirect
        return new Response(JSON.stringify({}), { status: 401, headers: { 'Content-Type': 'application/json' } })
    }

    return res
}
