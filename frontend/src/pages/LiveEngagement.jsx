import React, { useState, useEffect, useCallback } from 'react'
import {
    Search,
    Send,
    Trash2,
    EyeOff,
    Eye,
    CheckSquare,
    Square,
    Radio,
    Image,
    Link,
    FileText,
    Mail,
    X,
    Loader2,
    RefreshCw,
    Users,
    ChevronDown,
    ChevronUp,
    Undo2,
    Upload
} from 'lucide-react'

const API = '/api/engagement'

function LiveEngagement() {
    const [attendees, setAttendees] = useState([])
    const [hiddenAttendees, setHiddenAttendees] = useState([])
    const [selected, setSelected] = useState(new Set())
    const [search, setSearch] = useState('')
    const [loading, setLoading] = useState(true)
    const [showHidden, setShowHidden] = useState(false)
    const [showSendModal, setShowSendModal] = useState(false)
    const [sendType, setSendType] = useState('text')
    const [sendContent, setSendContent] = useState('')
    const [sendCaption, setSendCaption] = useState('')
    const [sendTitle, setSendTitle] = useState('')
    const [sendDescription, setSendDescription] = useState('')
    const [sendUrl, setSendUrl] = useState('')
    const [sending, setSending] = useState(false)
    const [imageFile, setImageFile] = useState(null)
    const [imagePreview, setImagePreview] = useState(null)
    const [toast, setToast] = useState(null)

    const showToast = (msg, type = 'success') => {
        setToast({ msg, type })
        setTimeout(() => setToast(null), 3000)
    }

    const fetchAttendees = useCallback(async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API}/attendees`)
            const data = await res.json()
            setAttendees(data.attendees || [])
        } catch (e) {
            console.error(e)
        }
        setLoading(false)
    }, [])

    const fetchHidden = useCallback(async () => {
        try {
            const res = await fetch(`${API}/hidden`)
            const data = await res.json()
            setHiddenAttendees(data.hidden || [])
        } catch (e) {
            console.error(e)
        }
    }, [])

    useEffect(() => {
        fetchAttendees()
        fetchHidden()
    }, [fetchAttendees, fetchHidden])

    // Filtering
    const filtered = attendees.filter(a =>
        (a.guest_name || '').toLowerCase().includes(search.toLowerCase()) ||
        (a.phone || '').includes(search) ||
        (a.email || '').toLowerCase().includes(search.toLowerCase())
    )

    // Selection
    const toggleSelect = (id) => {
        const next = new Set(selected)
        next.has(id) ? next.delete(id) : next.add(id)
        setSelected(next)
    }

    const toggleAll = () => {
        if (selected.size === filtered.length) {
            setSelected(new Set())
        } else {
            setSelected(new Set(filtered.map(a => a.id)))
        }
    }

    const selectByType = (type) => {
        const ids = filtered.filter(a => a.ticket_type === type).map(a => a.id)
        setSelected(new Set(ids))
    }

    const clearSelection = () => setSelected(new Set())

    // Get phones for selected
    const getSelectedPhones = () => {
        return attendees.filter(a => selected.has(a.id)).map(a => a.phone).filter(p => p && p !== '—')
    }

    // Bulk Actions
    const handleHide = async () => {
        const ids = [...selected]
        try {
            const res = await fetch(`${API}/hide`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticket_ids: ids })
            })
            const data = await res.json()
            showToast(data.message)
            setSelected(new Set())
            fetchAttendees()
            fetchHidden()
        } catch (e) {
            showToast('حدث خطأ', 'error')
        }
    }

    const handleUnhide = async (ids) => {
        try {
            const res = await fetch(`${API}/unhide`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticket_ids: ids })
            })
            const data = await res.json()
            showToast(data.message)
            fetchAttendees()
            fetchHidden()
        } catch (e) {
            showToast('حدث خطأ', 'error')
        }
    }

    const handleDelete = async () => {
        if (!confirm('هل أنت متأكد من الحذف النهائي للتذاكر المرفوضة المحددة؟')) return
        const ids = [...selected]
        try {
            const res = await fetch(`${API}/delete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticket_ids: ids })
            })
            const data = await res.json()
            showToast(data.message)
            setSelected(new Set())
            fetchAttendees()
        } catch (e) {
            showToast('حدث خطأ', 'error')
        }
    }

    // Image Upload
    const handleImageUpload = (e) => {
        const file = e.target.files[0]
        if (!file) return
        setImageFile(file)

        const reader = new FileReader()
        reader.onloadend = () => {
            setImagePreview(reader.result)
            // Extract pure base64
            const base64 = reader.result.split(',')[1]
            setSendContent(base64)
        }
        reader.readAsDataURL(file)
    }

    // Send Message
    const handleSend = async () => {
        const phones = getSelectedPhones()
        if (phones.length === 0) {
            showToast('لم يتم تحديد أرقام صالحة', 'error')
            return
        }

        setSending(true)
        try {
            const payload = {
                phones,
                type: sendType,
                content: sendContent,
                caption: sendCaption,
                title: sendTitle,
                description: sendDescription,
                url: sendUrl
            }

            const res = await fetch(`${API}/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            const data = await res.json()
            showToast(data.message)
            resetSendForm()
            setShowSendModal(false)
        } catch (e) {
            showToast('حدث خطأ في الإرسال', 'error')
        }
        setSending(false)
    }

    const resetSendForm = () => {
        setSendContent('')
        setSendCaption('')
        setSendTitle('')
        setSendDescription('')
        setSendUrl('')
        setImageFile(null)
        setImagePreview(null)
        setSendType('text')
    }

    // Status Badge
    const getStatusBadge = (status) => {
        const map = {
            'approved': { label: 'مقبولة', cls: 'badge-approved' },
            'activated': { label: 'مفعلة', cls: 'badge-approved' },
            'payment_submitted': { label: 'بانتظار القبول', cls: 'badge-pending' },
            'rejected': { label: 'مرفوضة', cls: 'badge-rejected' },
        }
        const s = map[status] || { label: status, cls: 'badge-pending' }
        return <span className={`badge ${s.cls}`}>{s.label}</span>
    }

    const getTypeBadge = (type) => {
        return type === 'VIP'
            ? <span className="badge badge-vip">VIP</span>
            : <span className="badge badge-student">Student</span>
    }

    return (
        <div className="fade-in">
            {/* Toast */}
            {toast && (
                <div className={`fixed top-6 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-xl text-sm font-semibold shadow-lg ${toast.type === 'error' ? 'bg-red-500/90 text-white' : 'bg-green-500/90 text-white'
                    }`} style={{ animation: 'fadeIn 0.3s ease' }}>
                    {toast.msg}
                </div>
            )}

            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold gold-text flex items-center gap-3">
                        <Radio className="w-8 h-8" />
                        إدارة التفاعل المباشر
                    </h1>
                    <p className="text-white/50 mt-1">{attendees.length} حاضر مسجل</p>
                </div>
                <div className="flex gap-3">
                    <button onClick={() => setShowHidden(!showHidden)}
                        className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gold-500/30 text-gold-400 hover:bg-gold-500/10 transition-all">
                        {showHidden ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                        {showHidden ? 'إخفاء المخفيين' : `المخفيين (${hiddenAttendees.length})`}
                    </button>
                    <button onClick={() => { fetchAttendees(); fetchHidden() }}
                        className="flex items-center gap-2 px-4 py-2 rounded-xl border border-white/20 text-white/70 hover:bg-white/10 transition-all">
                        <RefreshCw className="w-4 h-4" />
                        تحديث
                    </button>
                </div>
            </div>

            {/* Search */}
            <div className="relative mb-6">
                <Search className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 w-5 h-5" />
                <input
                    type="text"
                    placeholder="بحث بالاسم أو الرقم أو الإيميل..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="input-gold w-full pr-12"
                />
            </div>

            {/* Quick Select Filters */}
            <div className="flex items-center gap-3 mb-6">
                <span className="text-white/40 text-sm">تحديد سريع:</span>
                <button onClick={toggleAll}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-sm transition-all ${selected.size === filtered.length && filtered.length > 0
                        ? 'border-gold-500 bg-gold-500/15 text-gold-400'
                        : 'border-white/15 text-white/50 hover:border-white/30 hover:text-white/70'
                        }`}>
                    <CheckSquare className="w-4 h-4" />
                    الكل ({filtered.length})
                </button>
                <button onClick={() => selectByType('VIP')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-sm transition-all ${selected.size > 0 && [...selected].every(id => filtered.find(a => a.id === id)?.ticket_type === 'VIP')
                        ? 'border-yellow-500 bg-yellow-500/15 text-yellow-400'
                        : 'border-yellow-500/20 text-yellow-400/60 hover:border-yellow-500/40 hover:text-yellow-400'
                        }`}>
                    ⭐ VIP ({filtered.filter(a => a.ticket_type === 'VIP').length})
                </button>
                <button onClick={() => selectByType('Student')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-sm transition-all ${selected.size > 0 && [...selected].every(id => filtered.find(a => a.id === id)?.ticket_type === 'Student')
                        ? 'border-blue-500 bg-blue-500/15 text-blue-400'
                        : 'border-blue-500/20 text-blue-400/60 hover:border-blue-500/40 hover:text-blue-400'
                        }`}>
                    🎓 طلاب ({filtered.filter(a => a.ticket_type === 'Student').length})
                </button>
                {selected.size > 0 && (
                    <button onClick={clearSelection}
                        className="flex items-center gap-1 px-3 py-2 rounded-xl text-sm text-red-400/70 hover:text-red-400 hover:bg-red-500/10 transition-all">
                        <X className="w-4 h-4" /> إلغاء التحديد
                    </button>
                )}
            </div>

            {/* Bulk Toolbar */}
            {selected.size > 0 && (
                <div className="card mb-6 flex items-center justify-between" style={{ borderColor: 'rgba(212, 175, 55, 0.5)' }}>
                    <span className="text-gold-400 font-semibold">
                        تم تحديد {selected.size} شخص
                    </span>
                    <div className="flex gap-3">
                        <button onClick={() => setShowSendModal(true)}
                            className="btn-gold flex items-center gap-2 text-sm px-4 py-2">
                            <Send className="w-4 h-4" /> إرسال رسالة
                        </button>
                        <button onClick={handleHide}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-orange-500/30 text-orange-400 hover:bg-orange-500/10 transition-all text-sm">
                            <EyeOff className="w-4 h-4" /> إخفاء
                        </button>
                        <button onClick={handleDelete}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-all text-sm">
                            <Trash2 className="w-4 h-4" /> حذف نهائي
                        </button>
                    </div>
                </div>
            )}

            {/* Main Table */}
            <div className="card overflow-hidden" style={{ padding: 0 }}>
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <Loader2 className="w-8 h-8 text-gold-400 animate-spin" />
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="text-center py-20 text-white/40">
                        <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
                        <p>لا يوجد حضور مسجلين</p>
                    </div>
                ) : (
                    <table className="table-gold">
                        <thead>
                            <tr>
                                <th style={{ width: 50 }}>
                                    <button onClick={toggleAll} className="text-gold-400 hover:text-gold-300">
                                        {selected.size === filtered.length && filtered.length > 0
                                            ? <CheckSquare className="w-5 h-5" />
                                            : <Square className="w-5 h-5" />
                                        }
                                    </button>
                                </th>
                                <th>الاسم</th>
                                <th>الرقم</th>
                                <th>الإيميل</th>
                                <th>النوع</th>
                                <th>الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map(a => (
                                <tr key={a.id} className={selected.has(a.id) ? 'bg-gold-500/5' : ''}>
                                    <td>
                                        <button onClick={() => toggleSelect(a.id)} className="text-white/60 hover:text-gold-400">
                                            {selected.has(a.id)
                                                ? <CheckSquare className="w-5 h-5 text-gold-400" />
                                                : <Square className="w-5 h-5" />
                                            }
                                        </button>
                                    </td>
                                    <td className="font-semibold">{a.guest_name}</td>
                                    <td className="text-white/70 font-mono text-sm">{a.phone}</td>
                                    <td className="text-white/50 text-sm">{a.email}</td>
                                    <td>{getTypeBadge(a.ticket_type)}</td>
                                    <td>{getStatusBadge(a.status)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Hidden Attendees Panel */}
            {showHidden && hiddenAttendees.length > 0 && (
                <div className="card mt-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-orange-400 flex items-center gap-2">
                            <EyeOff className="w-5 h-5" />
                            الحضور المخفيين ({hiddenAttendees.length})
                        </h3>
                        <button onClick={() => handleUnhide(hiddenAttendees.map(a => a.id))}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-green-500/30 text-green-400 hover:bg-green-500/10 transition-all text-sm">
                            <Undo2 className="w-4 h-4" /> استعادة الكل
                        </button>
                    </div>
                    <table className="table-gold">
                        <thead>
                            <tr>
                                <th>الاسم</th>
                                <th>الرقم</th>
                                <th>النوع</th>
                                <th>إجراء</th>
                            </tr>
                        </thead>
                        <tbody>
                            {hiddenAttendees.map(a => (
                                <tr key={a.id}>
                                    <td className="font-semibold">{a.guest_name}</td>
                                    <td className="text-white/70 font-mono text-sm">{a.phone}</td>
                                    <td>{getTypeBadge(a.ticket_type)}</td>
                                    <td>
                                        <button onClick={() => handleUnhide([a.id])}
                                            className="flex items-center gap-1 px-3 py-1 rounded-lg text-sm border border-green-500/30 text-green-400 hover:bg-green-500/10 transition-all">
                                            <Undo2 className="w-4 h-4" /> استعادة
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Send Message Modal */}
            {showSendModal && (
                <div className="modal-2026" onClick={() => setShowSendModal(false)}>
                    <div className="glass-card-2026 w-full max-w-lg p-8" onClick={e => e.stopPropagation()}>
                        {/* Header */}
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold gold-text">إرسال رسالة</h2>
                            <button onClick={() => { setShowSendModal(false); resetSendForm() }}
                                className="p-2 rounded-lg hover:bg-white/10 text-white/50">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <p className="text-white/50 text-sm mb-6">
                            سيتم الإرسال إلى <span className="text-gold-400 font-bold">{getSelectedPhones().length}</span> شخص
                        </p>

                        {/* Type Tabs */}
                        <div className="grid grid-cols-4 gap-2 mb-6">
                            {[
                                { key: 'text', label: 'نص', icon: FileText },
                                { key: 'image', label: 'صورة', icon: Image },
                                { key: 'invitation', label: 'دعوة', icon: Mail },
                                { key: 'link', label: 'رابط', icon: Link },
                            ].map(tab => {
                                const Icon = tab.icon
                                return (
                                    <button
                                        key={tab.key}
                                        onClick={() => { setSendType(tab.key); setSendContent(''); setImagePreview(null); setImageFile(null) }}
                                        className={`flex flex-col items-center gap-1 p-3 rounded-xl border transition-all text-sm ${sendType === tab.key
                                            ? 'border-gold-500 bg-gold-500/10 text-gold-400'
                                            : 'border-white/10 text-white/50 hover:border-white/30'
                                            }`}
                                    >
                                        <Icon className="w-5 h-5" />
                                        {tab.label}
                                    </button>
                                )
                            })}
                        </div>

                        {/* Dynamic Fields */}
                        <div className="space-y-4">
                            {sendType === 'text' && (
                                <textarea
                                    rows={4}
                                    placeholder="اكتب الرسالة هنا..."
                                    value={sendContent}
                                    onChange={e => setSendContent(e.target.value)}
                                    className="input-gold w-full resize-none"
                                />
                            )}

                            {sendType === 'image' && (
                                <>
                                    <label className="flex flex-col items-center justify-center gap-3 p-6 rounded-xl border-2 border-dashed border-gold-500/30 hover:border-gold-500/50 cursor-pointer transition-all">
                                        {imagePreview ? (
                                            <img src={imagePreview} alt="Preview" className="max-h-40 rounded-lg" />
                                        ) : (
                                            <>
                                                <Upload className="w-8 h-8 text-gold-400" />
                                                <span className="text-white/50 text-sm">اضغط لرفع صورة</span>
                                            </>
                                        )}
                                        <input type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
                                    </label>
                                    <input
                                        type="text"
                                        placeholder="تعليق على الصورة (اختياري)"
                                        value={sendCaption}
                                        onChange={e => setSendCaption(e.target.value)}
                                        className="input-gold w-full"
                                    />
                                </>
                            )}

                            {sendType === 'invitation' && (
                                <>
                                    <input
                                        type="text"
                                        placeholder="عنوان الدعوة"
                                        value={sendTitle}
                                        onChange={e => setSendTitle(e.target.value)}
                                        className="input-gold w-full"
                                    />
                                    <textarea
                                        rows={3}
                                        placeholder="تفاصيل الدعوة..."
                                        value={sendDescription}
                                        onChange={e => setSendDescription(e.target.value)}
                                        className="input-gold w-full resize-none"
                                    />
                                    <input
                                        type="url"
                                        placeholder="رابط (اختياري)"
                                        value={sendUrl}
                                        onChange={e => setSendUrl(e.target.value)}
                                        className="input-gold w-full"
                                        dir="ltr"
                                    />
                                </>
                            )}

                            {sendType === 'link' && (
                                <>
                                    <input
                                        type="url"
                                        placeholder="الرابط"
                                        value={sendUrl}
                                        onChange={e => setSendUrl(e.target.value)}
                                        className="input-gold w-full"
                                        dir="ltr"
                                    />
                                    <input
                                        type="text"
                                        placeholder="عنوان الرابط"
                                        value={sendTitle}
                                        onChange={e => setSendTitle(e.target.value)}
                                        className="input-gold w-full"
                                    />
                                    <input
                                        type="text"
                                        placeholder="وصف (اختياري)"
                                        value={sendDescription}
                                        onChange={e => setSendDescription(e.target.value)}
                                        className="input-gold w-full"
                                    />
                                </>
                            )}
                        </div>

                        {/* Actions */}
                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={handleSend}
                                disabled={sending || (!sendContent && !sendUrl)}
                                className="btn-gold flex-1 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {sending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                                {sending ? 'جاري الإرسال...' : 'إرسال'}
                            </button>
                            <button onClick={() => { setShowSendModal(false); resetSendForm() }}
                                className="btn-cancel-2026 px-6">
                                إلغاء
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default LiveEngagement
