from django.test import TestCase
from pathlib import Path
import csv
from .models import Player, Level, PlayerLevel, Prize, LevelPrize
from .services import give_prize_to_player, export_player_data_csv


class PlayerLevelPrizeTests(TestCase):

    def setUp(self):
        # создаём игроков, уровни и призы
        self.p1 = Player.objects.create(player_id="p1")
        self.p2 = Player.objects.create(player_id="p2")
        self.l1 = Level.objects.create(title="Level 1", order=1)
        self.l2 = Level.objects.create(title="Level 2", order=2)
        self.pr1 = Prize.objects.create(title="Gold")
        self.pr2 = Prize.objects.create(title="Silver")

        PlayerLevel.objects.create(player=self.p1, level=self.l1, is_completed=True, completed="2025-09-22")
        PlayerLevel.objects.create(player=self.p2, level=self.l2, is_completed=False, completed="2025-09-22")
        LevelPrize.objects.create(level=self.l1, prize=self.pr1, received="2025-09-22")
        LevelPrize.objects.create(level=self.l2, prize=self.pr2, received="2025-09-22")

    def test_give_prize_once(self):
        # выдаём приз
        pl = PlayerLevel.objects.get(player=self.p1, level=self.l1)
        prize = give_prize_to_player(pl, self.pr1)
        self.assertIsNotNone(prize.received)

        # пробуем выдать снова — ничего нового не создаётся
        prize2 = give_prize_to_player(pl, self.pr1)
        self.assertEqual(prize.id, prize2.id)

    def test_export_csv(self):
        file_path = export_player_data_csv("test.csv")
        self.assertTrue(Path(file_path).exists())

        with open(file_path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))

        # проверяем заголовок
        self.assertEqual(rows[0], ["player_id", "level_title", "is_completed", "prizes"])
        # проверяем хотя бы одну строку данных
        data_rows = rows[1:]
        self.assertTrue(any("p1" in row for row in data_rows))
        self.assertTrue(any("Level 2" in row for row in data_rows))
