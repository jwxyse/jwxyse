"""벨로그 RSS에서 최신 글을 가져와 README.md의 Recent Posts 영역을 갱신합니다."""
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import timedelta, timezone

VELOG_ID = "jwxyse"
RSS_URL = f"https://v2.velog.io/rss/@{VELOG_ID}"
MAX_POSTS = 5
README = "README.md"
START = "<!-- VELOG-POST-LIST:START -->"
END = "<!-- VELOG-POST-LIST:END -->"
KST = timezone(timedelta(hours=9))

req = urllib.request.Request(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as res:
    root = ET.fromstring(res.read())

lines = []
for item in root.iter("item"):
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    pub = item.findtext("pubDate")
    date = parsedate_to_datetime(pub).astimezone(KST).strftime("%Y.%m.%d") if pub else ""
    title = title.replace("[", "\\[").replace("]", "\\]")
    lines.append(f"- `{date}` [{title}]({link})")
    if len(lines) >= MAX_POSTS:
        break

if not lines:
    raise SystemExit("RSS에서 글을 찾지 못했어요.")

with open(README, encoding="utf-8") as f:
    readme = f.read()

new_block = f"{START}\n" + "\n".join(lines) + f"\n{END}"
updated = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: new_block, readme, flags=re.S)

if updated != readme:
    with open(README, "w", encoding="utf-8") as f:
        f.write(updated)
    print("README 업데이트 완료")
else:
    print("변경 사항 없음")
