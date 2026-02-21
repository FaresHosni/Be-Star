import { useState } from 'react';
import eventData from '../config/eventData.json';

export default function Sessions() {
    const { sessions } = eventData;
    const [filter, setFilter] = useState('الكل');

    const types = ['الكل', ...new Set(sessions.map((s) => s.type))];
    const filtered = filter === 'الكل' ? sessions : sessions.filter((s) => s.type === filter);

    const typeIcons = {
        'محاضرة': '🎓',
        'ورشة عمل': '🛠️',
        'جلسة حوارية': '💬',
        'مسابقة': '🏆',
    };

    return (
        <>
            <div className="page-header">
                <h1>الجلسات والفقرات</h1>
                <p>اكتشف جميع الجلسات وورش العمل والمسابقات المقررة في الحدث</p>
            </div>

            <section className="section">
                <div className="container">
                    <div className="sessions-filters">
                        {types.map((type) => (
                            <button
                                key={type}
                                className={`filter-btn${filter === type ? ' active' : ''}`}
                                onClick={() => setFilter(type)}
                            >
                                {type}
                            </button>
                        ))}
                    </div>

                    {filtered.map((session) => (
                        <div className="session-card" key={session.id}>
                            <div className="session-icon">
                                {typeIcons[session.type] || '📌'}
                            </div>
                            <div className="session-info">
                                <h3>{session.title}</h3>
                                <p style={{ color: 'var(--gray-500)', fontSize: '0.95rem', margin: '8px 0' }}>
                                    {session.description}
                                </p>
                                <div className="session-meta">
                                    <span>🎤 {session.speaker}</span>
                                    <span className="badge badge-blue">{session.type}</span>
                                    <span className="badge badge-gold">{session.level}</span>
                                </div>
                                <p style={{ fontSize: '0.85rem', color: 'var(--gray-400)', marginTop: '8px' }}>
                                    📚 ما ستتعلمه: {session.learnings}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </>
    );
}
