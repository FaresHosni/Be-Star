import eventData from '../config/eventData.json';
import { Mic, Instagram, Youtube, Music, Linkedin } from 'lucide-react';

export default function Speakers() {
    const { speakers } = eventData;

    return (
        <>
            <div className="page-header">
                <h1>المتحدثون والضيوف</h1>
                <p>تعرّف على نخبة من أفضل الخبراء الذين سيشاركون معرفتهم وخبراتهم معك</p>
            </div>

            <section className="section">
                <div className="container">
                    <div className="speakers-grid">
                        {speakers.map((speaker) => (
                            <div className="speaker-card" key={speaker.id}>
                                <div className="speaker-avatar">
                                    {speaker.name.charAt(0)}
                                </div>
                                <h3>{speaker.name}</h3>
                                <div className="field">{speaker.field}</div>
                                <p className="bio">{speaker.bio}</p>
                                <div className="session-badge"><Mic size={16} style={{ display: 'inline', marginEnd: '6px', verticalAlign: 'text-bottom' }} /> {speaker.session}</div>
                                <div className="speaker-socials">
                                    {speaker.social.instagram && <a href={speaker.social.instagram}><Instagram size={18} /></a>}
                                    {speaker.social.youtube && <a href={speaker.social.youtube}><Youtube size={18} /></a>}
                                    {speaker.social.tiktok && <a href={speaker.social.tiktok}><Music size={18} /></a>}
                                    {speaker.social.linkedin && <a href={speaker.social.linkedin}><Linkedin size={18} /></a>}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>
        </>
    );
}
