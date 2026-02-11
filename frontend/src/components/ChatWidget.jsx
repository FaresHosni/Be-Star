import React, { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Loader2 } from 'lucide-react'

function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState([
        { id: 1, text: 'مرحباً! كيف يمكنني مساعدتك؟ 🌟', isBot: true }
    ])
    const [inputValue, setInputValue] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const messagesEndRef = useRef(null)

    useEffect(() => {
        // Generate session ID on mount
        setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
    }, [])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSend = async () => {
        if (!inputValue.trim() || isLoading) return

        const userMessage = { id: Date.now(), text: inputValue, isBot: false }
        setMessages(prev => [...prev, userMessage])
        setInputValue('')
        setIsLoading(true)

        try {
            // Send to backend/n8n
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    message: inputValue
                })
            })

            const data = await response.json()

            // Simulate bot response (in real scenario, this comes from n8n webhook)
            setTimeout(() => {
                setMessages(prev => [...prev, {
                    id: Date.now(),
                    text: 'شكراً لرسالتك! سيتم الرد عليك قريباً. 🎟️',
                    isBot: true
                }])
                setIsLoading(false)
            }, 1000)
        } catch (error) {
            setIsLoading(false)
            setMessages(prev => [...prev, {
                id: Date.now(),
                text: 'عذراً، حدث خطأ. حاول مرة أخرى.',
                isBot: true
            }])
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="chat-widget">
            {/* Chat Window */}
            {isOpen && (
                <div className="chat-window fade-in">
                    {/* Header */}
                    <div className="bg-gradient-to-l from-gold-500 to-gold-400 p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-dark-500 flex items-center justify-center">
                                <MessageCircle className="w-5 h-5 text-gold-500" />
                            </div>
                            <div>
                                <h3 className="font-bold text-dark-500">كن نجماً</h3>
                                <p className="text-xs text-dark-500/70">نحن هنا لمساعدتك</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="p-2 rounded-full hover:bg-dark-500/10 transition-colors"
                        >
                            <X className="w-5 h-5 text-dark-500" />
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`flex ${msg.isBot ? 'justify-start' : 'justify-end'}`}
                            >
                                <div
                                    className={`max-w-[80%] p-3 rounded-2xl ${msg.isBot
                                            ? 'bg-dark-100 text-white rounded-tr-sm'
                                            : 'bg-gradient-to-l from-gold-500 to-gold-400 text-dark-500 rounded-tl-sm'
                                        }`}
                                >
                                    <p className="text-sm">{msg.text}</p>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-dark-100 p-3 rounded-2xl rounded-tr-sm">
                                    <Loader2 className="w-5 h-5 text-gold-500 animate-spin" />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-4 border-t border-gold-500/20">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="اكتب رسالتك..."
                                className="input-gold flex-1"
                                disabled={isLoading}
                            />
                            <button
                                onClick={handleSend}
                                disabled={isLoading || !inputValue.trim()}
                                className="btn-gold px-4 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="chat-button pulse-gold"
            >
                {isOpen ? (
                    <X className="w-7 h-7 text-dark-500" />
                ) : (
                    <MessageCircle className="w-7 h-7 text-dark-500" />
                )}
            </button>
        </div>
    )
}

export default ChatWidget
