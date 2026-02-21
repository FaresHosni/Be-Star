import { useState } from 'react';
import { Ticket, MessageCircle, FileEdit, PartyPopper, AlertTriangle, Hourglass, Bot, Zap } from 'lucide-react';

export default function Tickets() {
    const [mode, setMode] = useState(null); // null, 'form', 'chat'
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        email: '',
        ticket_type: 'Student',
        payment_method: 'Vodafone Cash',
    });
    const [paymentProof, setPaymentProof] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setError('');

        try {
            // First: Create Ticket
            const response = await fetch('/api/tickets/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: formData.name,
                    phone: formData.phone,
                    email: formData.email || null,
                    ticket_type: formData.ticket_type,
                    payment_method: formData.payment_method,
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'حدث خطأ أثناء الحجز');
            }

            const ticketData = await response.json();

            // Second: Upload Payment Proof if provided
            if (paymentProof && ticketData.ticket_id) {
                const proofFormData = new FormData();
                proofFormData.append('file', paymentProof);

                const uploadRes = await fetch(`/api/tickets/${ticketData.ticket_id}/payment-proof`, {
                    method: 'POST',
                    body: proofFormData,
                });

                if (!uploadRes.ok) {
                    const uploadData = await uploadRes.json();
                    throw new Error(uploadData.detail || 'تم الحجز ولكن حدث خطأ أثناء رفع إثبات الدفع. يرجى التواصل مع الدعم.');
                }
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
                <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}><Ticket size={36} /> حجز التذاكر</h1>
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
                    <div className="ticket-option-icon"><MessageCircle size={32} /></div>
                    <h3>حجز مع موظف العملاء الذكي</h3>
                    <p>تحدث مع المساعد الذكي وهو هيساعدك تحجز خطوة بخطوة</p>
                </div>

                <div
                    className={`ticket-option${mode === 'form' ? ' active' : ''}`}
                    onClick={() => setMode('form')}
                >
                    <div className="ticket-option-icon"><FileEdit size={32} /></div>
                    <h3>حجز من خلال فورم</h3>
                    <p>املأ البيانات بنفسك وارفع إثبات الدفع</p>
                </div>
            </div>

            {/* محتوى الحجز */}
            {mode === 'form' && (
                <div className="ticket-form-container">
                    {success ? (
                        <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
                            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px', color: 'var(--primary-dark)' }}><PartyPopper size={64} /></div>
                            <h2 style={{ color: 'var(--primary-dark)', marginBottom: '12px' }}>تم الحجز بنجاح!</h2>
                            <p style={{ color: 'var(--gray-500)', marginBottom: '24px' }}>
                                سيتم مراجعة طلبك وإرسال تأكيد التذكرة قريباً
                            </p>
                            <button
                                className="btn btn-primary"
                                onClick={() => { setSuccess(false); setPaymentProof(null); setFormData({ name: '', phone: '', email: '', ticket_type: 'Student', payment_method: 'Vodafone Cash' }); }}
                            >
                                حجز تذكرة أخرى
                            </button>
                        </div>
                    ) : (
                        <form className="ticket-form" onSubmit={handleSubmit}>
                            <h2 style={{ textAlign: 'center', marginBottom: '8px', color: 'var(--primary-dark)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                                <FileEdit size={24} /> نموذج الحجز
                            </h2>
                            <p style={{ textAlign: 'center', color: 'var(--gray-500)', marginBottom: '32px', fontSize: '0.9rem' }}>
                                املأ البيانات التالية لحجز تذكرتك
                            </p>

                            {error && (
                                <div style={{
                                    background: '#fff3f3', border: '1px solid #fecaca', borderRadius: '12px',
                                    padding: '12px 16px', marginBottom: '20px', color: '#dc2626', fontSize: '0.9rem',
                                    display: 'flex', alignItems: 'center', gap: '8px'
                                }}>
                                    <AlertTriangle size={18} /> {error}
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
                                    <option value="Student">Student — طالب (100 جنيه)</option>
                                    <option value="VIP">VIP — كبار الزوار (500 جنيه)</option>
                                </select>
                            </div>

                            <div style={{
                                background: 'rgba(255, 193, 7, 0.1)', border: '1px solid rgba(255, 193, 7, 0.3)', borderRadius: '12px',
                                padding: '16px', marginBottom: '20px', color: 'var(--primary-dark)', fontSize: '0.95rem', lineHeight: 1.6
                            }}>
                                <strong style={{ color: 'var(--primary-gold-dark)', display: 'block', marginBottom: '8px' }}>📌 معلومات الدفع:</strong>
                                يرجى تحويل مبلغ التذكرة على الرقم التالي: <strong style={{ fontSize: '1.1rem', userSelect: 'all' }}>01278453450</strong>
                                <br />ثم إرفاق صورة إيصال التحويل (سكرين شوت) بالأسفل ليتم مراجعتها وتأكيد حجزك خلال ساعات قليلة.
                            </div>

                            <div className="form-group">
                                <label>طريقة الدفع *</label>
                                <select
                                    value={formData.payment_method}
                                    onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                                >
                                    <option value="Vodafone Cash">Vodafone Cash - فودافون كاش</option>
                                    <option value="InstaPay">InstaPay - انستا باي</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>صورة إثبات الدفع (إيصال التحويل) *</label>
                                <input
                                    type="file" required accept="image/*"
                                    onChange={(e) => setPaymentProof(e.target.files[0])}
                                    style={{ padding: '8px', border: '2px dashed #e9ecef' }}
                                />
                            </div>

                            <button
                                type="submit"
                                className="btn btn-primary form-submit btn-lg"
                                disabled={submitting}
                            >
                                {submitting ? <><Hourglass size={20} style={{ display: 'inline', verticalAlign: 'text-bottom', marginEnd: '8px' }} /> جاري الحجز...</> : <><Ticket size={20} style={{ display: 'inline', verticalAlign: 'text-bottom', marginEnd: '8px' }} /> تأكيد الحجز</>}
                            </button>
                        </form>
                    )}
                </div>
            )}

            {mode === 'chat' && (
                <div className="ticket-form-container">
                    <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px', color: 'var(--primary-dark)' }}><Bot size={64} /></div>
                        <h2 style={{ color: 'var(--primary-dark)', marginBottom: '12px' }}>موظف العملاء الذكي</h2>
                        <p style={{ color: 'var(--gray-500)', marginBottom: '24px', lineHeight: 1.7 }}>
                            اضغط على فقاعة الشات في الزاوية اليسرى من الشاشة <MessageCircle size={20} style={{ display: 'inline', verticalAlign: 'text-bottom', marginStart: '4px' }} />
                            <br />
                            وابدأ محادثة مع المساعد الذكي لحجز تذكرتك بسهولة!
                        </p>
                        <p style={{ color: 'var(--primary-gold-dark)', fontWeight: 600, fontSize: '0.9rem' }}>
                            مدعوم بالذكاء الاصطناعي من Mr. AI <Zap size={16} style={{ display: 'inline', verticalAlign: 'text-bottom', marginStart: '4px', fill: 'currentColor' }} />
                        </p>
                    </div>
                </div>
            )}
        </>
    );
}
