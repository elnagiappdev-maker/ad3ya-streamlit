
# أدعية صوتية – Streamlit (Single OGG + Background Photo)

A Streamlit web app with **one built-in OGG recording** and a **custom background photo**.  
Users can only **play** and **repeat**; **no uploads**.

## Repo layout
```
streamlit_app.py
requirements.txt
audio/
  v1.ogg          # ← your recording (≤ ~30s recommended)
assets/
  bg.jpg          # ← your photo (JPG or PNG)
```

> The folders include `.gitkeep` initially so Git tracks them; remove that after adding your files.

## How to use
1. Put your audio in `audio/v1.ogg` (exact name).
2. Put your background photo in `assets/bg.jpg` (or .png).
3. Commit & push to GitHub.
4. Deploy on Streamlit Cloud with **Main file** = `streamlit_app.py`.

## Local run
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
