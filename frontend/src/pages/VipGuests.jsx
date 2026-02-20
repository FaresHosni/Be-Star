import React, { useState, useEffect, useCallback } from 'react'
import {
    Crown, UserPlus, Trash2, Settings, Users, Save,
    CheckCircle, XCircle, HelpCircle, ThumbsUp, Clock,
    RefreshCw, Filter, X, Upload, Link, MessageSquare,
    Image as ImageIcon
} from 'lucide-react'
import { apiFetch } from '../utils/api'

const API = '/api/vip'

function VipGuests() {
    const [activeTab, setActiveTab] = useState('guests')
    const [guests, setGuests] = useState([])
    const [loading, setLoading] = useState(true)
    const [stats, setStats] = useState({})
    const [statusFilter, setStatusFilter] = useState('')
    const [showAddModal, setShowAddModal] = useState(false)
    const [newGuest, setNewGuest] = useState({ name: '', phone: '' })
    const [addLoading, setAddLoading] = useState(false)

    // Settings state
    const [settings, setSettings] = useState({
        invitation_text: '',
        invitation_image: '',
        invitation_link: '',
        reaction_reply: '',
        inquiry_reply: '',
    })
    const [settingsLoading, setSettingsLoading] = useState(false)
    const [settingsSaved, setSettingsSaved] = useState(false)

    const fetchGuests = useCallback(async () => {
        setLoading(true)
        try {
            const url = statusFilter ? `${API}/?status=${statusFilter}` : `${API}/`
            const res = await apiFetch(url)
            const data = await res.json()
            setGuests(data)
        } catch (e) { console.error(e) }
        setLoading(false)
    }, [statusFilter])

    const fetchStats = async () => {
        try {
            const res = await apiFetch(`${API}/stats`)
            const data = await res.json()
            setStats(data)
        } catch (e) { console.error(e) }
    }

    const fetchSettings = async () => {
        try {
            const res = await apiFetch(`${API}/settings`)
            const data = await res.json()
            setSettings(prev => ({ ...prev, ...data }))
        } catch (e) { console.error(e) }
    }

    useEffect(() => { fetchGuests() }, [fetchGuests])
    useEffect(() => { fetchStats(); fetchSettings() }, [])

    const addGuest = async () => {
        if (!newGuest.name || !newGuest.phone) return
        setAddLoading(true)
        try {
            const res = await apiFetch(`${API}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newGuest),
            })
            if (res.ok) {
                setShowAddModal(false)
                setNewGuest({ name: '', phone: '' })
                fetchGuests()
                fetchStats()
            } else {
                const err = await res.json()
                alert(err.detail || 'حدث خطأ')
            }
        } catch (e) { console.error(e) }
        setAddLoading(false)
    }

    const deleteGuest = async (id) => {
        if (!window.confirm('هل أنت متأكد من حذف هذه الشخصية؟')) return
        try {
            await apiFetch(`${API}/${id}`, { method: 'DELETE' })
            fetchGuests()
            fetchStats()
        } catch (e) { console.error(e) }
    }

    const saveSettings = async () => {
        setSettingsLoading(true)
        try {
            await apiFetch(`${API}/settings`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings),
            })
            setSettingsSaved(true)
            setTimeout(() => setSettingsSaved(false), 2000)
        } catch (e) { console.error(e) }
        setSettingsLoading(false)
    }

    const statusConfig = {
        will_attend: { label: '🟢 سيحضر', color: 'text-green-400', bg: 'bg-green-500/15 border-green-500/30' },
        not_attending: { label: '🔴 اعتذر', color: 'text-red-400', bg: 'bg-red-500/15 border-red-500/30' },
        inquiring: { label: '🟡 يستفسر', color: 'text-yellow-400', bg: 'bg-yellow-500/15 border-yellow-500/30' },
        reacted: { label: '💜 تفاعل', color: 'text-purple-400', bg: 'bg-purple-500/15 border-purple-500/30' },
        invited: { label: '📩 تم الدعوة', color: 'text-white/50', bg: 'bg-white/5 border-white/10' },
        no_response: { label: '⚪ لم يرد', color: 'text-white/40', bg: 'bg-white/5 border-white/10' },
    }

    const getStatusBadge = (status) => {
        const cfg = statusConfig[status] || statusConfig.invited
        return (
            <span className={`badge border ${cfg.bg}`}>
                {cfg.label}
            </span>
        )
    }

    // Filter options
    const filterOptions = [
        { value: '', label: 'الكل' },
        { value: 'will_attend', label: '🟢 سيحضرون' },
        { value: 'not_attending', label: '🔴 اعتذروا' },
        { value: 'inquiring', label: '🟡 يستفسرون' },
        { value: 'reacted', label: '💜 تفاعلوا' },
        { value: 'invited', label: '📩 مدعوون' },
        { value: 'no_response', label: '⚪ لم يردوا' },
    ]

    return (
        <div className="space-y-6 fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold gold-text">👑 كبار الزوار (VIP)</h1>
                    <p className="text-white/60 mt-1">إدارة الشخصيات المهمة ومتابعة ردود الدعوات</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveTab('guests')}
                        className={`px-4 py-2 rounded-lg text-sm transition-all ${activeTab === 'guests'
                                ? 'bg-gold-500/20 text-gold-400 border border-gold-500/40'
                                : 'bg-white/5 text-white/50 border border-white/10 hover:bg-white/10'
                            }`}
                    >
                        <Users className="w-4 h-4 inline-block ml-1" />
                        القائمة
                    </button>
                    <button
                        onClick={() => setActiveTab('settings')}
                        className={`px-4 py-2 rounded-lg text-sm transition-all ${activeTab === 'settings'
                                ? 'bg-gold-500/20 text-gold-400 border border-gold-500/40'
                                : 'bg-white/5 text-white/50 border border-white/10 hover:bg-white/10'
                            }`}
                    >
                        <Settings className="w-4 h-4 inline-block ml-1" />
                        الإعدادات
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <div className="stat-card cursor-pointer hover:border-white/30" onClick={() => { setStatusFilter(''); setActiveTab('guests') }}>
                    <p className="text-white/50 text-xs">الإجمالي</p>
                    <p className="text-2xl font-bold text-white mt-1">{stats.total || 0}</p>
                </div>
                <div className="stat-card cursor-pointer hover:border-green-500/50" onClick={() => { setStatusFilter('will_attend'); setActiveTab('guests') }}>
                    <p className="text-green-400/70 text-xs">🟢 سيحضرون</p>
                    <p className="text-2xl font-bold text-green-400 mt-1">{stats.will_attend || 0}</p>
                </div>
                <div className="stat-card cursor-pointer hover:border-red-500/50" onClick={() => { setStatusFilter('not_attending'); setActiveTab('guests') }}>
                    <p className="text-red-400/70 text-xs">🔴 اعتذروا</p>
                    <p className="text-2xl font-bold text-red-400 mt-1">{stats.not_attending || 0}</p>
                </div>
                <div className="stat-card cursor-pointer hover:border-yellow-500/50" onClick={() => { setStatusFilter('inquiring'); setActiveTab('guests') }}>
                    <p className="text-yellow-400/70 text-xs">🟡 يستفسرون</p>
                    <p className="text-2xl font-bold text-yellow-400 mt-1">{stats.inquiring || 0}</p>
                </div>
                <div className="stat-card cursor-pointer hover:border-purple-500/50" onClick={() => { setStatusFilter('reacted'); setActiveTab('guests') }}>
                    <p className="text-purple-400/70 text-xs">💜 تفاعلوا</p>
                    <p className="text-2xl font-bold text-purple-400 mt-1">{stats.reacted || 0}</p>
                </div>
                <div className="stat-card cursor-pointer hover:border-white/30" onClick={() => { setStatusFilter(''); setActiveTab('guests') }}>
                    <p className="text-white/40 text-xs">🔄 غيّروا رأيهم</p>
                    <p className="text-2xl font-bold text-white/70 mt-1">{stats.changed_mind || 0}</p>
                </div>
            </div>

            {/* ═══ TAB: Guests List ═══ */}
            {activeTab === 'guests' && (
                <>
                    {/* Filter + Add Button */}
                    <div className="flex items-center justify-between gap-3 flex-wrap">
                        <div className="flex items-center gap-2">
                            <Filter className="w-5 h-5 text-white/40" />
                            <div className="flex gap-2 flex-wrap">
                                {filterOptions.map(f => (
                                    <button
                                        key={f.value}
                                        onClick={() => setStatusFilter(f.value)}
                                        className={`px-3 py-1.5 rounded-lg text-xs transition-all ${statusFilter === f.value
                                            ? 'bg-gold-500/20 text-gold-400 border border-gold-500/40'
                                            : 'bg-white/5 text-white/50 border border-white/10 hover:bg-white/10'
                                            }`}
                                    >
                                        {f.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <button
                            onClick={() => setShowAddModal(true)}
                            className="btn-gold flex items-center gap-2"
                        >
                            <UserPlus className="w-4 h-4" />
                            إضافة شخصية
                        </button>
                    </div>

                    {/* Guests Table */}
                    <div className="glass-card overflow-hidden">
                        {loading ? (
                            <div className="p-12 text-center text-white/40">
                                <div className="animate-spin w-8 h-8 border-2 border-gold-500/30 border-t-gold-500 rounded-full mx-auto mb-3"></div>
                                جاري التحميل...
                            </div>
                        ) : guests.length === 0 ? (
                            <div className="p-12 text-center text-white/40">
                                <Crown className="w-12 h-12 mx-auto mb-3 opacity-30" />
                                <p>لا توجد شخصيات مهمة بعد</p>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-white/10">
                                            <th className="text-right p-4 text-white/50 text-sm font-medium">الاسم</th>
                                            <th className="text-right p-4 text-white/50 text-sm font-medium">الرقم</th>
                                            <th className="text-right p-4 text-white/50 text-sm font-medium">الحالة</th>
                                            <th className="text-right p-4 text-white/50 text-sm font-medium">آخر تفاعل</th>
                                            <th className="text-right p-4 text-white/50 text-sm font-medium">تغيير رأي</th>
                                            <th className="text-center p-4 text-white/50 text-sm font-medium">تحكم</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {guests.map(g => (
                                            <tr key={g.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                                <td className="p-4">
                                                    <div className="flex items-center gap-2">
                                                        <Crown className="w-4 h-4 text-gold-400" />
                                                        <span className="text-white font-medium">{g.name}</span>
                                                    </div>
                                                </td>
                                                <td className="p-4 text-white/70 font-mono text-sm" dir="ltr">{g.phone}</td>
                                                <td className="p-4">{getStatusBadge(g.status)}</td>
                                                <td className="p-4 text-white/50 text-sm">
                                                    {g.last_interaction
                                                        ? new Date(g.last_interaction).toLocaleString('ar-EG', { dateStyle: 'short', timeStyle: 'short' })
                                                        : '—'}
                                                </td>
                                                <td className="p-4 text-center">
                                                    {g.changed_mind ? (
                                                        <span className="text-orange-400">🔄 نعم</span>
                                                    ) : (
                                                        <span className="text-white/30">—</span>
                                                    )}
                                                </td>
                                                <td className="p-4 text-center">
                                                    <button
                                                        onClick={() => deleteGuest(g.id)}
                                                        className="p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                                                        title="حذف"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </>
            )}

            {/* ═══ TAB: Settings ═══ */}
            {activeTab === 'settings' && (
                <div className="space-y-6">
                    {/* Invitation Settings */}
                    <div className="glass-card p-6 space-y-4">
                        <h3 className="text-lg font-semibold gold-text flex items-center gap-2">
                            <MessageSquare className="w-5 h-5" />
                            إعدادات الدعوة
                        </h3>

                        <div>
                            <label className="block text-white/60 text-sm mb-2">نص الدعوة</label>
                            <textarea
                                value={settings.invitation_text}
                                onChange={e => setSettings(s => ({ ...s, invitation_text: e.target.value }))}
                                rows={4}
                                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-white/30 focus:border-gold-500/50 focus:outline-none resize-none"
                                placeholder="اكتب نص الدعوة هنا..."
                                dir="rtl"
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-white/60 text-sm mb-2">
                                    <Link className="w-4 h-4 inline-block ml-1" />
                                    رابط الإيفنت
                                </label>
                                <input
                                    type="url"
                                    value={settings.invitation_link}
                                    onChange={e => setSettings(s => ({ ...s, invitation_link: e.target.value }))}
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-white/30 focus:border-gold-500/50 focus:outline-none"
                                    placeholder="https://..."
                                    dir="ltr"
                                />
                            </div>
                            <div>
                                <label className="block text-white/60 text-sm mb-2">
                                    <ImageIcon className="w-4 h-4 inline-block ml-1" />
                                    رابط صورة الدعوة
                                </label>
                                <input
                                    type="url"
                                    value={settings.invitation_image}
                                    onChange={e => setSettings(s => ({ ...s, invitation_image: e.target.value }))}
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-white/30 focus:border-gold-500/50 focus:outline-none"
                                    placeholder="https://..."
                                    dir="ltr"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Auto Reply Settings */}
                    <div className="glass-card p-6 space-y-4">
                        <h3 className="text-lg font-semibold gold-text flex items-center gap-2">
                            <RefreshCw className="w-5 h-5" />
                            الردود التلقائية
                        </h3>

                        <div>
                            <label className="block text-white/60 text-sm mb-2">نص الرد على التفاعل (ريأكشن) 👍</label>
                            <textarea
                                value={settings.reaction_reply}
                                onChange={e => setSettings(s => ({ ...s, reaction_reply: e.target.value }))}
                                rows={3}
                                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-white/30 focus:border-gold-500/50 focus:outline-none resize-none"
                                placeholder="النص اللي هيتبعت تلقائياً لما حد يعمل ريأكشن..."
                                dir="rtl"
                            />
                        </div>

                        <div>
                            <label className="block text-white/60 text-sm mb-2">نص الرد على الاستفسار 🟡</label>
                            <textarea
                                value={settings.inquiry_reply}
                                onChange={e => setSettings(s => ({ ...s, inquiry_reply: e.target.value }))}
                                rows={3}
                                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-white/30 focus:border-gold-500/50 focus:outline-none resize-none"
                                placeholder="النص اللي هيتبعت تلقائياً لما حد يستفسر عن التفاصيل..."
                                dir="rtl"
                            />
                        </div>
                    </div>

                    {/* Save Button */}
                    <div className="flex justify-end">
                        <button
                            onClick={saveSettings}
                            disabled={settingsLoading}
                            className={`btn-gold flex items-center gap-2 px-6 py-3 ${settingsSaved ? 'bg-green-500/20 border-green-500/40' : ''}`}
                        >
                            {settingsSaved ? (
                                <>
                                    <CheckCircle className="w-5 h-5 text-green-400" />
                                    <span className="text-green-400">تم الحفظ ✅</span>
                                </>
                            ) : (
                                <>
                                    <Save className="w-5 h-5" />
                                    {settingsLoading ? 'جاري الحفظ...' : 'حفظ الإعدادات'}
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}

            {/* ═══ Add Guest Modal ═══ */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={() => setShowAddModal(false)}>
                    <div className="glass-card p-6 w-full max-w-md mx-4 space-y-4" onClick={e => e.stopPropagation()}>
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold gold-text flex items-center gap-2">
                                <Crown className="w-5 h-5" />
                                إضافة شخصية مهمة
                            </h3>
                            <button onClick={() => setShowAddModal(false)} className="text-white/40 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div>
                            <label className="block text-white/60 text-sm mb-2">الاسم</label>
                            <input
                                type="text"
                                value={newGuest.name}
                                onChange={e => setNewGuest(g => ({ ...g, name: e.target.value }))}
                                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-white/30 focus:border-gold-500/50 focus:outline-none"
                                placeholder="اسم الشخصية المهمة"
                                dir="rtl"
                                autoFocus
                            />
                        </div>

                        <div>
                            <label className="block text-white/60 text-sm mb-2">رقم الواتساب</label>
                            <input
                                type="tel"
                                value={newGuest.phone}
                                onChange={e => setNewGuest(g => ({ ...g, phone: e.target.value }))}
                                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-white/30 focus:border-gold-500/50 focus:outline-none"
                                placeholder="01XXXXXXXXX"
                                dir="ltr"
                            />
                        </div>

                        <div className="flex gap-3 justify-end pt-2">
                            <button
                                onClick={() => setShowAddModal(false)}
                                className="px-4 py-2 rounded-lg bg-white/5 text-white/60 hover:bg-white/10 transition-colors"
                            >
                                إلغاء
                            </button>
                            <button
                                onClick={addGuest}
                                disabled={addLoading || !newGuest.name || !newGuest.phone}
                                className="btn-gold px-6 py-2 flex items-center gap-2"
                            >
                                <UserPlus className="w-4 h-4" />
                                {addLoading ? 'جاري الإضافة...' : 'إضافة + إرسال الدعوة'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default VipGuests
