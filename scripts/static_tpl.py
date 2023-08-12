import glob
import re
import shutil
from pathlib import Path

from loguru import logger


def run():
    files = glob.glob('elegant/**/*.py', recursive=True)
    static = []

    for html in files:
        text = Path(html).read_text(encoding='utf-8')
        tags = re.findall(r"('[\w|/_\.]+\.html')", text)

        for tag in tags:
            tag and static.append((html, tag))
            tag and logger.info(f"{html} -> {tag}")

            dst = Path('static', tag)
            src = Path('elegant/static', tag)

            # src.exists() and dst.parent.mkdir(parents=True, exist_ok=True)
            # src.exists() and shutil.copy(src, dst)

            src.exists() and logger.info(f"src => {src}")
            src.exists() and logger.info(f"dst => {dst}")


if __name__ == '__main__':
    run()
