# 🔴 FSOCIETY RANSOMWARE SIMULATION

> 
> 
> ⚠️ **FOR EDUCATIONAL / VM USE ONLY — DO NOT RUN ON REAL MACHINES** ⚠️

---

## 📖 Overview

**Fsociety Ransomware Simulation** is a Python-based ransomware simulator designed for:
- 🎬 **Film / Video Production** — realistic hacking scenes
- 🎓 **Cybersecurity Education** — demonstrating how ransomware works
- 🧪 **Penetration Testing Training** — in isolated lab environments
- 🔬 **Security Research** — analyzing ransomware behavior

The tool displays a full-screen "locked" UI with a countdown timer, and if the correct password isn't entered before time runs out, it encrypts all user files using AES-128 (via Fernet).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **Full-Screen Lock UI** | Borderless, always-on-top window that blocks Alt+F4, Escape, and Alt keys |
| ⏱️ **60-Minute Countdown** | Real-time countdown displayed as `HH:MM:SS` |
| 🔐 **Masked Password Input** | Password shown as `•` characters |
| ❌ **5-Attempt Lockout** | After 5 wrong attempts → **`BYE BYE !`** + immediate encryption |
| 🔒 **AES-128 Encryption** | All user files encrypted via `Fernet` (AES-128-CBC + HMAC-SHA256) |
| 📁 **File Renaming** | Encrypted files renamed with `.fsociety` extension |
| 🔑 **Key Backup** | Encryption key saved to Desktop for recovery |
| 🎨 **Fsociety Branding** | Custom logo + "WE ARE FSOCIETY" theme |
| 🛡️ **Admin Privileges** | Requires UAC elevation for full access |
| 💥 **Window Shake Effect** | Shakes on wrong password attempts |

---


