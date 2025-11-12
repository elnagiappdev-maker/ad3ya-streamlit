
import base64
import streamlit as st
import uuid

st.set_page_config(
    page_title="أدعية صوتية",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ARABIC_CSS = """
<style>
html, body, [class*="css"] {
  direction: rtl;
  text-align: right;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Naskh Arabic", "Noto Sans Arabic", "Droid Arabic Naskh", "Tahoma", Arial, sans-serif !important;
}
.block-container { padding-top: 1.25rem; }
.dedication { border: 1px solid #e6e6e6; border-radius: 16px; padding: 16px 18px; background: #fafafa; }
.small { font-size: 12px; color: #666; }
#audio-wrap { margin-top: 8px; }
</style>
"""
st.markdown(ARABIC_CSS, unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'>أدعية صوتية</h2>", unsafe_allow_html=True)
with st.container():
    st.markdown(
        """
<div class="dedication">
  <div style="text-align:center; font-weight:700;">صدقة جارية</div>
  <div style="text-align:center; margin-top:2px;">لأرواح</div>
  <div style="height:8px;"></div>
  <div style="text-align:center;">الشيخ الدكتور عبد الرحمن الناجي</div>
  <div style="text-align:center;">الشيخ عبد الحي البشير</div>
  <div style="text-align:center;">الدكتور عبد الباقي الناجي</div>
  <div style="text-align:center;">الباشمهندس عثمان عباس عبد العاطي</div>
  <div style="text-align:center;">البروفيسور مصطفى محمد الحاج</div>
  <div style="text-align:center;">الأستاذ عبد الرحمن أحمد عثمان</div>
  <div style="text-align:center;">الأخ بابكر محمد إبراهيم عيدروس</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.write("")
st.markdown("### ارفع التسجيلات الصوتية (حتى ٣ ملفات قصيرة)")
uploads = st.file_uploader(
    "ملفات MP3 / WAV / OGG / M4A (يفضّل ≤ 30 ثانية لكل ملف)",
    type=["mp3", "wav", "ogg", "m4a"],
    accept_multiple_files=True,
    key="uploader",
)

uploads = (uploads or [])[:3]

def file_to_data_url(file) -> str:
    raw = file.read()
    file.seek(0)
    mime = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "m4a": "audio/mp4",
    }.get(file.name.split(".")[-1].lower(), "audio/mpeg")
    import base64
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"

tracks = []
for i, f in enumerate(uploads):
    try:
        src = file_to_data_url(f)
        label = f"التسجيل {i+1} — {f.name}"
        tracks.append({"label": label, "src": src})
    except Exception:
        pass

if not tracks:
    st.info("📥 ارفع من ١ إلى ٣ تسجيلات قصيرة لبدء التشغيل.")
else:
    labels = [t["label"] for t in tracks]
    sel_label = st.selectbox("اختر التسجيل:", labels, index=0)
    current = next(t for t in tracks if t["label"] == sel_label)

    st.markdown("#### عدد مرات التكرار")
    presets = [10, 100, 1000, 2000, 3000, 4000, 5000, 6000]
    if "reps" not in st.session_state:
        st.session_state.reps = 100

    cols = st.columns(6)
    for idx, n in enumerate(presets):
        with cols[idx % 6]:
            if st.button(f"{n}", use_container_width=True, key=f"chip_{n}"):
                st.session_state.reps = n

    reps = st.number_input("أو أدخل رقمًا يدويًا:", min_value=1, value=st.session_state.reps, step=1)
    st.session_state.reps = reps

    c1, c2, c3 = st.columns([1, 1, 2])
    play_clicked = c1.button("▶ تشغيل", use_container_width=True)
    pause_clicked = c2.button("⏸ إيقاف مؤقت", use_container_width=True)
    restart_clicked = c3.button("⟲ من البداية", use_container_width=True)

    aud_id = f"aud_{uuid.uuid4().hex}"
    wrap_id = f"wrap_{uuid.uuid4().hex}"

    payload_src = current["src"]
    payload_loops = int(reps)
    autoplay = bool(play_clicked or restart_clicked)
    restart = bool(restart_clicked)
    pause = bool(pause_clicked)

    js = f"""
<div id="{wrap_id}">
  <div class="small">المتبقي: <span id="loop-remaining">{payload_loops}</span> / {payload_loops}</div>
  <div id="audio-wrap">
    <audio id="{aud_id}" preload="auto" controls style="width:100%">
      <source src="{payload_src}">
      متصفحك لا يدعم مشغل الصوت.
    </audio>
  </div>
</div>

<script>
(function() {{
  const audio = document.getElementById("{aud_id}");
  if (!audio) return;

  let total = {payload_loops};
  let remainingEl = document.getElementById("loop-remaining");
  if (remainingEl) remainingEl.textContent = String(total);

  const restartFlag = {str(restart).lower()};
  if (restartFlag) {{
    try {{ audio.currentTime = 0; }} catch(e) {{}}
    total = {payload_loops};
    if (remainingEl) remainingEl.textContent = String(total);
  }}

  const pauseFlag = {str(pause).lower()};
  if (pauseFlag) {{
    try {{ audio.pause(); }} catch(e) {{}}
  }}

  function onEnded() {{
    if (total > 1) {{
      total -= 1;
      if (remainingEl) remainingEl.textContent = String(total);
      try {{
        audio.currentTime = 0;
        audio.play().catch(() => {{}});
      }} catch(e) {{}}
    }} else {{
      try {{ audio.pause(); }} catch(e) {{}}
    }}
  }}

  audio.onended = null;
  audio.addEventListener("ended", onEnded, {{ once: false }});

  const auto = {str(autoplay).lower()};
  if (auto) {{
    total = {payload_loops};
    if (remainingEl) remainingEl.textContent = String(total);
    try {{
      audio.currentTime = 0;
      audio.play().catch(() => {{}});
    }} catch(e) {{}}
  }}
}})();
</script>
    """
    st.components.v1.html(js, height=140, scrolling=False)

st.markdown(
    "<div class='small' style='text-align:center;margin-top:18px;'>"
    "يعمل هذا التطبيق محليًا في متصفحك — لا يتم رفع ملفاتك إلى أي خادم."
    "</div>",
    unsafe_allow_html=True,
)
