import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

#  KONFIGURASI TAMPILAN 
st.set_page_config(page_title="🍽️ Chatbot Menu Harian", page_icon="🍜", layout="centered")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #fff8f0 0%, #ffe6cc 100%);
}
.title {
    font-size: 36px;
    font-weight: 700;
    color: #e67300;
    text-align: center;
    margin-bottom: 10px;
}
.subtitle {
    text-align: center;
    color: #666666;
    font-size: 16px;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🍱 Rekomendasi Menu Harian</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Masukkan API key kamu dan mulai tanya menu hari ini!</div>', unsafe_allow_html=True)


# INPUT GOOGLE API KEY
def get_api_key_input():
    """Minta user untuk masukkan Google API Key."""
    if "GOOGLE_API_KEY" not in st.session_state or not st.session_state["GOOGLE_API_KEY"]:
        with st.form("api_key_form"):
            api_key = st.text_input("🔑 Masukkan Google API Key kamu:", type="password", help="API key dari Google AI Studio")
            submitted = st.form_submit_button("Simpan Key dan Mulai Chat")
            if submitted:
                if api_key.strip() == "":
                    st.warning("API key tidak boleh kosong!")
                    st.stop()
                st.session_state["GOOGLE_API_KEY"] = api_key
                os.environ["GOOGLE_API_KEY"] = api_key
                st.success("✅ API Key berhasil disimpan! Silakan mulai chat di bawah.")
                st.rerun()
    else:
        os.environ["GOOGLE_API_KEY"] = st.session_state["GOOGLE_API_KEY"]


#  LOAD MODEL 
def load_llm():
    # Load model dari Google Generative AI.
    if "llm" not in st.session_state:
        st.session_state["llm"] = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return st.session_state["llm"]


# CHAT SESSION
def get_chat_history():
    # Ambil atau buat riwayat chat baru.
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            SystemMessage(content=(
                "Kamu adalah asisten kuliner yang hanya menjawab topik seputar makanan dan minuman. "
                "Fokuslah untuk memberikan rekomendasi menu, ide masakan, atau saran kuliner. "
                "Jika pengguna menanyakan hal di luar topik kuliner (misalnya teknologi, politik, atau lainnya), "
                "tolak dengan sopan dan arahkan kembali ke topik makanan. Gunakan bahasa ramah dan santai."
            )),
            AIMessage(content="Hai! Aku asisten rekomendasi makananmu 🍛. Mau aku bantu pilih menu untuk sarapan, makan siang, atau malam?")
        ]
    return st.session_state["chat_history"]


def display_chat_message(message):
    # Tampilkan satu pesan chat.
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)


def display_chat_history(chat_history):
    # Tampilkan semua riwayat chat.
    for chat in chat_history:
        display_chat_message(chat)


def user_query_to_llm(llm, chat_history):
    # Ambil input dari user dan kirim ke LLM.
    prompt = st.chat_input("Tanyakan rekomendasi makanan hari ini...")
    if not prompt:
        return

    chat_history.append(HumanMessage(content=prompt))
    display_chat_message(chat_history[-1])

    with st.spinner("Sedang memikirkan menu yang lezat untukmu... 🍳"):
        response = llm.invoke([
            *chat_history,
            HumanMessage(content="Berikan rekomendasi makanan yang lezat dan mudah dibuat untuk konteks permintaan user di atas. Gunakan gaya bahasa ramah dan santai.")
        ])
    chat_history.append(response)
    display_chat_message(response)


# MAIN PROGRAM 
def main():
    get_api_key_input()

    if "GOOGLE_API_KEY" not in st.session_state or not st.session_state["GOOGLE_API_KEY"]:
        st.stop()  # Berhenti sampai user memasukkan API key

    llm = load_llm()
    chat_history = get_chat_history()
    display_chat_history(chat_history)
    user_query_to_llm(llm, chat_history)


if __name__ == "__main__":
    main()
