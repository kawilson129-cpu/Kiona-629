"""Disposable synthetic browser fixture, never a replacement business roster."""
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_secure_api import SecuredTests
from dev_demo import build_demo
from pulse import service
import uvicorn

fixture=SecuredTests()
fixture.setUp()
directory=tempfile.TemporaryDirectory(prefix="derexi-browser-fixture-")
source=Path(directory.name)/"synthetic.sqlite"
raw=fixture.fixture.engine.raw_connection()
with sqlite3.connect(source) as target:
    raw.driver_connection.backup(target)
raw.close()
app=build_demo(source,"http://127.0.0.1:8014")
# Network-free official-format payloads exercise the real normalizer/cache/UI.
payloads={"Federal Register":{"results":[{"title":"Synthetic capital final rule","html_url":"https://www.federalregister.gov/documents/synthetic",
    "publication_date":"2026-11-05","type":"Rule","abstract":"Synthetic browser verification only."}]},
    "NIST":{"entries":[]},"FDIC":ET.fromstring("<rss><channel/></rss>"),"Federal Reserve":ET.fromstring("<rss><channel/></rss>")}
service.fetch_source=lambda name:payloads[name]
metadata=Path(sys.argv[1])
metadata.write_text(json.dumps({"activation_key_path":str(app.state.activation_key_path),"base":"http://127.0.0.1:8014"}))
try:
    uvicorn.run(app,host="127.0.0.1",port=8014,proxy_headers=False,log_level="warning")
finally:
    app.state.local_engine.dispose()
    app.state.runtime.cleanup()
    fixture.tearDown()
    directory.cleanup()
