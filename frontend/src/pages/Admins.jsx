import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Plus,
    Edit2,
    Trash2,
    Loader2,
    Shield,
    Mail,
    ArrowRight
} from 'lucide-react'

function Admins() {
    const navigate = useNavigate()
    const [admins, setAdmins] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchAdmins()
    }, [])

    const fetchAdmins = async () => {
        try {
            const token = localStorage.getItem('token')
            const res = await fetch('/api/auth/admins', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            const data = await res.json()
            setAdmins(data)
        } catch (error) {
            console.error('Error fetching admins:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id) => {
        if (!confirm('هل أنت متأكد من حذف هذا الأدمن؟')) return
        try {
            const token = localStorage.getItem('token')
            await fetch(`/api/auth/admins/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })
            fetchAdmins()
        } catch (error) {
            console.error('Error deleting admin:', error)
        }
    }


    return (
        <div className="space-y-6 fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate(-1)}
                        className="p-3 rounded-xl bg-gold-500/20 text-gold-400 hover:bg-gold-500/30 transition-colors"
                        title="رجوع"
                    >
                        <ArrowRight className="w-6 h-6" />
                    </button>
                    <div>
                        <h1 className="text-3xl font-bold gold-text">إدارة المسؤولين</h1>
                        <p className="text-white/60 mt-2">إضافة وإدارة حسابات الأدمن</p>
                    </div>
                </div>
                <button onClick={() => navigate('/admins/add')} className="btn-gold flex items-center gap-2">
                    <Plus className="w-5 h-5" />
                    إضافة أدمن
                </button>
            </div>

            {/* Admins Grid */}
            {loading ? (
                <div className="flex items-center justify-center py-20">
                    <Loader2 className="w-10 h-10 text-gold-500 animate-spin" />
                </div>
            ) : admins.length === 0 ? (
                <div className="card text-center py-20">
                    <Shield className="w-16 h-16 text-white/20 mx-auto mb-4" />
                    <p className="text-white/50">لا يوجد مسؤولين</p>
                    <button onClick={() => navigate('/admins/add')} className="btn-gold mt-4">
                        إضافة أول أدمن
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {admins.map((admin) => (
                        <div
                            key={admin.id}
                            className="card border-2 transition-all border-gold-500/30 hover:border-gold-500/50"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-gold-500 to-gold-400 flex items-center justify-center">
                                    <span className="text-xl font-bold text-dark-500">
                                        {admin.name.charAt(0)}
                                    </span>
                                </div>
                                <span className={`badge ${admin.role === 'super_admin' ? 'badge-vip' : 'badge-approved'}`}>
                                    {admin.role === 'super_admin' ? 'مدير أعلى' : 'مسؤول'}
                                </span>
                            </div>

                            <h3 className="text-lg font-semibold text-white mb-3">{admin.name}</h3>

                            <div className="space-y-2 text-sm">
                                <div className="flex items-center gap-2 text-white/70">
                                    <Mail className="w-4 h-4 text-gold-500" />
                                    <span className="font-mono">{admin.email}</span>
                                </div>
                            </div>

                            <div className="flex items-center gap-2 mt-6 pt-4 border-t border-gold-500/20">
                                <button
                                    onClick={() => navigate(`/admins/edit/${admin.id}`, { state: { admin } })}
                                    className="flex-1 p-2 rounded-lg bg-gold-500/20 text-gold-400 hover:bg-gold-500/30 transition-colors flex items-center justify-center gap-2"
                                >
                                    <Edit2 className="w-4 h-4" />
                                    تعديل
                                </button>
                                <button
                                    onClick={() => handleDelete(admin.id)}
                                    className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default Admins

