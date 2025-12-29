import os
import json
import subprocess
import platform
import zipfile

MC_DIR = os.path.expanduser("~/.minecraft") if not platform.system().startswith("Windows") else os.path.join(os.getenv("APPDATA"), ".minecraft")
JAVA_PATH = r"C:\Program Files\Eclipse Adoptium\jdk-21.0.9.10-hotspot\bin\java.exe"  # Change if needed

def get_version_json(version_id):
    path = os.path.join(MC_DIR, "versions", version_id, f"{version_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Version JSON not found: {path}")
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)

def build_classpath(version_data):
    cp = []
    for lib in version_data["libraries"]:
        if "natives" in lib:
            continue
        name = lib["name"]
        parts = name.split(":")
        if len(parts) != 3:
            continue
        group, artifact, ver = parts
        jar_path = os.path.join(MC_DIR, "libraries", *group.split("."), artifact, ver, f"{artifact}-{ver}.jar")
        if os.path.exists(jar_path):
            cp.append(jar_path)
    client_jar = os.path.join(MC_DIR, "versions", version_data["id"], f"{version_data['id']}.jar")
    cp.append(client_jar)
    return os.pathsep.join(cp)

def extract_natives(version_data, version_id):
    natives_path = os.path.join(MC_DIR, "versions", version_id, "natives")
    os.makedirs(natives_path, exist_ok=True)
    for lib in version_data["libraries"]:
        if "natives" not in lib:
            continue
        os_name_key = None
        if platform.system() == "Windows":
            os_name_key = "windows"
        elif platform.system() == "Linux":
            os_name_key = "linux"
        elif platform.system() == "Darwin":
            os_name_key = "osx"
        if os_name_key not in lib["natives"]:
            continue
        classifier = lib["natives"][os_name_key]
        parts = lib["name"].split(":")
        group, artifact, ver = parts
        jar_file = os.path.join(MC_DIR, "libraries", *group.split("."), artifact, ver, f"{artifact}-{ver}-{classifier}.jar")
        if os.path.exists(jar_file):
            with zipfile.ZipFile(jar_file, "r") as zip_ref:
                zip_ref.extractall(natives_path)
    return natives_path

def launch_vanilla(version_id, username="Player"):
    version_data = get_version_json(version_id)
    classpath = build_classpath(version_data)
    natives_path = extract_natives(version_data, version_id)
    main_class = version_data["mainClass"]
    cmd = [
        JAVA_PATH,
        "-Xmx2G",
        "-Xms1G",
        f"-Djava.library.path={natives_path}",
        "-cp", classpath,
        main_class,
        "--username", username,
        "--version", version_id,
        "--gameDir", MC_DIR,
        "--assetsDir", os.path.join(MC_DIR, "assets"),
        "--assetIndex", version_data.get("assetIndex", {}).get("id", version_id),
        "--uuid", "0000-0000-0000-0000"
    ]
    print("Running Vanilla command:", " ".join(cmd))
    subprocess.run(cmd)

def launch_fabric(fabric_version, mc_version, username):
    fabric_id = f"fabric-loader-{fabric_version}-{mc_version}"
    version_data = get_version_json(fabric_id)
    classpath = build_classpath(version_data)
    natives_path = extract_natives(version_data, fabric_id)
    main_class = version_data.get("mainClass", "net.fabricmc.loader.impl.launch.knot.KnotClient")
    cmd = [
        JAVA_PATH,
        "-Xmx2G",
        "-Xms1G",
        f"-Djava.library.path={natives_path}",
        "-cp", classpath,
        main_class,
        "--username", username,
        "--version", fabric_id,
        "--gameDir", MC_DIR,
        "--assetsDir", os.path.join(MC_DIR, "assets"),
        "--assetIndex", version_data.get("assetIndex", {}).get("id", mc_version),
        "--uuid", "0000-0000-0000-0000"
    ]
    print("Running Fabric command:", " ".join(cmd))
    subprocess.run(cmd)

# Example usage:
# launch_vanilla("1.21.1")

def launch_fabric_from_launcher_data():
    with open("launcher_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    fabric_id = data.get("fabric_version")
    username = data.get("username", "Player")

    if not fabric_id or not fabric_id.startswith("fabric-loader-"):
        raise RuntimeError("Invalid fabric_version in launcher_data.json")

    _, _, fabric_version, mc_version = fabric_id.split("-", 3)

    launch_fabric(fabric_version, mc_version, username)

launch_fabric_from_launcher_data()
