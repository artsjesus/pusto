from django.test import TestCase
from django.utils.timezone import now, timedelta
from .models import Player, Boost, PlayerBoost


class PlayerModelTest(TestCase):

    def test_first_login_sets_first_login_at(self):
        """Первый вход устанавливает first_login_at и начисляет очки"""
        player = Player.objects.create(username="ivan")
        self.assertIsNone(player.first_login_at)
        self.assertEqual(player.points, 0)

        player.login()
        self.assertIsNotNone(player.first_login_at)
        self.assertEqual(player.last_login_at, player.first_login_at)
        self.assertEqual(player.points, 1)

    def test_multiple_logins_same_day(self):
        """Баллы начисляются только один раз в день"""
        player = Player.objects.create(username="olga")

        # первый вход
        player.login()
        self.assertEqual(player.points, 1)
        first_login = player.first_login_at

        # ещё один вход в тот же день
        player.login()
        self.assertEqual(player.points, 1)  # баллы не увеличились
        self.assertEqual(player.first_login_at, first_login)  # первый вход не изменился

        # вход на следующий день
        player.last_login_at -= timedelta(days=1)
        player.login()
        self.assertEqual(player.points, 2)  # баллы начислены снова


class PlayerBoostTest(TestCase):
    def test_assign_boost(self):
        """Проверка выдачи буста игроку"""
        player = Player.objects.create(username="max")
        boost = Boost.objects.create(boost_type="speed", title="Ускорение", duration_days=3)

        pb = PlayerBoost.objects.create(player=player, boost=boost, given_manually=True)
        self.assertEqual(pb.player, player)
        self.assertEqual(pb.boost, boost)
        self.assertTrue(pb.is_active())

        # Проверка связи через игрока
        self.assertIn(pb, player.boosts.all())

    def test_boost_expiry(self):
        """Проверка просроченного буста"""
        player = Player.objects.create(username="lena")
        boost = Boost.objects.create(boost_type="double_points", title="Удвоение очков", duration_days=1)
        pb = PlayerBoost.objects.create(player=player, boost=boost, expires_at=now() - timedelta(days=1))
        self.assertFalse(pb.is_active())
