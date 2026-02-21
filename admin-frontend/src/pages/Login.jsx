import React, { useState } from 'react'
import { Star, Mail, Lock, Loader2, AlertCircle, Eye, EyeOff } from 'lucide-react'

function Login({ onLogin }) {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            })

            const data = await res.json()

            if (!res.ok) {
                throw new Error(data.detail || 'حدث خطأ في تسجيل الدخول')
            }

            onLogin(data.access_token, data.admin)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            {/* Background Effects */}
            <div className="fixed inset-0 overflow-hidden">
                <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gold-500/10 rounded-full blur-3xl" />
                <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-gold-400/5 rounded-full blur-3xl" />
            </div>

            {/* Login Card */}
            <div className="relative w-full max-w-md">
                <div className="card border-gold-500/30">
                    {/* Logo */}
                    <div className="text-center mb-8">
                        <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-gold-500 to-gold-400 flex items-center justify-center shadow-lg shadow-gold-500/30">
                            <Star className="w-12 h-12 text-dark-500" fill="currentColor" />
                        </div>
                        <h1 className="text-3xl font-bold gold-text">كن نجماً</h1>
                        <p className="text-white/50 mt-2">Be Star - لوحة التحكم</p>
                    </div>

                    {/* Error */}
                    {error && (
                        <div className="mb-6 p-4 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center gap-3 text-red-400">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            <span className="text-sm">{error}</span>
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm text-white/70 mb-2">البريد الإلكتروني</label>
                            <div className="relative">
                                {!email && (
                                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gold-500/60 pointer-events-none" />
                                )}
                                <input
                                    type="email"
                                    required
                                    className="input-gold pl-12 text-right"
                                    placeholder="admin@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm text-white/70 mb-2">كلمة المرور</label>
                            <div className="relative">
                                {!password && (
                                    <Lock className="absolute left-12 top-1/2 -translate-y-1/2 w-5 h-5 text-gold-500/60 pointer-events-none" />
                                )}
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    required
                                    className="input-gold pl-20 pr-4 text-right"
                                    placeholder="أدخل كلمة المرور"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 hover:text-gold-400 transition-colors"
                                >
                                    {showPassword ? (
                                        <EyeOff className="w-5 h-5" />
                                    ) : (
                                        <Eye className="w-5 h-5" />
                                    )}
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-gold w-full py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    جاري التحقق...
                                </>
                            ) : (
                                'تسجيل الدخول'
                            )}
                        </button>
                    </form>
                </div>

                {/* Footer */}
                <p className="text-center text-white/30 text-sm mt-6">
                    © 2026 كن نجماً - جميع الحقوق محفوظة
                </p>
            </div>
        </div>
    )
}

export default Login

