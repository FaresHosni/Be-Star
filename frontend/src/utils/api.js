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

    if (res.status === 401) {
        // Token expired or invalid — auto logout
        localStorage.removeItem('token')
        localStorage.removeItem('admin')
        window.location.href = '/'
        throw new Error('جلستك انتهت، يرجى تسجيل الدخول مرة أخرى')
    }

    return res
}
