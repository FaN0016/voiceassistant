# === HACK ANTI-ERROR PYTORCH 2.6 ===
import torch
_original_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load
# ===================================

import ollama
import time
import pyaudio
import wave
from faster_whisper import WhisperModel
import asyncio
import edge_tts
import pygame
import os
import re
import json
import speech_recognition as sr # Pustaka baru untuk pendengaran otomatis
from rvc_python.infer import RVCInference 

print("[System] Memuat model pendengaran (Whisper)...")
stt_model = WhisperModel("medium", device="cpu", compute_type="int8")

print("[System] Memuat mesin pengubah suara (RVC)...")
rvc = RVCInference(device="cpu")

# Fungsi Pendengaran Pasif (Otomatis tanpa tekan tombol)
def dengarkan_pasif():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n💤 [Mode Pasif] Menunggu panggilan 'Miku'...")
        # Menyesuaikan sensitivitas dengan suara bising di ruangan Anda (kipas/AC)
        r.adjust_for_ambient_noise(source, duration=1) 
        
        try:
            # Otomatis merekam saat ada suara, maksimal 10 detik per kalimat
            audio = r.listen(source, phrase_time_limit=10) 
            print("⏳ [Suara terdeteksi, memproses...]")
            
            with open("temp_suara.wav", "wb") as f:
                f.write(audio.get_wav_data())
                
            segments, info = stt_model.transcribe(
                "temp_suara.wav", 
                beam_size=5, # Diperkecil agar respons lebih cepat
                language="id"
            )
            
            teks_hasil = "".join([segment.text for segment in segments])
            return teks_hasil.strip()
            
        except Exception:
            return ""

def tanya_asisten(teks_input):
    print("\n🧠 [Berpikir dan Mengingat...]")
    waktu_mulai = time.time()
    
    file_memori = "memori_miku.json"
    riwayat = []
    
    # 1. Membaca ingatan masa lalu (jika ada)
    if os.path.exists(file_memori):
        with open(file_memori, "r", encoding="utf-8") as f:
            try:
                riwayat = json.load(f)
            except json.JSONDecodeError:
                riwayat = []
                
    # 2. Menyiapkan kepribadian dasar AI
    messages = [{
        'role': 'system',
        'content': 'Kamu adalah asisten virtual pribadi yang ramah bernama Miku. Jawablah menggunakan bahasa Indonesia yang santai tapi sopan. Jawab dengan singkat dan padat.'
    }]
    
    # 3. Memasukkan maksimal 10 percakapan terakhir agar AI tidak kebingungan
    messages.extend(riwayat[-10:])
    
    # 4. Memasukkan pertanyaan Anda yang baru
    messages.append({
        'role': 'user',
        'content': teks_input
    })
    
    # 5. Mengirim semuanya ke Otak (Ollama)
    response = ollama.chat(model='qwen2.5:1.5b', messages=messages)
    jawaban = response['message']['content']
    waktu_selesai = time.time()
    durasi = waktu_selesai - waktu_mulai
    
    # 6. Menyimpan percakapan baru ke dalam ingatan
    riwayat.append({'role': 'user', 'content': teks_input})
    riwayat.append({'role': 'assistant', 'content': jawaban})
    
    with open(file_memori, "w", encoding="utf-8") as f:
        json.dump(riwayat, f, indent=4, ensure_ascii=False)
    
    return jawaban, durasi

def berbicara(teks):
    print("🔊 [Menyiapkan Suara Dasar Edge-TTS...]")
    suara_dasar = "id-ID-GadisNeural" 
    file_mp3 = "suara_dasar.mp3"
    file_miku = "suara_miku.wav"
    
    async def generate_audio():
        # Kecepatan sudah diperlambat 15% sesuai permintaan Anda sebelumnya
        komunikator = edge_tts.Communicate(teks, suara_dasar, rate="-15%")
        await komunikator.save(file_mp3)
        
    asyncio.run(generate_audio())
    
    print("🪄 [Mengubah ke Pita Suara Miku...]")
    rvc.load_model("miku.pth") 
    rvc.set_params(f0method="rmvpe", f0up_key=0)
    rvc.infer_file(file_mp3, file_miku)
    
    print("🎶 [Memutar Jawaban Miku...]")
    pygame.mixer.init()
    pygame.mixer.music.load(file_miku)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
        
    pygame.mixer.quit()
    
    if os.path.exists(file_mp3):
        os.remove(file_mp3)
    if os.path.exists(file_miku):
        os.remove(file_miku)

if __name__ == "__main__":
    print("=== Prototype Asisten AI (Versi Hatsune Miku) ===")
    
    try:
        while True:
            # 1. Dengarkan lingkungan sekitar
            teks_user = dengarkan_pasif()
            
            if not teks_user:
                continue
                
            # 2. Cek apakah ada kata "Miku" di ucapan Anda (tidak peduli huruf besar/kecil)
            if "test" in teks_user.lower():
                print(f"🗣️ Anda berkata: '{teks_user}'")
                
                # Menghapus kata "Miku" dari pertanyaan agar AI fokus pada perintahnya
                pertanyaan_bersih = re.sub(r'(?i)miku', '', teks_user).strip()
                
                # Jika Anda HANYA memanggil "Miku" tanpa pertanyaan lain
                if len(pertanyaan_bersih) < 2:
                    jawaban_ai = "Ya? Ada yang bisa kubantu?"
                    waktu_proses = 0
                else:
                    jawaban_ai, waktu_proses = tanya_asisten(pertanyaan_bersih)
                
                print(f"🤖 Asisten: {jawaban_ai}")
                if waktu_proses > 0:
                    print(f"⏱️ [Log System: Berpikir selama {waktu_proses:.2f} detik]")
                
                berbicara(jawaban_ai) 
                print("-" * 50)
                
    except KeyboardInterrupt:
        print("\n[System] Mematikan asisten...")