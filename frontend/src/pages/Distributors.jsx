import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Plus,
    Edit2,
    Trash2,
    Check,
    X,
    Loader2,
    Users,
    Phone,
    MapPin,
    ArrowRight
} from 'lucide-react'

function Distributors() {
    const navigate = useNavigate()
    const [distributors, setDistributors] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [editingDistributor, setEditingDistributor] = useState(null)
    const [formData, setFormData] = useState({ name: '', phone: '', location: '' })

    useEffect(() => {
        fetchDistributors()
    }, [])

    const fetchDistributors = async () => {
        try {
            const res = await fetch('/api/distributors')
            const data = await res.json()
            setDistributors(data)
        } catch (error) {
            console.error('Error fetching distributors:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            let res
            if (editingDistributor) {
                res = await fetch(`/api/distributors/${editingDistributor.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                })
            } else {
                res = await fetch('/api/distributors', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                })
            }
            if (!res.ok) {
                const err = await res.json().catch(() => ({}))
                alert(err.detail || 'حدث خطأ أثناء الحفظ')
                setLoading(false)
                return
            }
            fetchDistributors()
            closeModal()
        } catch (error) {
            console.error('Error saving distributor:', error)
            alert('خطأ في الاتصال بالسيرفر')
        }
        setLoading(false)
    }

    const handleToggleActive = async (distributor) => {
        try {
            await fetch(`/api/distributors/${distributor.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_active: !distributor.is_active })
            })
            fetchDistributors()
        } catch (error) {
            console.error('Error toggling distributor:', error)
        }
    }

    const handleDelete = async (id) => {
        if (!confirm('هل أنت متأكد من حذف هذا الموزع؟')) return
        try {
            await fetch(`/api/distributors/${id}`, { method: 'DELETE' })
            fetchDistributors()
        } catch (error) {
            console.error('Error deleting distributor:', error)
        }
    }

    const openModal = (distributor = null) => {
        if (distributor) {
            setEditingDistributor(distributor)
            setFormData({
                name: distributor.name,
                phone: distributor.phone,
                location: distributor.location || ''
            })
        } else {
            setEditingDistributor(null)
            setFormData({ name: '', phone: '', location: '' })
        }
        setShowModal(true)
    }

    const closeModal = () => {
        setShowModal(false)
        setEditingDistributor(null)
        setFormData({ name: '', phone: '', location: '' })
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
                        <h1 className="text-3xl font-bold gold-text">الموزعين المعتمدين</h1>
                        <p className="text-white/60 mt-2">إدارة الموزعين والبائعين المعتمدين</p>
                    </div>
                </div>
                <button onClick={() => openModal()} className="btn-gold flex items-center gap-2">
                    <Plus className="w-5 h-5" />
                    إضافة موزع
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="stat-card">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-gold-500 to-gold-400 flex items-center justify-center">
                            <Users className="w-6 h-6 text-dark-500" />
                        </div>
                        <div>
                            <p className="text-white/60 text-sm">إجمالي الموزعين</p>
                            <p className="text-2xl font-bold text-white">{distributors.length}</p>
                        </div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-green-500 to-green-400 flex items-center justify-center">
                            <Check className="w-6 h-6 text-dark-500" />
                        </div>
                        <div>
                            <p className="text-white/60 text-sm">نشط</p>
                            <p className="text-2xl font-bold text-white">
                                {distributors.filter(d => d.is_active).length}
                            </p>
                        </div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-red-500 to-red-400 flex items-center justify-center">
                            <X className="w-6 h-6 text-dark-500" />
                        </div>
                        <div>
                            <p className="text-white/60 text-sm">غير نشط</p>
                            <p className="text-2xl font-bold text-white">
                                {distributors.filter(d => !d.is_active).length}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Distributors Grid */}
            {loading ? (
                <div className="flex items-center justify-center py-20">
                    <Loader2 className="w-10 h-10 text-gold-500 animate-spin" />
                </div>
            ) : distributors.length === 0 ? (
                <div className="card text-center py-20">
                    <Users className="w-16 h-16 text-white/20 mx-auto mb-4" />
                    <p className="text-white/50">لا يوجد موزعين بعد</p>
                    <button onClick={() => openModal()} className="btn-gold mt-4">
                        إضافة أول موزع
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {distributors.map((distributor) => (
                        <div
                            key={distributor.id}
                            className={`card border-2 transition-all ${distributor.is_active
                                ? 'border-gold-500/30 hover:border-gold-500/50'
                                : 'border-red-500/20 opacity-60'
                                }`}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-gold-500 to-gold-400 flex items-center justify-center">
                                    <span className="text-xl font-bold text-dark-500">
                                        {distributor.name.charAt(0)}
                                    </span>
                                </div>
                                <span className={`badge ${distributor.is_active ? 'badge-approved' : 'badge-rejected'}`}>
                                    {distributor.is_active ? 'نشط' : 'غير نشط'}
                                </span>
                            </div>

                            <h3 className="text-lg font-semibold text-white mb-3">{distributor.name}</h3>

                            <div className="space-y-2 text-sm">
                                <div className="flex items-center gap-2 text-white/70">
                                    <Phone className="w-4 h-4 text-gold-500" />
                                    <span className="font-mono">{distributor.phone}</span>
                                </div>
                                {distributor.location && (
                                    <div className="flex items-center gap-2 text-white/70">
                                        <MapPin className="w-4 h-4 text-gold-500" />
                                        <span>{distributor.location}</span>
                                    </div>
                                )}
                            </div>

                            <div className="flex items-center gap-2 mt-6 pt-4 border-t border-gold-500/20">
                                <button
                                    onClick={() => handleToggleActive(distributor)}
                                    className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors ${distributor.is_active
                                        ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                                        : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                                        }`}
                                >
                                    {distributor.is_active ? 'إيقاف' : 'تفعيل'}
                                </button>
                                <button
                                    onClick={() => openModal(distributor)}
                                    className="p-2 rounded-lg bg-gold-500/20 text-gold-400 hover:bg-gold-500/30 transition-colors"
                                >
                                    <Edit2 className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => handleDelete(distributor.id)}
                                    className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Add/Edit Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="card max-w-md w-full">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={closeModal}
                                    className="p-2 rounded-lg bg-gold-500/20 text-gold-400 hover:bg-gold-500/30 transition-colors"
                                    title="رجوع"
                                >
                                    <ArrowRight className="w-5 h-5" />
                                </button>
                                <h3 className="text-xl font-bold text-gold-500">
                                    {editingDistributor ? 'تعديل الموزع' : 'إضافة موزع جديد'}
                                </h3>
                            </div>
                            <button
                                onClick={closeModal}
                                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm text-white/70 mb-2">الاسم</label>
                                <input
                                    type="text"
                                    required
                                    className="input-gold"
                                    placeholder="اسم الموزع"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-white/70 mb-2">رقم الهاتف</label>
                                <input
                                    type="tel"
                                    required
                                    className="input-gold"
                                    placeholder="01xxxxxxxxx"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-white/70 mb-2">الموقع (اختياري)</label>
                                <input
                                    type="text"
                                    className="input-gold"
                                    placeholder="المنطقة أو العنوان"
                                    value={formData.location}
                                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                                />
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button type="submit" className="btn-gold flex-1">
                                    {editingDistributor ? 'حفظ التعديلات' : 'إضافة الموزع'}
                                </button>
                                <button
                                    type="button"
                                    onClick={closeModal}
                                    className="flex-1 py-3 px-6 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
                                >
                                    إلغاء
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Distributors
