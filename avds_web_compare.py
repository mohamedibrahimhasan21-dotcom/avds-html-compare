import streamlit as st
from bs4 import BeautifulSoup

# ---------------- LOGIN ----------------
def login():
    st.title("AVDS Status Comparison")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "Turbine" and password == "Turbine":
            st.session_state["authenticated"] = True
        else:
            st.error("Invalid username or password")

if "authenticated" not in st.session_state:
    login()
    st.stop()
# --------------------------------------


# ---------- PARSE HTML ----------
def parse_html(file):
    soup = BeautifulSoup(file, "lxml")
    devices = {}

    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        if {"AVDS NAME", "AVDS IP", "Status"}.issubset(headers):
            for row in table.find_all("tr")[1:]:
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cols) < 3:
                    continue

                name = cols[headers.index("AVDS NAME")].split()[0]
                ip = cols[headers.index("AVDS IP")]
                status = cols[headers.index("Status")]

                devices[ip] = {
                    "name": name,
                    "status": status
                }
            break

    return devices


# ---------- COMPARE ----------
def compare(old_file, new_file):
    old = parse_html(old_file)
    new = parse_html(new_file)

    went_online = []
    went_offline = []

    for ip, old_data in old.items():
        if ip not in new:
            continue

        if old_data["status"] == "Offline" and new[ip]["status"] == "Online":
            went_online.append((new[ip]["name"], ip))

        if old_data["status"] == "Online" and new[ip]["status"] == "Offline":
            went_offline.append((new[ip]["name"], ip))

    return went_online, went_offline


# ---------- UI ----------
st.set_page_config(page_title="AVDS Status Compare", layout="centered")

st.header("AVDS HTML Status Comparison")

old_file = st.file_uploader("Upload OLDER status HTML", type=["html"])
new_file = st.file_uploader("Upload NEWER status HTML", type=["html"])

if old_file and new_file:
    online, offline = compare(old_file, new_file)

    st.subheader("🟢 Went ONLINE")
    if online:
        for name, ip in online:
            st.success(f"{name} ({ip})")
    else:
        st.info("No devices went online")

    st.subheader("🔴 Went OFFLINE")
    if offline:
        for name, ip in offline:
            st.error(f"{name} ({ip})")
    else:
        st.info("No devices went offline")
