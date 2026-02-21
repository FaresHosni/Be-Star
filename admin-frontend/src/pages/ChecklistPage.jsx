import React, { useState, useEffect, useCallback } from 'react'
import {
    CheckSquare, Plus, Trash2, Edit3, Save, X, Settings,
    Phone, Hash, User, ChevronRight, ChevronLeft, Calendar
} from 'lucide-react'
import { apiFetch } from '../utils/api'

const API = '/api/checklist'

// ─── Helper: حساب بداية الأسبوع (السبت) ───
function getWeekStart(dateObj) {
    const d = new Date(dateObj)
    const day = d.getDay() // 0=Sun, 6=Sat
    const diff = (day === 6) ? 0 : (day + 1)
    d.setDate(d.getDate() - diff)
    return d
}

function formatDate(d) {
    return d.toISOString().split('T')[0]
}

const DAY_NAMES = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']

function ChecklistPage() {
    const [selectedDate, setSelectedDate] = useState(formatDate(new Date()))
    const [items, setItems] = useState([])
    const [loading, setLoading] = useState(true)
    const [newTitle, setNewTitle] = useState('')
    const [newDesc, setNewDesc] = useState('')
    const [editingId, setEditingId] = useState(null)
    const [editTitle, setEditTitle] = useState('')
    const [editDesc, setEditDesc] = useState('')
    const [showSettings, setShowSettings] = useState(false)
    const [settings, setSettings] = useState({ manager_phone: '', manager_name: '', whatsapp_group_id: '' })
    const [savingSettings, setSavingSettings] = useState(false)
    const [settingsMsg, setSettingsMsg] = useState(null)
    const [weekProgress, setWeekProgress] = useState([])

    // ─── Fetch ───
    const fetchItems = useCallback(async () => {
        setLoading(true)
        try {
            const res = await apiFetch(`${API}/?date_filter=${selectedDate}`)
            const data = await res.json()
            setItems(data)
        } catch (e) { console.error(e) }
        setLoading(false)
    }, [selectedDate])

    const fetchWeekProgress = useCallback(async () => {
        try {
            const weekStart = getWeekStart(new Date(selectedDate))
            const res = await apiFetch(`${API}/week?start_date=${formatDate(weekStart)}`)
            const data = await res.json()
            setWeekProgress(data)
        } catch (e) { console.error(e) }
    }, [selectedDate])

    const fetchSettings = async () => {
        try {
            const res = await apiFetch(`${API}/settings`)
            const data = await res.json()
            setSettings({
                manager_phone: data.manager_phone || '',
                manager_name: data.manager_name || '',
                whatsapp_group_id: data.whatsapp_group_id || '',
            })
        } catch (e) { console.error(e) }
    }

    useEffect(() => { fetchItems(); fetchWeekProgress() }, [fetchItems, fetchWeekProgress])
    useEffect(() => { fetchSettings() }, [])

    // ─── Actions ───
    const addItem = async () => {
        if (!newTitle.trim()) return
        try {
            await apiFetch(`${API}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle, description: newDesc || null, date: selectedDate })
            })
            setNewTitle('')
            setNewDesc('')
            fetchItems()
            fetchWeekProgress()
        } catch (e) { console.error(e) }
    }

    const toggleItem = async (item) => {
        try {
            await apiFetch(`${API}/${item.id}/toggle`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    is_completed: !item.is_completed,
                    completed_by_name: 'الأدمن (المنصة)',
                })
            })
            fetchItems()
            fetchWeekProgress()
        } catch (e) { console.error(e) }
    }

    const deleteItem = async (id) => {
        if (!confirm('هل أنت متأكد من حذف هذه المهمة؟')) return
        try {
            await apiFetch(`${API}/${id}`, { method: 'DELETE' })
            fetchItems()
            fetchWeekProgress()
        } catch (e) { console.error(e) }
    }

    const saveEdit = async (id) => {
        try {
            await apiFetch(`${API}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: editTitle, description: editDesc })
            })
            setEditingId(null)
            fetchItems()
        } catch (e) { console.error(e) }
    }

    const saveSettings = async () => {
        setSavingSettings(true)
        setSettingsMsg(null)
        try {
            const res = await apiFetch(`${API}/settings`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            })
            if (res.ok) {
                setSettingsMsg({ type: 'success', text: 'تم الحفظ بنجاح ✅' })
            } else {
                setSettingsMsg({ type: 'error', text: 'فشل الحفظ ❌' })
            }
            setSavingSettings(false)
            setTimeout(() => setSettingsMsg(null), 3000)
        } catch (e) {
            console.error(e)
            setSettingsMsg({ type: 'error', text: 'خطأ في الاتصال ❌' })
            setSavingSettings(false)
            setTimeout(() => setSettingsMsg(null), 3000)
        }
    }

    // ─── Date Navigation ───
    const changeDate = (offset) => {
        const d = new Date(selectedDate)
        d.setDate(d.getDate() + offset)
        setSelectedDate(formatDate(d))
    }

    const todayDate = formatDate(new Date())
    const completed = items.filter(i => i.is_completed).length
    const total = items.length
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0

    // ─── Get current day name ───
    const currentDayName = DAY_NAMES[new Date(selectedDate).getDay()]

    return (
        <div className="space-y-6 fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold gold-text">✅ قائمة المهام</h1>
                    <p className="text-white/60 mt-1">إدارة المهام اليومية ومتابعة الإنجاز</p>
                </div>
                <button
                    onClick={() => { setShowSettings(!showSettings); if (!showSettings) fetchSettings() }}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-colors ${showSettings ? 'bg-gold-500/30 text-gold-400' : 'bg-white/5 text-white/60 hover:bg-white/10'}`}
                >
                    <Settings className="w-5 h-5" />
                    <span>الإعدادات</span>
                </button>
            </div>

            {/* Settings Panel (Collapsible) */}
            {showSettings && (
                <div className="card border-gold-500/40 animate-fadeIn">
                    <h3 className="text-lg font-semibold text-gold-500 mb-4 flex items-center gap-2">
                        <Settings className="w-5 h-5" />
                        إعدادات اللوجستيات
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="label-2026"><Phone className="w-4 h-4" /> رقم المدير</label>
                            <input
                                className="input-2026"
                                placeholder="مثال: 201557368364"
                                value={settings.manager_phone}
                                onChange={e => setSettings({ ...settings, manager_phone: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="label-2026"><User className="w-4 h-4" /> اسم المدير</label>
                            <input
                                className="input-2026"
                                placeholder="اسم المدير"
                                value={settings.manager_name}
                                onChange={e => setSettings({ ...settings, manager_name: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="label-2026"><Hash className="w-4 h-4" /> Group ID (واتساب)</label>
                            <input
                                className="input-2026"
                                placeholder="WhatsApp Group ID"
                                value={settings.whatsapp_group_id}
                                onChange={e => setSettings({ ...settings, whatsapp_group_id: e.target.value })}
                            />
                        </div>
                    </div>
                    <div className="mt-4 flex items-center justify-end gap-3">
                        {settingsMsg && (
                            <span className={`text-sm font-semibold animate-fadeIn ${settingsMsg.type === 'success' ? 'text-green-400' : 'text-red-400'
                                }`}>
                                {settingsMsg.text}
                            </span>
                        )}
                        <button onClick={saveSettings} className="btn-2026 text-sm" disabled={savingSettings}>
                            {savingSettings ? 'جاري الحفظ...' : '💾 حفظ الإعدادات'}
                        </button>
                    </div>
                </div>
            )}

            {/* Week Progress */}
            {weekProgress.length > 0 && (
                <div className="card">
                    <h3 className="text-lg font-semibold text-gold-500 mb-4">📊 إنجاز الأسبوع</h3>
                    <div className="grid grid-cols-7 gap-2">
                        {weekProgress.map((day) => {
                            const isSelected = day.date === selectedDate
                            const isToday = day.date === todayDate
                            return (
                                <button
                                    key={day.date}
                                    onClick={() => setSelectedDate(day.date)}
                                    className={`rounded-xl p-3 text-center transition-all border ${isSelected
                                        ? 'border-gold-500 bg-gold-500/20'
                                        : isToday
                                            ? 'border-green-500/50 bg-green-500/10'
                                            : 'border-white/10 bg-white/5 hover:bg-white/10'
                                        }`}
                                >
                                    <div className="text-xs text-white/50 mb-1">{day.day_name}</div>
                                    <div className="text-sm font-bold text-white mb-2">{day.date.split('-')[2]}</div>
                                    {/* Progress Ring */}
                                    <div className="mx-auto w-10 h-10 relative">
                                        <svg className="w-10 h-10 transform -rotate-90" viewBox="0 0 36 36">
                                            <circle cx="18" cy="18" r="15.5" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3" />
                                            <circle
                                                cx="18" cy="18" r="15.5" fill="none"
                                                stroke={day.percentage >= 100 ? '#22C55E' : '#D4AF37'}
                                                strokeWidth="3"
                                                strokeDasharray={`${day.percentage} 100`}
                                                strokeLinecap="round"
                                            />
                                        </svg>
                                        <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white">
                                            {day.total > 0 ? `${Math.round(day.percentage)}%` : '-'}
                                        </span>
                                    </div>
                                    <div className="text-[10px] text-white/40 mt-1">{day.completed}/{day.total}</div>
                                </button>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* Date Navigation + Today Progress */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <button onClick={() => changeDate(-1)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                        <ChevronRight className="w-5 h-5 text-white/60" />
                    </button>
                    <div className="flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-gold-500" />
                        <input
                            type="date"
                            value={selectedDate}
                            onChange={e => setSelectedDate(e.target.value)}
                            className="bg-transparent text-white text-lg font-semibold border-none outline-none cursor-pointer"
                        />
                        <span className="text-white/40 text-sm">({currentDayName})</span>
                    </div>
                    <button onClick={() => changeDate(1)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                        <ChevronLeft className="w-5 h-5 text-white/60" />
                    </button>
                    {selectedDate !== todayDate && (
                        <button
                            onClick={() => setSelectedDate(todayDate)}
                            className="text-xs text-gold-400 hover:text-gold-300 transition-colors"
                        >
                            اليوم
                        </button>
                    )}
                </div>
                {/* Today Progress Bar */}
                <div className="flex items-center gap-3">
                    <span className="text-sm text-white/50">{completed}/{total} مهام</span>
                    <div className="w-40 h-3 rounded-full bg-white/10 overflow-hidden">
                        <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                                width: `${percentage}%`,
                                background: percentage >= 100
                                    ? 'linear-gradient(90deg, #22C55E, #4ADE80)'
                                    : 'linear-gradient(90deg, #D4AF37, #FFD700)'
                            }}
                        />
                    </div>
                    <span className={`text-sm font-bold ${percentage >= 100 ? 'text-green-400' : 'text-gold-400'}`}>
                        {percentage}%
                    </span>
                </div>
            </div>

            {/* Add Task */}
            <div className="card border-gold-500/20">
                <div className="flex gap-3">
                    <div className="flex-1 space-y-2">
                        <input
                            className="input-2026"
                            placeholder="عنوان المهمة الجديدة..."
                            value={newTitle}
                            onChange={e => setNewTitle(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && addItem()}
                        />
                        <input
                            className="input-2026 text-sm"
                            placeholder="وصف إضافي (اختياري)"
                            value={newDesc}
                            onChange={e => setNewDesc(e.target.value)}
                        />
                    </div>
                    <button onClick={addItem} className="btn-2026 self-start flex items-center gap-2" disabled={!newTitle.trim()}>
                        <Plus className="w-5 h-5" />
                        إضافة
                    </button>
                </div>
            </div>

            {/* Task List */}
            <div className="space-y-3">
                {loading ? (
                    <div className="text-center py-12 text-white/40">جاري التحميل...</div>
                ) : items.length === 0 ? (
                    <div className="text-center py-12">
                        <CheckSquare className="w-16 h-16 mx-auto text-white/10 mb-4" />
                        <p className="text-white/40">لا توجد مهام لهذا اليوم</p>
                        <p className="text-white/30 text-sm mt-1">أضف مهمة جديدة من الحقل أعلاه</p>
                    </div>
                ) : (
                    items.map(item => (
                        <div
                            key={item.id}
                            className={`card flex items-center gap-4 transition-all ${item.is_completed ? 'border-green-500/30 bg-green-500/5' : 'border-white/10'
                                }`}
                        >
                            {/* Checkbox */}
                            <button
                                onClick={() => toggleItem(item)}
                                className={`w-8 h-8 rounded-lg border-2 flex items-center justify-center transition-all flex-shrink-0 ${item.is_completed
                                    ? 'border-green-500 bg-green-500/20 text-green-400'
                                    : 'border-white/20 hover:border-gold-500'
                                    }`}
                            >
                                {item.is_completed && <CheckSquare className="w-5 h-5" />}
                            </button>

                            {/* Content */}
                            {editingId === item.id ? (
                                <div className="flex-1 flex gap-2">
                                    <input
                                        className="input-2026 flex-1"
                                        value={editTitle}
                                        onChange={e => setEditTitle(e.target.value)}
                                    />
                                    <input
                                        className="input-2026 flex-1"
                                        placeholder="الوصف"
                                        value={editDesc}
                                        onChange={e => setEditDesc(e.target.value)}
                                    />
                                    <button onClick={() => saveEdit(item.id)} className="p-2 text-green-400 hover:bg-green-500/10 rounded-lg">
                                        <Save className="w-5 h-5" />
                                    </button>
                                    <button onClick={() => setEditingId(null)} className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg">
                                        <X className="w-5 h-5" />
                                    </button>
                                </div>
                            ) : (
                                <div className="flex-1">
                                    <p className={`font-semibold ${item.is_completed ? 'line-through text-white/40' : 'text-white'}`}>
                                        {item.title}
                                    </p>
                                    {item.description && (
                                        <p className="text-sm text-white/40 mt-1">{item.description}</p>
                                    )}
                                    {item.is_completed && item.completed_by_name && (
                                        <p className="text-xs text-green-400/60 mt-1">
                                            ✅ أكملها: {item.completed_by_name}
                                            {item.completed_at && ` • ${new Date(item.completed_at).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })}`}
                                        </p>
                                    )}
                                </div>
                            )}

                            {/* Actions */}
                            {editingId !== item.id && (
                                <div className="flex gap-1">
                                    <button
                                        onClick={() => { setEditingId(item.id); setEditTitle(item.title); setEditDesc(item.description || '') }}
                                        className="p-2 text-white/30 hover:text-gold-400 hover:bg-gold-500/10 rounded-lg transition-colors"
                                    >
                                        <Edit3 className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => deleteItem(item.id)}
                                        className="p-2 text-white/30 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}

export default ChecklistPage
