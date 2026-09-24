#!/usr/bin/env python3
"""Réencode en webp les images lourdes réellement utilisées par le site.

Idempotent : relançable sans risque (les images déjà optimisées sont ignorées).
Met aussi à jour les références dans les templates.

Principe : aucune image n'est servie à plus de 2x sa taille d'affichage réelle
dans le template qui l'utilise, et le webp n'est conservé que s'il est plus
léger que l'original.

Usage :  python scripts/optimize_images.py [--dry-run]
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'medeo/static/images')
TEMPLATES = os.path.join(ROOT, 'medeo/templates')

# (chemin relatif à static/images, largeur max, hauteur max, justification)
TARGETS = [
    # carousel_founders.html les affiche en w-72 h-72 = 288x288 px, rognées en
    # cercle. 576 couvre les écrans 2x ; au-delà chaque pixel est jeté.
    ('israel_haikou.jpg', 576, 576, 'photo fondateur affichée en 288px'),
    ('avi_gozlane.webp', 576, 576, 'photo fondateur affichée en 288px'),
    # Vignettes d'actualités : déjà au bon ratio, mais en JPEG peu compressé.
    ('news/fiscal/news_1112.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/fiscal/news_1200.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/fiscal/news_1212.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/fiscal/news_1234.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/fiscal/news_4322.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/fiscal/news_5555.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/fiscal/news_787.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/juridique/eiffel_tower.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/juridique/juridique_one.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/social/news_1.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/social/news_2.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/social/news_3.jpeg', 1200, 1200, "vignette d'actualité"),
    ('news/social/news_4.jpeg', 1200, 1200, "vignette d'actualité"),
]

# Images volumineuses référencées NULLE PART (vérifié sur tout le dépôt) :
# 26 Mo de poids mort embarqués dans chaque déploiement.
UNUSED = [
    'successful-business-team-expressing-unity.jpg',
    'startup-business.jpg',
]


def kb(path):
    return os.path.getsize(path) // 1024


def convert(src, out, width, height, square):
    args = ['magick', src]
    if square:
        args += ['-resize', f'{width}x{height}^', '-gravity', 'center',
                 '-extent', f'{width}x{height}']
    else:
        args += ['-resize', f'{width}x{height}>']
    args += ['-strip', '-quality', '82', out]
    subprocess.run(args, check=True)


def main():
    dry = '--dry-run' in sys.argv
    saved = 0
    renames = {}

    print('== Réencodage des images utilisées ==')
    for rel, w, h, why in TARGETS:
        src = os.path.join(IMG, rel)
        if not os.path.exists(src):
            print(f'  (absent, ignoré) {rel}')
            continue
        out_rel = os.path.splitext(rel)[0] + '.webp'
        out = os.path.join(IMG, out_rel)
        tmp = out + '.tmp'
        before = kb(src)
        convert(src, tmp, w, h, square=(w == h))
        after = kb(tmp)
        if after >= before:
            # Le webp n'apporte rien : on garde l'original tel quel.
            os.remove(tmp)
            print(f'  = {rel:<42} {before:>5} KB (déjà optimal, inchangé)')
            continue
        if dry:
            os.remove(tmp)
        else:
            os.replace(tmp, out)
            if os.path.abspath(src) != os.path.abspath(out):
                os.remove(src)
                renames[f'images/{rel}'] = f'images/{out_rel}'
        saved += before - after
        pct = 100 * (before - after) // before
        print(f'  ✓ {rel:<42} {before:>5} KB -> {after:>4} KB  (-{pct}%)  [{why}]')

    print('\n== Suppression des images non référencées ==')
    for rel in UNUSED:
        path = os.path.join(IMG, rel)
        if not os.path.exists(path):
            continue
        size = kb(path)
        saved += size
        print(f'  ✗ {rel:<42} {size:>5} KB supprimée (référencée nulle part)')
        if not dry:
            os.remove(path)

    if renames and not dry:
        print('\n== Mise à jour des références dans les templates ==')
        count = 0
        for dirpath, _dirs, files in os.walk(TEMPLATES):
            for name in files:
                if not name.endswith('.html'):
                    continue
                path = os.path.join(dirpath, name)
                with open(path, encoding='utf-8') as fh:
                    content = original = fh.read()
                for old, new in renames.items():
                    content = content.replace(old, new)
                if content != original:
                    with open(path, 'w', encoding='utf-8') as fh:
                        fh.write(content)
                    count += 1
                    print(f'  ✓ {os.path.relpath(path, ROOT)}')
        print(f'  {count} template(s) mis à jour')

    print(f"\nTotal économisé : {saved // 1024} Mo ({saved} KB)"
          + (' [DRY RUN, rien écrit]' if dry else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
