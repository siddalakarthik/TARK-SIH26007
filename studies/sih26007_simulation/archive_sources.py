"""One-time source capture from already-downloaded official files; no network."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('download_directory', type=Path)
    args = p.parse_args()
    out = Path(__file__).parent / 'sources'
    out.mkdir(exist_ok=True)
    source = args.download_directory / 'SIH2026PS.html'
    data = source.read_bytes()
    text = data.decode('utf-8')
    start = text.index('<div id="ViewProblemStatement26007"')
    end = text.index('</thead>', start) + len('</thead>')
    modal = text[start:end]
    modal = re.sub(r'<!--.*?-->', '', modal, flags=re.S)
    (out / 'SIH26007_official_modal.html').write_text(modal, encoding='utf-8', newline='\n')
    entries = [{'id': 'S1', 'url': 'https://sih.gov.in/sih2026PS',
                'file': 'SIH26007_official_modal.html', 'scope': 'modal ViewProblemStatement26007',
                'complete_page_sha256': hashlib.sha256(data).hexdigest()}]
    for sid, name, url in [
        ('S2', 'SIH2026-Guidelines.pdf', 'https://sih.gov.in/letters/2026/SIH%202026%20Guidelines.pdf'),
        ('S3', 'SIH2026-IDEA-Presentation-Format.pptx', 'https://sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx')]:
        shutil.copyfile(args.download_directory / name, out / name)
        entries.append({'id': sid, 'url': url, 'file': name, 'scope': 'complete official download'})
    for e in entries:
        e.update(retrieved_date='2026-09-29', authority='OFFICIAL_SIH', http_status=200,
                 sha256=hashlib.sha256((out/e['file']).read_bytes()).hexdigest())
    (out/'source_inventory.json').write_text(json.dumps(entries, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
