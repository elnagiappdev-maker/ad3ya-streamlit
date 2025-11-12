
import base64
import mimetypes
from pathlib import Path
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
AUDIO_DIR = BASE / "audio"             # put audio files here; auto-detected
ASSETS_DIR = BASE / "assets"
BG_IMAGE  = ASSETS_DIR / "bg.jpg"      # optional
DEDIC_FILE = ASSETS_DIR / "dedications.txt"  # one name per line, UTF-8

# ---------- Helpers ----------
def guess_mime(path_or_name: str) -> str:
    import mimetypes
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

def to_data_url_bytes(raw: bytes, name_hint: str) -> str:
    mime = guess_mime(name_hint)
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"

def to_data_url_file(path: Path) -> str:
    raw = path.read_bytes()
    return to_data_url_bytes(raw, path.name)

def css_background_from(path: Path) -> str:
    if not path.exists():
        return """
        <style>
        html, body, .block-container { background: #0d1117; }
        </style>
        """
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    ext = path.suffix.lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    return f"""
    <style>
    html, body {{ background: #000; }}
    .stApp {{
      background-image: url('data:{mime};base64,{b64}');
      background-size: cover;
      background-position: center center;
      background-attachment: fixed;
    }}
    .block-container {{
      background: rgba(255,255,255,0.86);
      border-radius: 16px;
      padding: 18px;
      margin-top: 18px;
    }}
    </style>
    """

