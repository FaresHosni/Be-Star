import { useState } from 'react';

export default function Tickets() {
    const [mode, setMode] = useState(null); // null, 'form', 'chat'
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        email: '',
        ticket_type: 'Student',
    });
    const [submitting, setSubmitting] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setError('');

        try {
            const response = await fetch('/api/tickets/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: formData.name,
                    phone: formData.phone,
                    email: formData.email || null,
                    ticket_type: formData.ticket_type,
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'حدث خطأ أثناء الحجز');
            }

            setSuccess(true);
        } catch (err) {
            setError(err.message);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <>
            <div className="tickets-hero">
                <h1>🎫 حجز التذاكر</h1>
                <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '1.1rem' }}>
                    اختر الطريقة المناسبة لك لحجز تذكرتك
                </p>
            </div>

            {/* خيارات الحجز */}
            <div className="tickets-options">
                <div
                    className={`ticket-option${mode === 'chat' ? ' active' : ''}`}
                    onClick={() => setMode('chat')}
                >
                    <div className="ticket-option-icon">💬</div>
                    <h3>حجز مع موظف العملاء الذكي</h3>
                    <p>تحدث مع المساعد الذكي وهو هيساعدك تحجز خطوة بخطوة</p>
                </div>

                <div
                    className={`ticket-option${mode === 'form' ? ' active' : ''}`}
                    onClick={() => setMode('form')}
                >
                    <div className="ticket-option-icon">📝</div>
                    <h3>حجز من خلال فورم</h3>
                    <p>املأ البيانات بنفسك وارفع إثبات الدفع</p>
                </div>
            </div>

            {/* محتوى الحجز */}
            {mode === 'form' && (
                <div className="ticket-form-container">
                    {success ? (
                        <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
                            <div style={{ fontSize: '4rem', marginBottom: '16px' }}>🎉</div>
                            <h2 style={{ color: 'var(--primary-dark)', marginBottom: '12px' }}>تم الحجز بنجاح!</h2>
                            <p style={{ color: 'var(--gray-500)', marginBottom: '24px' }}>
                                سيتم مراجعة طلبك وإرسال تأكيد التذكرة قريباً
                            </p>
                            <button
                                className="btn btn-primary"
                                onClick={() => { setSuccess(false); setFormData({ name: '', phone: '', email: '', ticket_type: 'Student' }); }}
                            >
                                حجز تذكرة أخرى
                            </button>
                        </div>
                    ) : (
                        <form className="ticket-form" onSubmit={handleSubmit}>
                            <h2 style={{ textAlign: 'center', marginBottom: '8px', color: 'var(--primary-dark)' }}>
                                📝 نموذج الحجز
                            </h2>
                            <p style={{ textAlign: 'center', color: 'var(--gray-500)', marginBottom: '32px', fontSize: '0.9rem' }}>
                                املأ البيانات التالية لحجز تذكرتك
                            </p>

                            {error && (
                                <div style={{
                                    background: '#fff3f3', border: '1px solid #fecaca', borderRadius: '12px',
                                    padding: '12px 16px', marginBottom: '20px', color: '#dc2626', fontSize: '0.9rem',
                                }}>
                                    ⚠️ {error}
                                </div>
                            )}

                            <div className="form-group">
                                <label>الاسم الكامل *</label>
                                <input
                                    type="text" required placeholder="أدخل اسمك الكامل"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>

                            <div className="form-group">
                                <label>رقم الهاتف *</label>
                                <input
                                    type="tel" required placeholder="01xxxxxxxxx" dir="ltr"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                />
                            </div>

                            <div className="form-group">
                                <label>البريد الإلكتروني</label>
                                <input
                                    type="email" placeholder="example@email.com" dir="ltr"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>

                            <div className="form-group">
                                <label>نوع التذكرة *</label>
                                <select
                                    value={formData.ticket_type}
                                    onChange={(e) => setFormData({ ...formData, ticket_type: e.target.value })}
                                >
                                    <option value="Student">Student — طالب</option>
                                    <option value="VIP">VIP — كبار الزوار</option>
                                </select>
                            </div>

                            <button
                                type="submit"
                                className="btn btn-primary form-submit btn-lg"
                                disabled={submitting}
                            >
                                {submitting ? '⏳ جاري الحجز...' : '🎫 تأكيد الحجز'}
                            </button>
                        </form>
                    )}
                </div>
            )}

            {mode === 'chat' && (
                <div className="ticket-form-container">
                    <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '16px' }}>🤖</div>
                        <h2 style={{ color: 'var(--primary-dark)', marginBottom: '12px' }}>موظف العملاء الذكي</h2>
                        <p style={{ color: 'var(--gray-500)', marginBottom: '24px', lineHeight: 1.7 }}>
                            اضغط على فقاعة الشات في الزاوية اليسرى من الشاشة 💬
                            <br />
                            وابدأ محادثة مع المساعد الذكي لحجز تذكرتك بسهولة!
                        </p>
                        <p style={{ color: 'var(--primary-gold-dark)', fontWeight: 600, fontSize: '0.9rem' }}>
                            مدعوم بالذكاء الاصطناعي من Mr. AI ⚡
                        </p>
                    </div>
                </div>
            )}
        </>
    );
}
