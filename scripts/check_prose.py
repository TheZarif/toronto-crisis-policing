#### Preamble ####
# Purpose: Flags words and phrases that the paper's style guide prohibits.
#   Checks prose only (code chunks are skipped). Exits non-zero if any are found.
# Author: Zarif Masud
# Date: 7 October 2026
# Contact: zarif.masud@gmail.com
# License: MIT
# Pre-requisites: None; run from repo root.


#### Workspace setup ####
import re
import sys
from pathlib import Path

PAPER = Path("paper/paper.qmd")

# Words that tend to signal filler, hype or overstatement in academic prose.
PROHIBITED = [
    r"advanced", r"all-encompassing", r"apt", r"backdrop", r"beg the question", r"bridges? (the|a) gap",
    r"comprehensive", r"critical", r"crucial", r"data-driven", r"delves?", r"drastic", r"drives forward",
    r"elucidat(e|ing)", r"embarks?", r"exploration", r"fill (that|the|a) gap", r"fresh perspectives?",
    r"hidden factors?", r"imperative", r"insights? from", r"insights?", r"interrogate", r"intricate",
    r"intriguing", r"key insights", r"kind of", r"leverage", r"meticulous(ly)?", r"multifaceted", r"novel",
    r"nuance", r"offer(s|ing) crucial insight", r"plummeted", r"profound", r"rapidly", r"reveals",
    r"shed(s)? light", r"shocking", r"soared", r"unparalleled", r"unveiling", r"valuable", r"wanna",
]


#### Check prose ####
text = PAPER.read_text()
prose = re.sub(r"```\{python\}.*?```", "", text, flags=re.DOTALL)  # drop code chunks
prose = re.sub(r"`\{python\}[^`]*`", "", prose)  # drop inline code

hits = []
for line in prose.splitlines():
    for pattern in PROHIBITED:
        for match in re.finditer(rf"\b{pattern}\b", line, flags=re.IGNORECASE):
            hits.append(f"{PAPER}: '{match.group(0)}' in: {line.strip()[:100]}")

print("\n".join(hits) if hits else "No prohibited words found.")
sys.exit(1 if hits else 0)
