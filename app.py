import streamlit as st
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import Config
from auth import AuthManager
from database import DatabaseManager
from ai_manager import AIManager
from security import SecurityManager
from cache_manager import CacheManager

# Set page config
st.set_page_config(
    page_title="AI Education Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

class EducationPlatform:
    def __init__(self):
        self.auth = AuthManager()
        self.db = DatabaseManager()
        self.ai = AIManager()
        self.security = SecurityManager()
        self.cache = CacheManager()
        
        # Initialize session state
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
        if 'current_subject' not in st.session_state:
            st.session_state.current_subject = None
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'exam_questions' not in st.session_state:
            st.session_state.exam_questions = None
        if 'exam_answers' not in st.session_state:
            st.session_state.exam_answers = {}
    
    def send_otp_email(self, email: str, otp: str):
        """Send OTP email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.SMTP_USERNAME
            msg['To'] = email
            msg['Subject'] = "OTP Verification - AI Education Platform"
            
            body = f"""
            <h2>Verifikasi OTP</h2>
            <p>Kode OTP Anda adalah: <strong>{otp}</strong></p>
            <p>Kode ini berlaku selama {Config.OTP_EXPIRY_MINUTES} menit.</p>
            <p>Jangan berikan kode ini kepada siapapun.</p>
            <hr>
            <p><small>Email ini dikirim secara otomatis, mohon tidak membalas.</small></p>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
                server.send_message(msg)
            
            return True
        except Exception as e:
            st.error(f"Gagal mengirim email: {str(e)}")
            return False
    
    def login_page(self):
        """Login page with Google OAuth"""
        st.title("🎓 AI Education Platform")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.subheader("Login dengan Google")
            
            # Google OAuth button (simplified - in production use proper OAuth flow)
            email = st.text_input("Email")
            # In production, implement proper Google OAuth
            # This is a simplified version for demonstration
            
            if st.button("Login dengan Google", type="primary"):
                if email and "@" in email and "." in email:
                    # Simulate user creation/login
                    user_info = {
                        'id': f"user_{hash(email)}",
                        'email': email,
                        'name': email.split('@')[0]
                    }
                    self.auth.login_user(user_info)
                    
                    # Check if user exists in DB
                    user = self.db.get_user_by_email(email)
                    if not user:
                        self.db.add_user({
                            'id': user_info['id'],
                            'email': email,
                            'name': user_info['name']
                        })
                    
                    st.session_state.page = 'select_grade'
                    st.rerun()
                else:
                    st.error("Masukkan email yang valid")
    
    def select_grade_page(self):
        """Page to select grade level"""
        st.title("Pilih Jenjang Pendidikan")
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("SD", use_container_width=True, type="primary"):
                self.db.update_user_grade(st.session_state.user_id, "SD")
                st.session_state.grade_level = "SD"
                st.session_state.page = 'main_menu'
                st.rerun()
        
        with col2:
            if st.button("SMP", use_container_width=True, type="primary"):
                self.db.update_user_grade(st.session_state.user_id, "SMP")
                st.session_state.grade_level = "SMP"
                st.session_state.page = 'main_menu'
                st.rerun()
        
        with col3:
            if st.button("SMA", use_container_width=True, type="primary"):
                self.db.update_user_grade(st.session_state.user_id, "SMA")
                st.session_state.grade_level = "SMA"
                st.session_state.page = 'main_menu'
                st.rerun()
        
        if st.button("Logout"):
            self.auth.logout_user()
            st.session_state.page = 'login'
            st.rerun()
    
    def main_menu_page(self):
        """Main menu page"""
        st.title(f"🎓 AI Education Platform - {st.session_state.grade_level}")
        st.markdown(f"**Selamat datang, {st.session_state.get('user_name', 'User')}!**")
        st.markdown("---")
        
        # Menu options
        menu_options = [
            "📚 Belajar Interaktif",
            "🤔 Refleksi",
            "💡 Validasi Ide",
            "📝 Uji Kompetensi",
            "📊 Level Pengetahuan",
            "⏰ Pengingat Belajar"
        ]
        
        cols = st.columns(3)
        for idx, option in enumerate(menu_options):
            with cols[idx % 3]:
                if st.button(option, use_container_width=True, key=f"menu_{idx}"):
                    if idx == 0:
                        st.session_state.page = 'interactive_learning'
                    elif idx == 1:
                        st.session_state.page = 'reflection'
                    elif idx == 2:
                        st.session_state.page = 'idea_validation'
                    elif idx == 3:
                        st.session_state.page = 'exam'
                    elif idx == 4:
                        st.session_state.page = 'knowledge_level'
                    elif idx == 5:
                        st.session_state.page = 'reminder'
                    st.rerun()
        
        st.markdown("---")
        if st.button("Logout"):
            self.auth.logout_user()
            st.session_state.page = 'login'
            st.rerun()
    
    def interactive_learning_page(self):
        """Interactive learning page"""
        st.title("📚 Belajar Interaktif")
        st.markdown("---")
        
        # Back button
        if st.button("← Kembali ke Menu Utama"):
            st.session_state.page = 'main_menu'
            st.session_state.current_subject = None
            st.session_state.chat_history = []
            st.rerun()
        
        if not st.session_state.current_subject:
            # Show subject selection
            st.subheader("Pilih Mata Pelajaran")
            
            subjects = Config.SUBJECTS.get(st.session_state.grade_level, [])
            cols = st.columns(4)
            
            for idx, subject in enumerate(subjects):
                with cols[idx % 4]:
                    if st.button(subject, use_container_width=True, key=f"subj_{idx}"):
                        st.session_state.current_subject = subject
                        st.session_state.chat_history = []
                        st.rerun()
        else:
            # Show chat interface
            self._show_chat_interface()
    
    def _show_chat_interface(self):
        """Show chat interface for selected subject"""
        st.subheader(f"💬 Chat dengan Guru {st.session_state.current_subject}")
        
        # Initialize AI greeting
        if not st.session_state.chat_history:
            greeting = f"Halo! Saya guru {st.session_state.current_subject} untuk jenjang {st.session_state.grade_level}. Ada yang bisa saya bajar?"
            st.session_state.chat_history.append({"role": "assistant", "content": greeting})
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "assistant":
                    with st.chat_message("assistant", avatar="👨‍🏫"):
                        st.markdown(message["content"])
                else:
                    with st.chat_message("user", avatar="👨‍🎓"):
                        st.markdown(message["content"])
        
        # Chat input
        st.markdown("---")
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_area(
                "Pesan Anda:",
                key="chat_input",
                height=100,
                placeholder="Ketik pesan Anda di sini... (Shift+Enter untuk baris baru, Enter untuk mengirim)",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("Kirim", type="primary", use_container_width=True)
        
        # Handle send
        if send_button and user_input:
            # Check rate limit
            if not self.security.check_rate_limit(st.session_state.user_id, "chat"):
                st.error(f"Tunggu {Config.RATE_LIMIT_SECONDS} detik sebelum mengirim pesan lagi.")
                time.sleep(1)
                st.rerun()
            
            # Sanitize input
            sanitized_input = self.security.sanitize_input(user_input)
            if not self.security.validate_sql_input(sanitized_input):
                st.error("Input tidak valid.")
                st.rerun()
            
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": sanitized_input})
            
            # Get AI response
            with st.spinner("Guru sedang mengetik..."):
                try:
                    response = self.ai.get_response(
                        sanitized_input,
                        st.session_state.current_subject,
                        st.session_state.grade_level
                    )
                    
                    # Save to database
                    self.db.save_chat({
                        'user_id': st.session_state.user_id,
                        'subject': st.session_state.current_subject,
                        'grade_level': st.session_state.grade_level,
                        'user_message': sanitized_input,
                        'ai_response': response,
                        'ai_provider': 'gemini'  # You can track which provider was used
                    })
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    # Update rate limit
                    self.security.update_rate_limit(st.session_state.user_id, "chat")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            st.rerun()
    
    def reflection_page(self):
        """Reflection page"""
        st.title("🤔 Refleksi")
        st.markdown("---")
        
        if st.button("← Kembali ke Menu Utama"):
            st.session_state.page = 'main_menu'
            st.rerun()
        
        subjects = Config.SUBJECTS.get(st.session_state.grade_level, [])
        
        # Handle religion subjects
        if "AGAMA" in subjects:
            subjects.remove("AGAMA")
            subjects.extend(Config.RELIGIONS)
        
        cols = st.columns(4)
        for idx, subject in enumerate(subjects):
            with cols[idx % 4]:
                if st.button(subject, use_container_width=True, key=f"refl_{idx}"):
                    st.session_state.current_subject = subject
                    st.session_state.page = 'reflection_detail'
                    st.rerun()
    
    def reflection_detail_page(self):
        """Reflection detail page"""
        st.title(f"🤔 Refleksi - {st.session_state.current_subject}")
        st.markdown("---")
        
        if st.button("← Kembali"):
            st.session_state.page = 'reflection'
            st.rerun()
        
        # Generate reflection story
        with st.spinner("Membuat cerita refleksi..."):
            story_prompt = f"""
            Buatkan cerita pendek atau skenario untuk refleksi siswa {st.session_state.grade_level} 
            tentang mata pelajaran {st.session_state.current_subject}.
            
            Cerita harus memicu pemikiran kritis dan refleksi diri.
            Panjang: 150-200 kata.
            """
            
            story = self.ai.get_response(
                story_prompt,
                st.session_state.current_subject,
                st.session_state.grade_level
            )
        
        st.subheader("Cerita untuk Refleksi:")
        st.markdown(f"> {story}")
        st.markdown("---")
        
        st.subheader("Refleksi Anda:")
        reflection_text = st.text_area(
            "Tulis refleksi Anda berdasarkan cerita di atas:",
            height=200,
            placeholder="Apa yang Anda pelajari? Bagaimana hubungannya dengan pengalaman Anda? Apa yang akan Anda lakukan berbeda?"
        )
        
        if st.button("Kirim Refleksi", type="primary"):
            if reflection_text:
                with st.spinner("Mengoreksi refleksi..."):
                    # Grade reflection
                    result = self.ai.grade_reflection(
                        reflection_text,
                        st.session_state.current_subject,
                        st.session_state.grade_level
                    )
                    
                    # Save to database
                    self.db.save_reflection({
                        'user_id': st.session_state.user_id,
                        'subject': st.session_state.current_subject,
                        'reflection_text': reflection_text,
                        'correction': result['correction'],
                        'score': result['score']
                    })
                    
                    # Show results
                    st.success("Refleksi telah disimpan!")
                    st.subheader("Hasil Koreksi:")
                    st.markdown(f"**Nilai:** {result['score']}/100")
                    st.markdown(f"**Koreksi:** {result['correction']}")
                    st.markdown(f"**Feedback:** {result['feedback']}")
            else:
                st.error("Silakan tulis refleksi terlebih dahulu.")
    
    def idea_validation_page(self):
        """Idea validation page"""
        st.title("💡 Validasi Ide")
        st.markdown("---")
        
        if st.button("← Kembali ke Menu Utama"):
            st.session_state.page = 'main_menu'
            st.rerun()
        
        st.subheader("Jelaskan Ide Anda")
        idea = st.text_area(
            "Deskripsikan ide atau konsep yang ingin Anda validasi:",
            height=150,
            placeholder="Contoh: Saya ingin membuat sistem penyiraman tanaman otomatis menggunakan Arduino..."
        )
        
        if st.button("Validasi Ide", type="primary"):
            if idea:
                with st.spinner("Membuat POC (Proof of Concept)..."):
                    prompt = f"""
                    Buatkan POC (Proof of Concept) sederhana untuk ide berikut:
                    
                    Ide: {idea}
                    
                    POC harus mencakup:
                    1. Komponen yang dibutuhkan
                    2. Langkah-langkah implementasi
                    3. Sketsa/diagram sederhana (dalam bentuk deskripsi)
                    4. Estimasi biaya dan waktu
                    5. Cara replikasi di dunia nyata
                    
                    Format dengan jelas dan mudah diikuti.
                    """
                    
                    response = self.ai.get_response(
                        prompt,
                        "Teknologi",
                        "Umum"
                    )
                    
                    st.subheader("POC (Proof of Concept):")
                    st.markdown(response)
            else:
                st.error("Silakan jelaskan ide Anda terlebih dahulu.")
    
    def exam_page(self):
        """Exam page"""
        st.title("📝 Uji Kompetensi")
        st.markdown("---")
        
        if st.button("← Kembali ke Menu Utama"):
            st.session_state.page = 'main_menu'
            st.rerun()
        
        subjects = Config.SUBJECTS.get(st.session_state.grade_level, [])
        
        # Handle religion subjects
        if "AGAMA" in subjects:
            subjects.remove("AGAMA")
            subjects.extend(Config.RELIGIONS)
        
        if not st.session_state.exam_questions:
            # Show subject selection
            st.subheader("Pilih Mata Pelajaran")
            
            cols = st.columns(4)
            for idx, subject in enumerate(subjects):
                with cols[idx % 4]:
                    if st.button(subject, use_container_width=True, key=f"exam_{idx}"):
                        st.session_state.current_subject = subject
                        with st.spinner("Membuat soal ujian..."):
                            # Generate exam questions
                            questions = self.ai.generate_exam_questions(
                                subject,
                                st.session_state.grade_level
                            )
                            st.session_state.exam_questions = questions
                            st.session_state.exam_answers = {}
                        st.rerun()
        else:
            # Show exam questions
            self._show_exam_questions()
    
    def _show_exam_questions(self):
        """Display exam questions"""
        st.subheader(f"Ujian: {st.session_state.current_subject}")
        st.markdown("---")
        
        questions = st.session_state.exam_questions
        answers = st.session_state.exam_answers
        
        # Multiple choice questions
        st.markdown("### Soal Pilihan Ganda")
        for idx, mc in enumerate(questions['multiple_choice']):
            st.markdown(f"**{idx + 1}. {mc['question']}**")
            
            # Create answer options
            options = mc['options']
            answer_key = f"mc_{idx}"
            
            # Use radio buttons for single selection
            selected = st.radio(
                f"Pilih jawaban untuk soal {idx + 1}:",
                options,
                key=answer_key,
                index=None
            )
            
            # Store answer
            if selected:
                # Extract letter from selected option (e.g., "A" from "A. Jawaban")
                answer_letter = selected[0] if selected[0].isalpha() else "A"
                answers[answer_key] = answer_letter
        
        st.markdown("---")
        
        # Essay questions
        st.markdown("### Soal Esai")
        for idx, essay in enumerate(questions['essay_questions']):
            st.markdown(f"**Esai {idx + 1}. {essay['question']}**")
            essay_key = f"essay_{idx}"
            
            answer = st.text_area(
                f"Jawaban Anda untuk esai {idx + 1}:",
                height=150,
                key=essay_key
            )
            
            if answer:
                answers[essay_key] = answer
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Kembali ke Daftar Mapel", use_container_width=True):
                st.session_state.exam_questions = None
                st.session_state.exam_answers = {}
                st.rerun()
        
        with col2:
            if st.button("Kirim Jawaban", type="primary", use_container_width=True):
                # Check if all questions answered
                total_mc = len(questions['multiple_choice'])
                total_essay = len(questions['essay_questions'])
                
                answered_mc = sum(1 for i in range(total_mc) if f"mc_{i}" in answers)
                answered_essay = sum(1 for i in range(total_essay) if f"essay_{i}" in answers)
                
                if answered_mc == total_mc and answered_essay == total_essay:
                    with st.spinner("Mengoreksi jawaban..."):
                        # Grade the exam
                        result = self.ai.grade_exam(questions, answers)
                        
                        # Save to database
                        self.db.save_exam({
                            'user_id': st.session_state.user_id,
                            'subject': st.session_state.current_subject,
                            'exam_data': json.dumps(questions, ensure_ascii=False),
                            'answers': json.dumps(answers, ensure_ascii=False),
                            'score': result['total_score']
                        })
                        
                        # Show results
                        st.success("Ujian telah dikoreksi!")
                        st.subheader("Hasil Ujian:")
                        st.markdown(f"**Total Nilai:** {result['total_score']}/100")
                        st.markdown(f"**Nilai PG:** {result['multiple_choice_score']}/{(total_mc * 2)}")
                        st.markdown(f"**Nilai Esai:** {result['essay_score']}/{(total_essay * 10)}")
                        
                        # Show corrections
                        with st.expander("Lihat Detail Koreksi"):
                            st.json(result)
                else:
                    st.error(f"Harap jawab semua soal! ({answered_mc}/{total_mc} PG, {answered_essay}/{total_essay} Esai)")
    
    def knowledge_level_page(self):
        """Knowledge level page"""
        st.title("📊 Level Pengetahuan")
        st.markdown("---")
        
        if st.button("← Kembali ke Menu Utama"):
            st.session_state.page = 'main_menu'
            st.rerun()
        
        # Calculate overall score from reflections and exams
        user_id = st.session_state.user_id
        
        # Get user data
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            st.error("Data pengguna tidak ditemukan.")
            return
        
        # Get reflections
        reflections = self.db.get_session().query(Reflection).filter_by(user_id=user_id).all()
        exams = self.db.get_session().query(Exam).filter_by(user_id=user_id).all()
        
        # Calculate average scores
        reflection_scores = [r.score for r in reflections if r.score]
        exam_scores = [e.score for e in exams if e.score]
        
        all_scores = reflection_scores + exam_scores
        
        if all_scores:
            avg_score = sum(all_scores) / len(all_scores)
            
            # Determine knowledge level
            if avg_score >= 90:
                level = "Sangat Tinggi"
                color = "🟢"
            elif avg_score >= 75:
                level = "Tinggi"
                color = "🟡"
            elif avg_score >= 60:
                level = "Sedang"
                color = "🟠"
            elif avg_score >= 40:
                level = "Rendah"
                color = "🔴"
            else:
                level = "Sangat Rendah"
                color = "⚫"
            
            st.subheader(f"{color} Level Pengetahuan Anda: **{level}**")
            st.markdown(f"**Rata-rata Nilai:** {avg_score:.2f}/100")
            
            # Create progress bar
            st.progress(avg_score / 100)
            
            # Show detailed breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Refleksi", f"{len(reflections)} kali")
                if reflection_scores:
                    st.metric("Rata-rata Refleksi", f"{sum(reflection_scores)/len(reflection_scores):.1f}")
            
            with col2:
                st.metric("Ujian", f"{len(exams)} kali")
                if exam_scores:
                    st.metric("Rata-rata Ujian", f"{sum(exam_scores)/len(exam_scores):.1f}")
            
            # Generate AI feedback
            with st.spinner("Membuat catatan..."):
                feedback_prompt = f"""
                Berikan catatan konstruktif untuk siswa dengan:
                - Rata-rata nilai: {avg_score:.2f}/100
                - Level pengetahuan: {level}
                - Jenjang: {user.grade_level}
                - Jumlah refleksi: {len(reflections)}
                - Jumlah ujian: {len(exams)}
                
                Berikan saran untuk meningkatkan pembelajaran.
                """
                
                feedback = self.ai.get_response(feedback_prompt, "Evaluasi", "Umum")
                
                st.subheader("📝 Catatan dan Saran:")
                st.markdown(feedback)
        else:
            st.info("Belum ada data penilaian. Selesaikan beberapa refleksi dan ujian terlebih dahulu.")
    
    def reminder_page(self):
        """Reminder page"""
        st.title("⏰ Pengingat Belajar")
        st.markdown("---")
        
        if st.button("← Kembali ke Menu Utama"):
            st.session_state.page = 'main_menu'
            st.rerun()
        
        menu = st.radio(
            "Pilih menu:",
            ["BUAT PENGINGAT", "HAPUS PENGINGAT"],
            horizontal=True
        )
        
        st.markdown("---")
        
        if menu == "BUAT PENGINGAT":
            self._create_reminder()
        else:
            self._delete_reminder()
    
    def _create_reminder(self):
        """Create reminder"""
        st.subheader("Buat Pengingat Belajar")
        
        email = st.text_input("Email untuk pengingat:")
        reminder_time = st.time_input("Waktu pengingat harian:")
        
        if st.button("Kirim OTP", type="primary"):
            if email and "@" in email and "." in email:
                # Check rate limit
                if not self.security.check_rate_limit(email, "otp"):
                    st.error(f"Tunggu {Config.OTP_COOLDOWN_SECONDS} detik sebelum meminta OTP lagi.")
                    return
                
                # Generate and send OTP
                otp = self.security.generate_otp()
                
                # Store OTP in session
                st.session_state['otp_email'] = email
                st.session_state['otp_code'] = otp
                st.session_state['otp_time'] = datetime.now()
                st.session_state['otp_attempts'] = 0
                
                # Send email
                if self.send_otp_email(email, otp):
                    st.success("OTP telah dikirim ke email Anda!")
                    self.security.update_rate_limit(email, "otp")
                else:
                    st.error("Gagal mengirim OTP. Coba lagi nanti.")
            else:
                st.error("Masukkan email yang valid.")
        
        # OTP verification
        if 'otp_email' in st.session_state:
            st.markdown("---")
            st.subheader("Verifikasi OTP")
            
            otp_input = st.text_input("Masukkan 6 digit OTP:")
            
            if st.button("Verifikasi OTP", type="secondary"):
                if otp_input:
                    # Check OTP expiry
                    time_passed = (datetime.now() - st.session_state['otp_time']).total_seconds()
                    
                    if time_passed > Config.OTP_EXPIRY_MINUTES * 60:
                        st.error("OTP telah kedaluwarsa. Minta OTP baru.")
                        del st.session_state['otp_email']
                        del st.session_state['otp_code']
                    elif st.session_state['otp_attempts'] >= 3:
                        st.error("Terlalu banyak percobaan. Tunggu 30 menit.")
                    elif otp_input == st.session_state['otp_code']:
                        # Save reminder
                        session = self.db.get_session()
                        try:
                            reminder = Reminder(
                                user_id=st.session_state.user_id,
                                email=st.session_state['otp_email'],
                                reminder_time=reminder_time.strftime("%H:%M"),
                                is_active=True
                            )
                            session.add(reminder)
                            session.commit()
                            
                            st.success(f"Pengingat berhasil dibuat! Akan dikirim setiap hari pukul {reminder_time.strftime('%H:%M')}")
                            
                            # Clear OTP data
                            del st.session_state['otp_email']
                            del st.session_state['otp_code']
                        except Exception as e:
                            st.error(f"Gagal menyimpan pengingat: {str(e)}")
                    else:
                        st.session_state['otp_attempts'] += 1
                        st.error(f"OTP salah. Percobaan {st.session_state['otp_attempts']}/3")
                else:
                    st.error("Masukkan OTP")
    
    def _delete_reminder(self):
        """Delete reminder"""
        st.subheader("Hapus Pengingat")
        
        email = st.text_input("Email pengingat yang akan dihapus:")
        
        if st.button("Kirim OTP untuk Hapus", type="primary"):
            if email:
                # Check if reminder exists
                session = self.db.get_session()
                reminder = session.query(Reminder).filter_by(
                    user_id=st.session_state.user_id,
                    email=email
                ).first()
                
                if reminder:
                    # Generate and send OTP
                    otp = self.security.generate_otp()
                    
                    # Store OTP in session
                    st.session_state['delete_otp_email'] = email
                    st.session_state['delete_otp_code'] = otp
                    st.session_state['delete_otp_time'] = datetime.now()
                    st.session_state['delete_otp_attempts'] = 0
                    
                    # Send email
                    if self.send_otp_email(email, otp):
                        st.success("OTP telah dikirim ke email Anda!")
                    else:
                        st.error("Gagal mengirim OTP. Coba lagi nanti.")
                else:
                    st.error("Tidak ada pengingat dengan email tersebut.")
            else:
                st.error("Masukkan email")
        
        # OTP verification for deletion
        if 'delete_otp_email' in st.session_state:
            st.markdown("---")
            st.subheader("Verifikasi OTP untuk Hapus")
            
            otp_input = st.text_input("Masukkan 6 digit OTP:", key="delete_otp")
            
            if st.button("Hapus Pengingat", type="secondary"):
                if otp_input:
                    # Check OTP expiry
                    time_passed = (datetime.now() - st.session_state['delete_otp_time']).total_seconds()
                    
                    if time_passed > Config.OTP_EXPIRY_MINUTES * 60:
                        st.error("OTP telah kedaluwarsa. Minta OTP baru.")
                        del st.session_state['delete_otp_email']
                        del st.session_state['delete_otp_code']
                    elif st.session_state['delete_otp_attempts'] >= 3:
                        st.error("Terlalu banyak percobaan. Tunggu 30 menit.")
                    elif otp_input == st.session_state['delete_otp_code']:
                        # Delete reminder
                        session = self.db.get_session()
                        try:
                            reminder = session.query(Reminder).filter_by(
                                user_id=st.session_state.user_id,
                                email=st.session_state['delete_otp_email']
                            ).first()
                            
                            if reminder:
                                session.delete(reminder)
                                session.commit()
                                st.success("Pengingat berhasil dihapus!")
                            else:
                                st.error("Pengingat tidak ditemukan.")
                            
                            # Clear OTP data
                            del st.session_state['delete_otp_email']
                            del st.session_state['delete_otp_code']
                        except Exception as e:
                            st.error(f"Gagal menghapus pengingat: {str(e)}")
                    else:
                        st.session_state['delete_otp_attempts'] += 1
                        st.error(f"OTP salah. Percobaan {st.session_state['delete_otp_attempts']}/3")
                else:
                    st.error("Masukkan OTP")
    
    def run(self):
        """Main application runner"""
        # Check authentication
        if not self.auth.is_authenticated():
            st.session_state.page = 'login'
        
        # Route to appropriate page
        if st.session_state.page == 'login':
            self.login_page()
        elif st.session_state.page == 'select_grade':
            self.select_grade_page()
        elif st.session_state.page == 'main_menu':
            self.main_menu_page()
        elif st.session_state.page == 'interactive_learning':
            self.interactive_learning_page()
        elif st.session_state.page == 'reflection':
            self.reflection_page()
        elif st.session_state.page == 'reflection_detail':
            self.reflection_detail_page()
        elif st.session_state.page == 'idea_validation':
            self.idea_validation_page()
        elif st.session_state.page == 'exam':
            self.exam_page()
        elif st.session_state.page == 'knowledge_level':
            self.knowledge_level_page()
        elif st.session_state.page == 'reminder':
            self.reminder_page()

# Run the application
if __name__ == "__main__":
    # Initialize the platform
    platform = EducationPlatform()
    platform.run()
