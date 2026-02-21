import { useState } from 'react';
import { MessageCircle, Bot, X, Hand, Send } from 'lucide-react';

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            <div className="chat-bubble" onClick={() => setIsOpen(!isOpen)}>
                <MessageCircle size={28} style={{ color: '#fff' }} />
                <div className="chat-tooltip">اسأل الموظف الذكي</div>
            </div>

            {isOpen && (
                <div style={{
                    position: 'fixed',
                    bottom: '96px',
                    left: '24px',
                    width: '380px',
                    maxWidth: 'calc(100vw - 48px)',
                    height: '500px',
                    maxHeight: '70vh',
                    background: '#fff',
                    borderRadius: '20px',
                    boxShadow: '0 8px 40px rgba(0,0,0,0.2)',
                    zIndex: 998,
                    display: 'flex',
                    flexDirection: 'column',
                    overflow: 'hidden',
                }}>
                    {/* Header */}
                    <div style={{
                        background: 'linear-gradient(135deg, #0a1628, #1a237e)',
                        padding: '16px 20px',
                        color: '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                    }}>
                        <div>
                            <div style={{ fontWeight: 700, fontSize: '1rem' }}>
                                <Bot size={20} style={{ display: 'inline', verticalAlign: 'text-bottom', marginEnd: '6px' }} /> مساعد Be Star الذكي
                            </div>
                            <div style={{ fontSize: '0.8rem', opacity: 0.7, marginTop: '2px' }}>
                                مدعوم من Mr. AI
                            </div>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            style={{
                                background: 'rgba(255,255,255,0.15)',
                                border: 'none',
                                color: '#fff',
                                width: '32px',
                                height: '32px',
                                borderRadius: '50%',
                                cursor: 'pointer',
                                fontSize: '1rem',
                            }}
                        >
                            <X size={20} />
                        </button>
                    </div>

                    {/* Messages Area */}
                    <div style={{
                        flex: 1,
                        padding: '20px',
                        overflowY: 'auto',
                        background: '#f8f9fa',
                    }}>
                        <div style={{
                            background: '#fff',
                            padding: '12px 16px',
                            borderRadius: '12px 12px 4px 12px',
                            marginBottom: '12px',
                            maxWidth: '85%',
                            boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                            lineHeight: 1.6,
                            fontSize: '0.95rem',
                        }}>
                            أهلاً بيك! <Hand size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', margin: '0 4px', color: '#f59e0b' }} /> أنا مساعد إيفنت كن نجماً الذكي.
                            <br />
                            اسألني أي سؤال عن الحدث، الجلسات، المتحدثين، أو التذاكر وهجاوبك فوراً!
                        </div>
                    </div>

                    {/* Input */}
                    <div style={{
                        padding: '12px 16px',
                        borderTop: '1px solid #eee',
                        display: 'flex',
                        gap: '8px',
                        background: '#fff',
                    }}>
                        <input
                            type="text"
                            placeholder="اكتب سؤالك هنا..."
                            style={{
                                flex: 1,
                                padding: '12px 16px',
                                border: '2px solid #e9ecef',
                                borderRadius: '12px',
                                fontSize: '0.95rem',
                                fontFamily: 'Cairo, sans-serif',
                                direction: 'rtl',
                            }}
                        />
                        <button style={{
                            background: 'linear-gradient(135deg, #f9a825, #ffc107)',
                            border: 'none',
                            borderRadius: '12px',
                            padding: '0 16px',
                            cursor: 'pointer',
                            fontSize: '1.2rem',
                        }}>
                            <Send size={20} style={{ transform: 'rotate(180deg)' }} />
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
