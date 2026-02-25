import { useState, useRef, useEffect, useCallback } from 'react';
import { MessageCircle, Bot, X, Send, Image, Mic, Square, Loader2, User, Phone, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';

const WEBHOOK_URL = 'https://n8n.growhubeg.com/webhook/bestar-webchat';

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);

    // Registration state
    const [isRegistered, setIsRegistered] = useState(() => {
        return !!sessionStorage.getItem('bestar_chat_user');
    });
    const [regName, setRegName] = useState('');
    const [regPhone, setRegPhone] = useState('');
    const [regError, setRegError] = useState('');

    // Chat state
    const [messages, setMessages] = useState([
        { id: 'welcome', role: 'ai', text: 'أهلاً بيك! 👋 أنا عمر، مساعد إيفنت كن نجماً الذكي.\nاسألني أي سؤال عن الحدث، الجلسات، المتحدثين، أو التذاكر وهجاوبك فوراً!' }
    ]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Voice recording state
    const [isRecording, setIsRecording] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const recordingTimerRef = useRef(null);

    // Refs
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const inputRef = useRef(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    // Get user data from session
    const getUserData = useCallback(() => {
        try {
            return JSON.parse(sessionStorage.getItem('bestar_chat_user') || '{}');
        } catch {
            return {};
        }
    }, []);

    // Handle registration
    const handleRegister = (e) => {
        e.preventDefault();
        setRegError('');

        const trimmedName = regName.trim();
        const trimmedPhone = regPhone.trim();

        if (!trimmedName || !trimmedPhone) {
            setRegError('من فضلك املأ جميع الحقول');
            return;
        }

        // Validate name has at least 2 words
        const nameWords = trimmedName.split(/\s+/).filter(w => w.length > 0);
        if (nameWords.length < 2) {
            setRegError('من فضلك اكتب اسمك الثنائي أو أكثر');
            return;
        }

        // Validate phone
        if (!/^[\d+]{8,15}$/.test(trimmedPhone.replace(/\s/g, ''))) {
            setRegError('من فضلك أدخل رقم هاتف صحيح');
            return;
        }

        const userData = { name: trimmedName, phone: trimmedPhone };
        sessionStorage.setItem('bestar_chat_user', JSON.stringify(userData));
        setIsRegistered(true);
    };

    // Send message to n8n
    const sendToWebhook = async (payload) => {
        const user = getUserData();
        const sessionId = `web_${user.phone || 'anon'}`;

        const body = {
            source: 'webchat',
            session_id: sessionId,
            user_phone: user.phone || '',
            user_name: user.name || '',
            message_type: 'text',
            message_text: '',
            image_base64: '',
            audio_base64: '',
            ...payload,
        };

        try {
            const res = await fetch(WEBHOOK_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });

            if (!res.ok) throw new Error('Server error');

            const data = await res.json();
            return data;
        } catch (err) {
            console.error('Webhook error:', err);
            return { reply: 'عذراً، حدث خطأ في الاتصال. حاول مرة أخرى.' };
        }
    };

    // Send text message
    const handleSendText = async () => {
        const text = inputText.trim();
        if (!text || isLoading) return;

        const userMsg = { id: Date.now(), role: 'user', text };
        setMessages(prev => [...prev, userMsg]);
        setInputText('');
        setIsLoading(true);

        const data = await sendToWebhook({ message_type: 'text', message_text: text });

        setMessages(prev => [...prev, {
            id: Date.now() + 1,
            role: 'ai',
            text: data.reply || 'عذراً، لم أتمكن من الرد.'
        }]);
        setIsLoading(false);
        inputRef.current?.focus();
    };

    // Handle image upload
    const handleImageUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file || isLoading) return;

        // Reset file input
        if (fileInputRef.current) fileInputRef.current.value = '';

        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            setMessages(prev => [...prev, {
                id: Date.now(),
                role: 'system',
                text: '⚠️ حجم الصورة كبير جداً. الحد الأقصى 5 ميجابايت.'
            }]);
            return;
        }

        // Convert to Base64
        const reader = new FileReader();
        reader.onload = async () => {
            const base64 = reader.result;

            const userMsg = { id: Date.now(), role: 'user', text: '📷 تم إرسال صورة', isMedia: true };
            setMessages(prev => [...prev, userMsg]);
            setIsLoading(true);

            const data = await sendToWebhook({
                message_type: 'image',
                message_text: 'العميل بعت صورة',
                image_base64: base64,
            });

            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                role: 'ai',
                text: data.reply || 'عذراً، لم أتمكن من الرد.'
            }]);
            setIsLoading(false);
        };
        reader.readAsDataURL(file);
    };

    // Voice recording
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                    ? 'audio/webm;codecs=opus'
                    : 'audio/webm'
            });
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunksRef.current.push(e.data);
            };

            mediaRecorder.onstop = async () => {
                stream.getTracks().forEach(t => t.stop());
                clearInterval(recordingTimerRef.current);
                setRecordingTime(0);

                const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

                // Convert to Base64
                const reader = new FileReader();
                reader.onload = async () => {
                    const base64 = reader.result;

                    const userMsg = { id: Date.now(), role: 'user', text: '🎤 تم إرسال تسجيل صوتي', isMedia: true };
                    setMessages(prev => [...prev, userMsg]);
                    setIsLoading(true);

                    const data = await sendToWebhook({
                        message_type: 'audio',
                        message_text: '',
                        audio_base64: base64,
                    });

                    setMessages(prev => [...prev, {
                        id: Date.now() + 1,
                        role: 'ai',
                        text: data.reply || 'عذراً، لم أتمكن من الرد.'
                    }]);
                    setIsLoading(false);
                };
                reader.readAsDataURL(blob);
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingTime(0);
            recordingTimerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);
        } catch (err) {
            console.error('Microphone error:', err);
            setMessages(prev => [...prev, {
                id: Date.now(),
                role: 'system',
                text: '⚠️ لم يتم السماح بالوصول إلى الميكروفون. يرجى السماح ثم المحاولة مرة أخرى.'
            }]);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendText();
        }
    };

    return (
        <>
            {/* Floating Bubble */}
            <div className="chat-bubble" onClick={() => setIsOpen(!isOpen)}>
                {isOpen ? <X size={28} color="#fff" /> : <MessageCircle size={28} color="#fff" />}
                {!isOpen && <div className="chat-tooltip">اسأل الموظف الذكي</div>}
            </div>

            {/* Chat Window */}
            {isOpen && (
                <div className="cw-window">
                    {/* Header */}
                    <div className="cw-header">
                        <div>
                            <div className="cw-header-title">
                                <Bot size={20} /> مساعد Be Star الذكي
                            </div>
                            <div className="cw-header-sub">مدعوم من Mr. AI</div>
                        </div>
                        <button className="cw-close-btn" onClick={() => setIsOpen(false)}>
                            <X size={20} />
                        </button>
                    </div>

                    {/* Registration Form */}
                    {!isRegistered ? (
                        <div className="cw-register">
                            <div className="cw-register-icon">
                                <Bot size={48} />
                            </div>
                            <h3 className="cw-register-title">مرحباً بك! 👋</h3>
                            <p className="cw-register-desc">
                                عرّفنا بنفسك علشان نقدر نساعدك بشكل أفضل
                            </p>

                            <form onSubmit={handleRegister} className="cw-register-form">
                                <div className="cw-input-group">
                                    <User size={18} className="cw-input-icon" />
                                    <input
                                        type="text"
                                        placeholder="الاسم الكامل (مثال: أحمد محمد)"
                                        value={regName}
                                        onChange={(e) => setRegName(e.target.value)}
                                        className="cw-reg-input"
                                        dir="rtl"
                                    />
                                </div>
                                <div className="cw-input-group">
                                    <Phone size={18} className="cw-input-icon" />
                                    <input
                                        type="tel"
                                        placeholder="رقم الهاتف (مثال: 01xxxxxxxxx)"
                                        value={regPhone}
                                        onChange={(e) => setRegPhone(e.target.value)}
                                        className="cw-reg-input"
                                        dir="ltr"
                                    />
                                </div>

                                {regError && (
                                    <div className="cw-reg-error">
                                        <AlertCircle size={16} /> {regError}
                                    </div>
                                )}

                                <button type="submit" className="cw-reg-btn">
                                    ابدأ المحادثة <ArrowRight size={18} />
                                </button>
                            </form>
                        </div>
                    ) : (
                        <>
                            {/* Messages Area */}
                            <div className="cw-messages">
                                {messages.map(msg => (
                                    <div
                                        key={msg.id}
                                        className={`cw-msg ${msg.role === 'user' ? 'cw-msg-user' : msg.role === 'system' ? 'cw-msg-system' : 'cw-msg-ai'}`}
                                    >
                                        {msg.role === 'ai' && (
                                            <div className="cw-msg-avatar">
                                                <Bot size={16} />
                                            </div>
                                        )}
                                        <div className={`cw-msg-bubble ${msg.isMedia ? 'cw-msg-media' : ''}`}>
                                            {msg.text.split('\n').map((line, i) => (
                                                <span key={i}>{line}{i < msg.text.split('\n').length - 1 && <br />}</span>
                                            ))}
                                        </div>
                                    </div>
                                ))}

                                {isLoading && (
                                    <div className="cw-msg cw-msg-ai">
                                        <div className="cw-msg-avatar">
                                            <Bot size={16} />
                                        </div>
                                        <div className="cw-msg-bubble cw-typing">
                                            <span className="cw-dot"></span>
                                            <span className="cw-dot"></span>
                                            <span className="cw-dot"></span>
                                        </div>
                                    </div>
                                )}

                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input Area */}
                            <div className="cw-input-bar">
                                {isRecording ? (
                                    <div className="cw-recording-bar">
                                        <div className="cw-rec-indicator">
                                            <span className="cw-rec-dot"></span>
                                            جاري التسجيل {formatTime(recordingTime)}
                                        </div>
                                        <button className="cw-rec-stop" onClick={stopRecording} title="إيقاف التسجيل">
                                            <Square size={18} />
                                        </button>
                                    </div>
                                ) : (
                                    <>
                                        {/* Media buttons */}
                                        <button
                                            className="cw-media-btn"
                                            onClick={() => fileInputRef.current?.click()}
                                            disabled={isLoading}
                                            title="إرسال صورة"
                                        >
                                            <Image size={20} />
                                        </button>
                                        <input
                                            type="file"
                                            ref={fileInputRef}
                                            accept="image/*"
                                            onChange={handleImageUpload}
                                            style={{ display: 'none' }}
                                        />

                                        <button
                                            className="cw-media-btn cw-mic-btn"
                                            onClick={startRecording}
                                            disabled={isLoading}
                                            title="تسجيل صوتي"
                                        >
                                            <Mic size={20} />
                                        </button>

                                        {/* Text input */}
                                        <input
                                            ref={inputRef}
                                            type="text"
                                            className="cw-text-input"
                                            placeholder="اكتب رسالتك هنا..."
                                            value={inputText}
                                            onChange={(e) => setInputText(e.target.value)}
                                            onKeyDown={handleKeyDown}
                                            disabled={isLoading}
                                            dir="rtl"
                                        />

                                        {/* Send button */}
                                        <button
                                            className="cw-send-btn"
                                            onClick={handleSendText}
                                            disabled={!inputText.trim() || isLoading}
                                            title="إرسال"
                                        >
                                            {isLoading ? <Loader2 size={20} className="cw-spinner" /> : <Send size={20} />}
                                        </button>
                                    </>
                                )}
                            </div>
                        </>
                    )}
                </div>
            )}
        </>
    );
}
