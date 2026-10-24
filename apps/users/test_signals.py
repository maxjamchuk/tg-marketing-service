from django.test import TestCase

from apps.parser.models import ChannelModerator, TelegramChannel
from apps.users.models import User
from apps.users.roles import UserRoleHistory


class AssignRoleModeratorChannelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="channel_owner",
            email="owner@example.com",
            password="secret123",
            role="user",
        )
        self.channel = TelegramChannel.objects.create(
            channel_id=987654321,
            title="Тестовый канал",
        )

    def test_owner_receives_channel_moderator_role(self) -> None:
        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, "channel_moderator")
        self.assertTrue(
            UserRoleHistory.objects.filter(
                user=self.user,
                role__code="channel_moderator",
                end_date__isnull=True,
            ).exists()
        )

    def test_regular_moderator_does_not_receive_owner_role(self) -> None:
        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=False,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, "user")
        self.assertFalse(
            UserRoleHistory.objects.filter(
                user=self.user,
                role__code="channel_moderator",
            ).exists()
        )

    def test_partner_keeps_partner_role(self) -> None:
        self.user.role = "partner"
        self.user.save(update_fields=["role"])

        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, "partner")
