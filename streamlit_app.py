
import base64
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
AUDIO_FILE = BASE / "audio" / "v1.ogg"     # <-- place your OGG here (exact name)
BG_IMAGE   = BASE / "assets" / "bg.jpg"    # <-- place your background photo here (jpg/png)

# ---------- Helpers ----------
def data_url_for_audio(path: Path) -> str | None:
    if not path.exists():
        return None
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:audio/ogg;base64,{b64}"

def css_background_from(path: Path) -> str:
    if not path.exists():
        # fallback to solid color if bg is missing
        return """
        <style>
        html, body, .block-container { background: #0d1117; }
        </style>
        """
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    # try to infer mime type by extension
    ext = path.suffix.lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    return f"""
    <style>
    html, body {{
      background: #000;
    }}
    .stApp {{
      background-image: url('data:{mime};base64,{b64}');
      background-size: cover;
      background-position: center center;
      background-attachment: fixed;
    }}
    /* backdrop for readability */
    .block-container {{
      background: rgba(255,255,255,0.86);
      border-radius: 16px;
      padding: 18px;
      margin-top: 18px;
    }}
    </style>
    """

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
with st.container():
    st.markdown(
        """
<div class="dedication" style="text-align:center">
  <div style="font-weight:700;">صدقة جارية</div>
  <div style="margin-top:2px;">لأرواح</div>
  <div style="height:6px;"></div>
  <div>الشيخ الدكتور عبد الرحمن الناجي</div>
  <div>الشيخ عبد الحي البشير</div>
  <div>الدكتور عبد الباقي الناجي</div>
  <div>الباشمهندس عثمان عباس عبد العاطي</div>
  <div>البروفيسور مصطفى محمد الحاج</div>
  <div>الأستاذ عبد الرحمن أحمد عثمان</div>
  <div>الأخ بابكر محمد إبراهيم عيدروس</div>
</div>
""",
        unsafe_allow_html=True,
    )

# ---------- Single built-in recording ----------
src = data_url_for_audio(AUDIO_FILE)
if not src:
    st.warning("الملف الصوتي غير موجود: **audio/v1.ogg** — أضف الملف إلى المستودع ثم أعد النشر.")
    st.stop()

st.write("")
st.markdown("#### التسجيل: ملف واحد (OGG)")

# ---------- Repetition controls ----------
if "reps" not in st.session_state:
    st.session_state.reps = 100
cols = st.columns(6)
for i, n in enumerate([10, 100, 1000, 2000, 3000, 4000]):
    with cols[i]:
        if st.button(f"{n}", use_container_width=True, key=f"chip_{n}"):
            st.session_state.reps = n

reps = st.number_input("عدد مرات التكرار (يمكن تغييره يدويًا):", min_value=1, value=st.session_state.reps, step=1)
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
  <div class="small">المتبقي: <span id="loop-remaining">{loops}</span> / {loops}</div>
  <div style="margin-top:8px;">
    <audio id="{aud_id}" preload="auto" controls style="width:100%">
      <source src="{src}">
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
st.components.v1.html(html, height=160, scrolling=False)

st.markdown(
    "<div class='small' style='text-align:center;margin-top:18px;'>"
    "التسجيل مدمج ضمن المستودع (audio/v1.ogg) والخلفية (assets/bg.jpg). لا يمكن للمستخدمين تعديلهما."
    "</div>",
    unsafe_allow_html=True,
)
