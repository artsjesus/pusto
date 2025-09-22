from datetime import date
from .models import PlayerLevel, LevelPrize, Prize
import csv
from pathlib import Path


def give_prize_to_player(player_level: PlayerLevel, prize: Prize):
    """
    Выдаёт игроку приз за прохождение уровня.
    Если уже получен — ничего не делает.
    """
    level = player_level.level
    lp, created = LevelPrize.objects.get_or_create(
        level=level,
        prize=prize,
        defaults={"received": date.today()}
    )
    if not created and lp.received is None:
        lp.received = date.today()
        lp.save()
    return lp


def export_player_data_csv(file_name="player_data.csv"):
    """
    Экспорт данных:
    player_id, level_title, is_completed, prizes
    """
    base_dir = Path(__file__).resolve().parent.parent
    export_dir = base_dir / "exports"
    export_dir.mkdir(exist_ok=True)

    file_path = export_dir / file_name
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["player_id", "level_title", "is_completed", "prizes"])

        for pl in PlayerLevel.objects.select_related("player", "level").iterator():
            prizes_qs = LevelPrize.objects.filter(level=pl.level)
            prizes_titles = [prize.prize.title for prize in prizes_qs]
            prizes_str = ", ".join(prizes_titles)

            writer.writerow([pl.player.player_id, pl.level.title, pl.is_completed, prizes_str])

    return file_path
