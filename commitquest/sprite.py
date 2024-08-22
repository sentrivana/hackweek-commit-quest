from pathlib import Path


def load_sprites(kind: str) -> list[str]:
    path = Path(f'static/images/{kind}').glob('*.png')
    return [sprite.name for sprite in path]


HERO_SPRITES = load_sprites('heroes')
BOSS_SPRITES = load_sprites('bosses')
LEVEL_BGS = load_sprites('bgs')

