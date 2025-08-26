import subprocess
import re

def search_programmes(query, type_, channel):
    query = ".*" if not query.strip() else query.strip()
    channel = f"{channel.strip()}$" if channel.strip() else ""

    cmd = [
        r"C:\Program Files\get_iplayer\get_iplayer.cmd",
        f"--type={type_}",
        f"--channel={channel}",
        query
    ]

    print("Executing:", " ".join(cmd))

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout + result.stderr

    print("Full output:\n", output)

    programmes = []
    pattern = re.compile(r'^(\d+):\s+(.*?),\s+(BBC .+?),\s+([a-z0-9]{8})$', re.IGNORECASE)

    for line in output.splitlines():
        match = pattern.match(line.strip())
        if match:
            index, title, channel_name, pid = match.groups()
            programmes.append({
                "index": index,
                "pid": pid,
                "title": title
            })

    return programmes

def download_by_indexes(index_list):
    cmd = [r"C:\Program Files\get_iplayer\get_iplayer.cmd", "--get"] + index_list
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout + result.stderr
        if "No media streams found" in output or "Response: 410 Gone" in output:
            return "Download failed: Content not available in your region."
        return "Download complete!"
    except Exception as e:
        return f"Download error: {str(e)}"
