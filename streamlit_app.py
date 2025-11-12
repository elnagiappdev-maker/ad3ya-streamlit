import base64
import mimetypes
from pathlib import Path
import unicodedata
import uuid
import streamlit as st

st.set_page_config(
    page_title="أدعية صوتية",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- Paths ----------
BASE = Path(__file__).parent
AUDIO_DIR = BASE / "audio"
ASSETS_DIR = BASE / "assets"
BG_IMAGE  = ASSETS_DIR / "bg.jpg"
DEDIC_FILE = ASSETS_DIR / "dedications.txt"

# ---------- Helpers ----------
def guess_mime(path_or_name: str) -> str:
    mime, _ = mimetypes.guess_type(path_or_name)
    if not mime:
        ext = str(path_or_name).split(".")[-1].lower()
        return {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "ogg": "audio/ogg",
            "m4a": "audio/mp4",
        }.get(ext, "audio/mpeg")
    return mime

def to_data_url_file(path: Path) -> str:
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{guess_mime(path.name)};base64,{b64}"

def css_background_from(path: Path) -> str:
    if not path.exists():
        return "<style>html, body, .block-container {background:#0d1117;}</style>"
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    mime = "image/jpeg" if path.suffix.lower() in (".jpg",".jpeg") else "image/png"
    return f"""
    <style>
    .stApp {{
      background-image: url('data:{mime};base64,{b64}');
      background-size: cover;
      background-position: center;
      background-attachment: fixed;
    }}
    .block-container {{
      background: rgba(255,255,255,0.85);
      border-radius: 16px;
      padding: 18px;
      margin-top: 18px;
    }}
    </style>
    """

def load_dedications(path: Path) -> list[str]:
    defaults = [
        "الشيخ الدكتور عبد الرحمن الناجي",
        "الشيخ محمد الناجي محمد إبراهيم",
        "الشيخ عبد الحي البشير",
        "الدكتور عبد الباقي الناجي",
        "الباشمهندس عثمان عباس عبد العاطي",
        "البروفيسور مصطفى محمد الحاج",
        "الأستاذ عبد الرحمن أحمد عثمان",
        "الأخ بابكر محمد إبراهيم عيدروس",
        "الأستاذ مجد الدين أحمد البشير",
        "الحاجة ٱسيا مبارك فضيل",
    ]
    if not path.exists():
        return defaults
    try:
        text = path.read_text(encoding="utf-8")
        names = [ln.strip() for ln in text.splitlines() if ln.strip()]
        seen, out = set(), []
        for n in names:
            if n not in seen:
                seen.add(n)
                out.append(n)
        return out or defaults
    except Exception:
        return defaults

def normalize_for_sort(s: str) -> str:
    return unicodedata.normalize("NFKD", s).casefold()

# ---------- Styles ----------
st.markdown("""
<style>
html,body,[class*="css"]{
  direction:rtl;text-align:right;
  font-family:"Noto Naskh Arabic","Noto Sans Arabic",Tahoma,Arial,sans-serif;
}
h1,h2,h3{text-align:center}
.small{font-size:12px;color:#444}
.dedication{
  border:1px solid #e6e6e6;border-radius:16px;
  padding:12px 14px;background:#fafafa
}
</style>
""", unsafe_allow_html=True)
st.markdown(css_background_from(BG_IMAGE), unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("<h2>أدعية صوتية</h2>", unsafe_allow_html=True)

# ---------- Dedications ----------
names = load_dedications(DEDIC_FILE)
st.markdown(
    "<div class='dedication' style='text-align:center'><b>صدقة جارية</b><br>لأرواح<br>"
    + "".join(f"<div>{n}</div>" for n in names) + "</div>",
    unsafe_allow_html=True,
)

# ---------- Collect audio files ----------
AUDIO_DIR.mkdir(exist_ok=True)
repo_files = [p for p in AUDIO_DIR.glob("*") if p.suffix.lower() in (".mp3",".wav",".ogg",".m4a")]
repo_files.sort(key=lambda p: normalize_for_sort(p.stem))

if not repo_files:
    st.warning("لا توجد تسجيلات بعد. أضف ملفات إلى مجلد audio/ وأعد النشر.")
    st.stop()

labels = [p.stem for p in repo_files]
label = st.selectbox("اختر التسجيل:", labels, index=0)
current = next(p for p in repo_files if p.stem == label)

# ---------- Repetition ----------
st.markdown("#### عدد مرات التكرار")
if "reps" not in st.session_state:
    st.session_state.reps = 100
cols = st.columns(6)
for i,n in enumerate([10,100,1000,2000,3000,4000]):
    with cols[i]:
        if st.button(f"{n}",use_container_width=True,key=f"r{n}"):
            st.session_state.reps = n
reps = st.number_input("أو أدخل رقمًا يدويًا:",1,100000,st.session_state.reps)
st.session_state.reps = reps

# ---------- Player ----------
c1,c2,c3 = st.columns([1,1,2])
play = c1.button("▶ تشغيل")
pause = c2.button("⏸ إيقاف مؤقت")
restart = c3.button("⟲ من البداية")
loops = int(st.session_state.reps)
aud_id = f"a{uuid.uuid4().hex}"
url = to_data_url_file(current)
html = f"""
<div><div class="small">يشغّل الآن: {label}</div>
<div class="small">المتبقي: <span id='r'>{loops}</span> / {loops}</div>
<audio id='{aud_id}' controls style='width:100%'><source src='{url}'></audio></div>
<script>
const a=document.getElementById('{aud_id}');let n={loops};
const R=document.getElementById('r');
a.onended=()=>{{if(n>1){{n--;R.textContent=n;a.currentTime=0;a.play();}}}};
{"a.play();" if play or restart else ""}
{"a.pause();" if pause else ""}
</script>
"""
st.components.v1.html(html,height=180)
st.markdown("<div class='small' style='text-align:center'>🔒 التسجيلات ثابتة من داخل المستودع.</div>",unsafe_allow_html=True)
