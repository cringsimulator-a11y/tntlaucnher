import os
import json
import subprocess
import tkinter as tk
import minecraft_launcher_lib

mc_dir = os.path.join(os.getenv("APPDATA"), ".minecraft")
data_file = "launcher_data.json"

# ---------------- DATA ----------------
def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"username": "Player", "fabric_version": "none"}

def save_data():
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

data = load_data()

# ---------------- VERSION LISTS ----------------
def get_vanilla_versions():
    versions = []
    versions_dir = os.path.join(mc_dir, "versions")
    if not os.path.exists(versions_dir):
        return versions
    for v in os.listdir(versions_dir):
        if v[0].isdigit():
            json_path = os.path.join(versions_dir, v, f"{v}.json")
            if os.path.exists(json_path):
                versions.append(v)
    return sorted(versions, reverse=True)

def get_fabric_versions():
    versions = []
    versions_dir = os.path.join(mc_dir, "versions")
    if not os.path.exists(versions_dir):
        return versions
    for v in os.listdir(versions_dir):
        if v.startswith("fabric-loader"):
            json_path = os.path.join(versions_dir, v, f"{v}.json")
            if os.path.exists(json_path):
                versions.append(v)
    return sorted(versions, reverse=True)

# ---------------- LAUNCHERS ----------------
def launch_vanilla():
    username = username_entry.get().strip()
    version = version_var.get()
    if not username or not version:
        status_label.config(text="Select username and version")
        return

    data["username"] = username
    save_data()

    options = {
        "username": username,
        "uuid": "0",
        "token": "0",
        "launcherName": "TNT Launcher",
        "launcherVersion": "1.0"
    }

    try:
        cmd = minecraft_launcher_lib.command.get_minecraft_command(
            version,
            mc_dir,
            options
        )
        subprocess.Popen(cmd, cwd=mc_dir)
        status_label.config(text=f"Launching {version}...")
    except Exception as e:
        status_label.config(text=f"Launch failed: {e}")

def launch_fabric():
    save_data()

    fabric_file = "FabricLoaderLauncher.py"
    if not os.path.exists(fabric_file):
        status_label.config(text="FabricLoaderLauncher.py not found")
        return

    subprocess.Popen(
        ["python", fabric_file],
        cwd=os.path.dirname(os.path.abspath(fabric_file))
    )
    status_label.config(text=f"Running Fabric")


# ---------------- UI ----------------
root = tk.Tk()
root.title("Minecraft Launcher")
root.geometry("460x420")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

tk.Label(root, text="Minecraft Launcher", fg="white", bg="#1e1e1e",
         font=("Segoe UI", 18, "bold")).pack(pady=12)

username_entry = tk.Entry(root, font=("Segoe UI", 12), justify="center")
username_entry.insert(0, data["username"])
username_entry.pack(pady=6, ipadx=10, ipady=6)

# -------- VANILLA --------
tk.Label(root, text="Vanilla", fg="white", bg="#1e1e1e").pack(pady=(10, 0))
vanilla_versions = get_vanilla_versions()
version_var = tk.StringVar(value=vanilla_versions[0] if vanilla_versions else "")
tk.OptionMenu(root, version_var, *vanilla_versions).pack(pady=4)
tk.Button(root, text="PLAY VANILLA", bg="#3ba55d", fg="white", font=("Segoe UI", 12, "bold"),
          command=launch_vanilla).pack(pady=6, ipadx=20, ipady=6)

# -------- FABRIC --------
tk.Label(root, text="Fabric", fg="white", bg="#1e1e1e").pack(pady=(14, 0))
fabric_versions = get_fabric_versions()
initial_fabric_version = data.get("fabric_version", fabric_versions[0] if fabric_versions else "")
fabric_var = tk.StringVar(value=initial_fabric_version)

def on_fabric_select(value):
    data["fabric_version"] = value
    save_data()

fabric_menu = tk.OptionMenu(root, fabric_var, *fabric_versions, command=on_fabric_select)
fabric_menu.pack(pady=4)
tk.Button(root, text="PLAY FABRIC", bg="#5865f2", fg="white", font=("Segoe UI", 12, "bold"),
          command=launch_fabric).pack(pady=6, ipadx=22, ipady=6)

status_label = tk.Label(root, text="", fg="#aaaaaa", bg="#1e1e1e")
status_label.pack(pady=10)

root.mainloop()
