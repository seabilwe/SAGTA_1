from flask import Flask, Response, abort, stream_with_context
import requests
import os, re

app = Flask(__name__)

DEFAULT_SCHEME = os.getenv("UPSTREAM_SCHEME", "https")

def flip_y(y: int, z: int) -> int:
    """XYZ → TMS row index."""
    return (1 << z) - 1 - y            # 2**z - 1 - y

@app.route("/proxy/<path:upstream>/<int:z>/<int:x>/<int:y>.png")
def tile(upstream: str, z: int, x: int, y: int):
    if min(z, x, y) < 0:
        abort(400)

    m = re.match(r"(?:(https?)://)?(.+)", upstream)
    if not m:
        abort(400)

    scheme = m.group(1) or DEFAULT_SCHEME
    host_and_path = m.group(2).rstrip("/")

    url = f"{scheme}://{host_and_path}/{z}/{x}/{flip_y(y, z)}.png"

    upstream_resp = requests.get(url, stream=True, timeout=10)
    if upstream_resp.status_code != 200:
        abort(upstream_resp.status_code)

    return Response(
        stream_with_context(upstream_resp.iter_content(8192)),
        content_type="image/png"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
