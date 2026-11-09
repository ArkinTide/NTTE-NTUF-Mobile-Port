"""Save deterministic source-alpha comparison for Visual205 crown review."""
from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw

from generate_frontier_menu_art import LOCKED_SHAPE, ROOT, SOURCE, TEMPLATE, RESOURCE


def main():
    output = ROOT / 'review/visual205-qa'
    output.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((TEMPLATE / (RESOURCE + '.yy')).read_text('utf8'))
    native_root = ROOT / 'staging/project/sprites/sprLockedLoadoutCrown'
    native_metadata = json.loads((native_root / 'sprLockedLoadoutCrown.yy').read_text('utf8'))
    paths = [SOURCE, LOCKED_SHAPE,
             TEMPLATE / (metadata['frames'][1]['name'] + '.png'),
             native_root / (native_metadata['frames'][1]['name'] + '.png')]
    images = [Image.open(path).convert('RGBA') for path in paths]
    old = Image.new('RGBA', (32, 32), (40, 40, 40, 0))
    old.paste(Image.new('RGBA', images[0].size, (40, 40, 40, 255)), (4, 0))
    images.insert(2, old)
    labels = ['Upstream menu icon', 'Transparent Idle source', 'Previous locked frame',
              'Revised locked frame', 'Native locked reference']
    sheet = Image.new('RGB', (1000, 246), (32, 32, 40))
    draw = ImageDraw.Draw(sheet)
    entries = []
    for index, (label, image) in enumerate(zip(labels, images, strict=True)):
        draw.text((index * 200 + 9, 12), label, fill='white')
        for y in range(8):
            for x in range(8):
                shade = 92 if (x + y) % 2 else 128
                draw.rectangle((index * 200 + 36 + x * 16, 42 + y * 16,
                                index * 200 + 51 + x * 16, 57 + y * 16), fill=(shade,) * 3)
        expanded = image.resize((128, 128), Image.Resampling.NEAREST)
        sheet.paste(expanded, (index * 200 + 36, 42), expanded)
        opaque = sum(pixel[3] != 0 for pixel in image.getdata())
        draw.text((index * 200 + 9, 184), f'{image.width}x{image.height}; opaque {opaque}', fill='white')
        draw.text((index * 200 + 9, 205), f'alpha bounds {image.getchannel("A").getbbox()}', fill='white')
        entries.append({'label': label, 'size': list(image.size), 'opaque_pixels': opaque,
                        'alpha_bounds': image.getchannel('A').getbbox()})
    target = output / 'crown-source-comparison.png'
    sheet.save(target)
    report = {'image': str(target), 'evidence': entries,
              'sources': [{'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                          for path in paths],
              'derivation': 'Revised locked alpha is upstream transparent Idle enlarged nearest2x; RGB40 matches native locked crowns. No color masking.'}
    (output / 'crown-source-comparison.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
