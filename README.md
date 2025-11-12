
# أدعية صوتية – Streamlit (Auto-audio + Dedications file)

- **Audios**: put any number of files into `audio/` (`.mp3`, `.wav`, `.ogg`, `.m4a`). The app discovers them automatically.
- **Uploads**: you (or users) can also upload multiple files at runtime (session-only).
- **Dedications**: edit `assets/dedications.txt` (UTF-8, one name per line). No code changes needed.
- **Background** (optional): add `assets/bg.jpg` (JPG/PNG).

## Layout
```
streamlit_app.py
requirements.txt
audio/
  .gitkeep
assets/
  .gitkeep
  dedications.txt   # one name per line; defaults pre-filled
  bg.jpg            # optional
```

## Local run
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