def load_dedications(path: Path) -> list[str]:
    defaults = [
        "الشيخ الدكتور عبد الرحمن الناجي",
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
        names = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        # de-duplicate while preserving order
        seen = set()
        out = []
        for n in names:
            if n not in seen:
                seen.add(n)
                out.append(n)
        return out or defaults
    except Exception:
        return defaults

# ---------- Styles (Arabic RTL) ----------
ARABIC_BASE_CSS = """
<style>
html, body, [class*="css"] {
  direction: rtl;
  text-align: right;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Naskh Arabic", "Noto Sans Arabic", "Droid Arabic Naskh", "Tahoma", Arial, sans-serif !important;
}
h1,h2,h3 { text-align: center; }
.dedication {
  border: 1px solid #e6e6e6;
  border-radius: 16px;
  padding: 12px 14px;
  background: #fafafa;
}
.small { font-size: 12px; color: #444; }
</style>
"""
st.markdown(ARABIC_BASE_CSS, unsafe_allow_html=True)
st.markdown(css_background_from(BG_IMAGE), unsafe_allow_html=True)

# ---------- Header + Dedication ----------
st.markdown("<h2>أدعية صوتية</h2>", unsafe_allow_html=True)

names = load_dedications(DEDIC_FILE)
with st.container():
    html_names = "".join(f"<div>{n}</div>" for n in names)
    st.markdown(
        f"""
<div class="dedication" style="text-align:center">
  <div style="font-weight:700;">صدقة جارية</div>
  <div style="margin-top:2px;">لأرواح</div>
  <div style="height:6px;"></div>
  {html_names}
</div>
""",
        unsafe_allow_html=True,
    )

# ---------- Auto-detect repo audio files ----------
AUDIO_DIR.mkdir(exist_ok=True)
repo_files = []
for p in sorted(AUDIO_DIR.glob("*")):
    if p.suffix.lower() in (".mp3", ".wav", ".ogg", ".m4a"):
        repo_files.append(p)

# ---------- Optional multi-upload (session only) ----------
st.markdown("### ارفع تسجيلات صوتية (اختياري – لا يتم حفظها بعد إعادة التشغيل)")
uploads = st.file_uploader(
    "ملفات MP3 / WAV / OGG / M4A (يمكن رفع عدة ملفات)",
    type=["mp3", "wav", "ogg", "m4a"],
    accept_multiple_files=True,
    key="uploader_multi",
)

choices = []
for p in repo_files:
    choices.append(("📦 من المستودع — " + p.name, ("repo", p)))
if uploads:
    for up in uploads:
        choices.append(("⬆️ مرفوع الآن — " + up.name, ("up", up)))

if not choices:
    st.info("أضف ملفات إلى مجلد **audio/** في المستودع أو ارفع ملفات مؤقتًا لبدء التشغيل.")
    st.stop()

label = st.selectbox("اختر التسجيل:", [c[0] for c in choices], index=0)
source, payload = next(c[1] for c in choices if c[0] == label)

# Lazy-load only selected
if source == "repo":
    display_name = payload.name
    data_url = to_data_url_file(payload)
else:
    display_name = payload.name
    raw = payload.read()
    payload.seek(0)
    data_url = to_data_url_bytes(raw, payload.name)

# ---------- Repetition controls ----------
st.markdown("#### عدد مرات التكرار")
if "reps" not in st.session_state:
    st.session_state.reps = 100

cols = st.columns(6)
for i, n in enumerate([10, 100, 1000, 2000, 3000, 4000]):
    with cols[i]:
        if st.button(f"{n}", use_container_width=True, key=f"chip_{n}"):
            st.session_state.reps = n

reps = st.number_input("أو أدخل رقمًا يدويًا:", min_value=1, value=st.session_state.reps, step=1)
st.session_state.reps = reps

# ---------- Player controls ----------
c1, c2, c3 = st.columns([1, 1, 2])
play_clicked = c1.button("▶ تشغيل", use_container_width=True)
pause_clicked = c2.button("⏸ إيقاف مؤقت", use_container_width=True)
restart_clicked = c3.button("⟲ من البداية", use_container_width=True)

aud_id = f"aud_{uuid.uuid4().hex}"
wrap_id = f"wrap_{uuid.uuid4().hex}"
loops = int(st.session_state.reps)

html = f"""
<div id="{wrap_id}">
  <div class="small">يشغّل الآن: {display_name}</div>
  <div class="small">المتبقي: <span id="loop-remaining">{loops}</span> / {loops}</div>
  <div style="margin-top:8px;">
    <audio id="{aud_id}" preload="auto" controls style="width:100%">
      <source src="{data_url}">
      متصفحك لا يدعم مشغل الصوت.
    </audio>
  </div>
</div>
<script>
(function() {{
  const audio = document.getElementById("{aud_id}");
  if (!audio) return;

  let total = {loops};
  const remainingEl = document.getElementById("loop-remaining");
  const restartFlag = {"true" if restart_clicked else "false"};
  const pauseFlag = {"true" if pause_clicked else "false"};
  const autoFlag = {"true" if (play_clicked or restart_clicked) else "false"};

  if (restartFlag) {{
    try {{ audio.currentTime = 0; }} catch(e) {{}}
    total = {loops};
    if (remainingEl) remainingEl.textContent = String(total);
  }}
  if (pauseFlag) {{
    try {{ audio.pause(); }} catch(e) {{}}
  }}

  function onEnded() {{
    if (total > 1) {{
      total -= 1;
      if (remainingEl) remainingEl.textContent = String(total);
      try {{ audio.currentTime = 0; audio.play().catch(()=>{{}}); }} catch(e) {{}}
    }} else {{
      try {{ audio.pause(); }} catch(e) {{}}
    }}
  }}
  audio.onended = null;
  audio.addEventListener("ended", onEnded, {{ once: false }});

  if (autoFlag) {{
    total = {loops};
    if (remainingEl) remainingEl.textContent = String(total);
    try {{ audio.currentTime = 0; audio.play().catch(()=>{{}}); }} catch(e) {{}}
  }}
}})();
</script>
"""
st.components.v1.html(html, height=180, scrolling=False)

st.markdown(
    "<div class='small' style='text-align:center;margin-top:18px;'>"
    "👥 لإضافة أسماء جديدة: حرّر الملف <code>assets/dedications.txt</code> في GitHub (اسم في كل سطر). "
    "🔒 ملفات المستودع ثابتة (audio/ و assets/). ⬆️ الرفع هنا مؤقت للجلسة."
    "</div>",
    unsafe_allow_html=True,
)
