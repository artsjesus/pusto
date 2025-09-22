from django.db import models
from django.utils.timezone import now, localtime


NULLABLE = {"blank": True, "null": True}


class Player(models.Model):
    username = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    first_login_at = models.DateTimeField(**NULLABLE)
    last_login_at = models.DateTimeField(**NULLABLE)
    points = models.PositiveIntegerField(default=0)

    def login(self):
        """Фиксация входа игрока и начисление баллов."""
        today = localtime(now()).date()
        if not self.first_login_at:
            self.first_login_at = now()
        if not self.last_login_at or localtime(self.last_login_at).date() < today:
            self.points += 1
        self.last_login_at = now()
        self.save()

    def __str__(self):
        return self.username


class Boost(models.Model):
    BOOST_TYPES = (
        ("double_points", "Удвоением очков"),
        ("speed", "Ускорение"),
        ("shield", "Щит"),
    )

    boost_type = models.CharField(max_length=50, choices=BOOST_TYPES)
    title = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class PlayerBoost(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="boosts")
    boost = models.ForeignKey(Boost, on_delete=models.CASCADE)
    given_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(**NULLABLE)
    given_manually = models.BooleanField(default=False)

    def is_active(self):
        return not self.expires_at or self.expires_at > now()

    def __str__(self):
        return f"{self.player.username} - {self.boost.title}"
