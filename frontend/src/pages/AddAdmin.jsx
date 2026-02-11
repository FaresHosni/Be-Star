import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, User, Mail, Eye, EyeOff, ArrowRight, Plus, Sparkles } from 'lucide-react'

function AddAdmin() {
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        role: 'admin'
    })
    const [showPassword, setShowPassword] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            const token = localStorage.getItem('token')
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            })

            if (!res.ok) {
                const data = await res.json()
                throw new Error(data.message || 'حدث خطأ أثناء إضافة المسؤول')
            }

            navigate('/admins')
        } catch (err) {
            setError(err.message || 'حدث خطأ أثناء إضافة المسؤول')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="h-full flex items-center justify-center overflow-hidden" style={{ background: '#0a0a0a' }}>
            {/* Main Card - Compact */}
            <div
                className="relative w-full max-w-sm"
                style={{
                    background: 'linear-gradient(180deg, #151515 0%, #0d0d0d 100%)',
                    borderRadius: '16px',
                    border: '1px solid rgba(212, 175, 55, 0.3)',
                    boxShadow: '0 0 40px rgba(212, 175, 55, 0.1)',
                    overflow: 'hidden'
                }}
            >
                {/* Gold Accent Line */}
                <div style={{
                    height: '2px',
                    background: 'linear-gradient(90deg, transparent, #D4AF37, transparent)'
                }} />

                <div className="p-5">
                    {/* Back Button - Compact */}
                    <button
                        onClick={() => navigate('/admins')}
                        className="flex items-center gap-1 text-white/50 hover:text-gold-400 transition-colors mb-3 text-sm"
                    >
                        <ArrowRight className="w-4 h-4" />
                        <span>العودة للمسؤولين</span>
                    </button>

                    {/* Header - Compact */}
                    <div className="text-center mb-4">
                        <div className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-gold-400/20 to-gold-600/10 border border-gold-400/30 mb-2">
                            <Shield className="w-5 h-5 text-gold-400" />
                        </div>
                        <h1 className="text-lg font-bold gold-text">إضافة مسؤول جديد</h1>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-3 py-2 rounded-lg mb-3 text-center text-xs">
                            {error}
                        </div>
                    )}

                    {/* Form - Compact */}
                    <form onSubmit={handleSubmit} className="space-y-3">
                        {/* Name Input */}
                        <div>
                            <label className="block text-white/60 text-xs mb-1 text-right">الاسم الكامل</label>
                            <div className="relative">
                                <User className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                                <input
                                    type="text"
                                    required
                                    placeholder="أدخل اسم المسؤول"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full py-2 px-3 pr-9 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-white/30 focus:border-gold-400/50 transition-all outline-none text-right"
                                    dir="rtl"
                                />
                            </div>
                        </div>

                        {/* Email Input */}
                        <div>
                            <label className="block text-white/60 text-xs mb-1 text-right">البريد الإلكتروني</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gold-400" />
                                <input
                                    type="email"
                                    required
                                    placeholder="admin@example.com"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full py-2 px-3 pl-9 rounded-lg bg-white/5 border border-gold-400/30 text-white text-sm placeholder-white/30 focus:border-gold-400/50 transition-all outline-none text-right"
                                    dir="rtl"
                                />
                            </div>
                        </div>

                        {/* Password Input */}
                        <div>
                            <label className="block text-white/60 text-xs mb-1 text-right">كلمة المرور</label>
                            <div className="relative">
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-gold-400 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    required
                                    placeholder="••••••••"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    className="w-full py-2 px-3 pl-9 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-white/30 focus:border-gold-400/50 transition-all outline-none text-right"
                                    dir="rtl"
                                />
                            </div>
                        </div>

                        {/* Role Select */}
                        <div>
                            <label className="block text-white/60 text-xs mb-1 text-right">الصلاحية</label>
                            <select
                                value={formData.role}
                                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                                className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm focus:border-gold-400/50 transition-all outline-none cursor-pointer appearance-none"
                                dir="rtl"
                                style={{
                                    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23D4AF37'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
                                    backgroundRepeat: 'no-repeat',
                                    backgroundPosition: 'left 0.75rem center',
                                    backgroundSize: '1rem'
                                }}
                            >
                                <option value="admin" className="bg-gray-900">🛡️ مسؤول</option>
                                <option value="super_admin" className="bg-gray-900">⭐ مدير أعلى</option>
                            </select>
                        </div>

                        {/* Buttons - Compact */}
                        <div className="pt-2 space-y-2">
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-2.5 rounded-lg font-bold text-black text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                                style={{
                                    background: 'linear-gradient(135deg, #D4AF37 0%, #B8860B 100%)',
                                    boxShadow: '0 2px 10px rgba(212, 175, 55, 0.3)'
                                }}
                            >
                                {loading ? (
                                    <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                                ) : (
                                    <>
                                        <Plus className="w-4 h-4" />
                                        إضافة المسؤول
                                    </>
                                )}
                            </button>

                            <button
                                type="button"
                                onClick={() => navigate('/admins')}
                                className="w-full py-2 rounded-lg border border-white/10 text-white/50 text-sm hover:text-white hover:border-white/30 transition-all"
                            >
                                إلغاء
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default AddAdmin
