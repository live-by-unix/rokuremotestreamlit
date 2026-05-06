import streamlit as st
import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import urllib.parse
import time

st.set_page_config(page_title="ROKU CONTROLLER", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .stButton>button { border-radius: 8px; height: 3.5em; background: #1a1a1a; border: 1px solid #333; transition: 0.2s; }
    .stButton>button:hover { border-color: #bb86fc; background: #252525; box-shadow: 0 0 10px #6a1b9a; }
    .pwr-btn button { background-color: #4a0000 !important; border: 1px solid #ff4b4b !important; color: #ff4b4b !important; }
    .pwr-btn button:hover { background-color: #ff4b4b !important; color: white !important; }
    .app-card { background: #121212; padding: 15px; border-radius: 12px; border: 1px solid #222; text-align: center; margin-bottom: 10px; }
    .search-zone { background: #000b1a; padding: 20px; border-radius: 15px; border-left: 5px solid #00d2ff; margin-bottom: 20px; }
    .dev-zone { background: #1a001a; padding: 20px; border-radius: 15px; border-left: 5px solid #ff00ff; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🛰️ QUICK CONNECT")
    ip = st.text_input("ROKU IP", value="")
    st.divider()
    st.subheader("🔑 DEV AUTH")
    user = st.text_input("USERNAME", value="rokudev")
    pw = st.text_input("PASSWORD", type="password")
    
if not ip:
    st.warning("🔌 IP REQUIRED")
    st.stop()

ecp = f"http://{ip}:8060"
dev_root = f"http://{ip}"
auth = HTTPDigestAuth(user, pw)

def fire(path, prefix="keypress/"):
    try: requests.post(f"{ecp}/{prefix}{path}", timeout=0.8)
    except: pass

st.markdown('<div class="search-zone">', unsafe_allow_html=True)
st.subheader("🔍 SYSTEM QUERY ENGINE")
with st.form("query_form", clear_on_submit=True):
    kw = st.text_input("TYPE TO QUERY TV LIST (Movies, Apps, Actors)", placeholder="Netflix...")
    if st.form_submit_button("PUSH QUERY TO TV"):
        if kw:
            requests.post(f"{ecp}/search/browse?keyword={urllib.parse.quote_plus(kw)}&launch=true")
st.markdown('</div>', unsafe_allow_html=True)

t_remote, t_catalog, t_media, t_dev = st.tabs(["🎮 REMOTE", "📱 APP CATALOG", "🎬 MEDIA", "🚀 DEV"])

with t_remote:
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown('<div class="pwr-btn">', unsafe_allow_html=True)
        st.button("⏻ POWER", on_click=fire, args=("Power",))
        st.markdown('</div>', unsafe_allow_html=True)
    c2.button("🏠 HOME", on_click=fire, args=("Home",))
    c3.button("↩️ BACK", on_click=fire, args=("Back",))

    st.write("")
    _, up, _ = st.columns(3)
    up.button("▲", on_click=fire, args=("Up",))
    lt, ok, rt = st.columns(3)
    lt.button("◀", on_click=fire, args=("Left",))
    ok.button("OK", on_click=fire, args=("Select",))
    rt.button("▶", on_click=fire, args=("Right",))
    _, dn, _ = st.columns(3)
    dn.button("▼", on_click=fire, args=("Down",))

    st.write("")
    s1, s2, s3 = st.columns(3)
    s1.button("⏪", on_click=fire, args=("Rev",))
    s2.button("⏯️", on_click=fire, args=("Play",))
    s3.button("⏩", on_click=fire, args=("Fwd",))
    
    v1, v2, v3 = st.columns(3)
    v1.button("🔉 DOWN", on_click=fire, args=("VolumeDown",))
    v2.button("🔇 MUTE", on_click=fire, args=("Mute",))
    v3.button("🔊 UP", on_click=fire, args=("VolumeUp",))
    st.button("✱ OPTIONS (ASTERISK)", on_click=fire, args=("Info",), use_container_width=True)

with t_catalog:
    if st.button("🔄 SYNC APP CATALOG", use_container_width=True):
        try:
            r = requests.get(f"{ecp}/query/apps")
            root = ET.fromstring(r.content)
            st.session_state.app_db = [{"id": a.get('id'), "name": a.text} for a in root.findall('app')]
        except: st.error("OFFLINE")

    if 'app_db' in st.session_state:
        grid = st.columns(5)
        for i, app in enumerate(st.session_state.app_db):
            with grid[i % 5]:
                st.markdown('<div class="app-card">', unsafe_allow_html=True)
                st.image(f"{ecp}/query/icon/{app['id']}", width=70)
                st.caption(app['name'])
                if st.button("LAUNCH", key=f"run_{app['id']}"):
                    requests.post(f"{ecp}/launch/{app['id']}")
                st.markdown('</div>', unsafe_allow_html=True)

with t_media:
    m_url = st.text_input("URL (YouTube/Direct)")
    mc1, mc2 = st.columns(2)
    if mc1.button("🚀 BEAM", use_container_width=True):
        if "youtube" in m_url:
            v_id = m_url.split("v=")[1].split("&")[0] if "v=" in m_url else m_url.split("be/")[1]
            requests.post(f"{ecp}/launch/837?contentId={v_id}")
        else:
            enc = urllib.parse.quote_plus(m_url)
            requests.post(f"{ecp}/launch/551012?contentId={enc}&mediaType=movie&url={enc}")
    if mc2.button("⏹️ KILL", use_container_width=True):
        fire("Back"); time.sleep(0.3); fire("Home")
    
    st.divider()
    h1, h2 = st.columns(2)
    h1.button("💾 USB MODE", on_click=fire, args=("19042", "launch/"), use_container_width=True)
    h2.button("🌐 DLNA SCAN", on_click=fire, args=("19042?location=network", "launch/"), use_container_width=True)
    
    st.divider()
    st.subheader("📁 DRAG & DROP")
    st.file_uploader("DROP MEDIA", type=['mp4', 'mkv'])

with t_dev:
    st.markdown('<div class="dev-zone">', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    if d1.button("🔓 SECRET MENU"):
        for k in ["Home"]*3 + ["Up"]*2 + ["Right", "Left", "Right", "Left", "Right"]:
            fire(k); time.sleep(0.4)
    if d2.button("🔄 REBOOT"):
        for k in ["Home"]*5 + ["Up", "Rev", "Rev", "Fwd", "Fwd"]:
            fire(k); time.sleep(0.4)
    
    st.write("")
    bundle = st.file_uploader("SIDELOAD ZIP", type="zip")
    if st.button("📥 INSTALL BUNDLE"):
        if bundle and pw:
            f = {'archive': (bundle.name, bundle.getvalue(), 'application/zip')}
            requests.post(f"{dev_root}/plugin_install", auth=auth, files=f, data={'mysubmit': 'Install'})
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🔍 RAW XML QUERY"):
        r = requests.get(f"{ecp}/query/apps")
        st.code(r.text)