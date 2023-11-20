import synapse
from synapse.api.constants import EventTypes, RoomEncryptionAlgorithms
from synapse.handlers.room_list import _matches_room_entry
from synapse.rest.client import login, room

from tests import unittest
from tests.unittest import override_config


class EncryptedByDefaultTestCase(unittest.HomeserverTestCase):
    servlets = [
        login.register_servlets,
        synapse.rest.admin.register_servlets_for_client_rest_resource,
        room.register_servlets,
    ]

    @override_config({"encryption_enabled_by_default_for_room_type": "all"})
    def test_encrypted_by_default_config_option_all(self) -> None:
        """Tests that invite-only and non-invite-only rooms have encryption enabled by
        default when the config option encryption_enabled_by_default_for_room_type is "all".
        """
        # Create a user
        user = self.register_user("user", "pass")
        user_token = self.login(user, "pass")

        # Create an invite-only room as that user
        room_id = self.helper.create_room_as(user, is_public=False, tok=user_token)

        # Check that the room has an encryption state event
        event_content = self.helper.get_state(
            room_id=room_id,
            event_type=EventTypes.RoomEncryption,
            tok=user_token,
        )
        self.assertEqual(event_content, {"algorithm": RoomEncryptionAlgorithms.DEFAULT})

        # Create a non invite-only room as that user
        room_id = self.helper.create_room_as(user, is_public=True, tok=user_token)

        # Check that the room has an encryption state event
        event_content = self.helper.get_state(
            room_id=room_id,
            event_type=EventTypes.RoomEncryption,
            tok=user_token,
        )
        self.assertEqual(event_content, {"algorithm": RoomEncryptionAlgorithms.DEFAULT})

    @override_config({"encryption_enabled_by_default_for_room_type": "invite"})
    def test_encrypted_by_default_config_option_invite(self) -> None:
        """Tests that only new, invite-only rooms have encryption enabled by default when
        the config option encryption_enabled_by_default_for_room_type is "invite".
        """
        # Create a user
        user = self.register_user("user", "pass")
        user_token = self.login(user, "pass")

        # Create an invite-only room as that user
        room_id = self.helper.create_room_as(user, is_public=False, tok=user_token)

        # Check that the room has an encryption state event
        event_content = self.helper.get_state(
            room_id=room_id,
            event_type=EventTypes.RoomEncryption,
            tok=user_token,
        )
        self.assertEqual(event_content, {"algorithm": RoomEncryptionAlgorithms.DEFAULT})

        # Create a non invite-only room as that user
        room_id = self.helper.create_room_as(user, is_public=True, tok=user_token)

        # Check that the room does not have an encryption state event
        self.helper.get_state(
            room_id=room_id,
            event_type=EventTypes.RoomEncryption,
            tok=user_token,
            expect_code=404,
        )

    @override_config({"encryption_enabled_by_default_for_room_type": "off"})
    def test_encrypted_by_default_config_option_off(self) -> None:
        """Tests that neither new invite-only nor non-invite-only rooms have encryption
        enabled by default when the config option
        encryption_enabled_by_default_for_room_type is "off".
        """
        # Create a user
        user = self.register_user("user", "pass")
        user_token = self.login(user, "pass")

        # Create an invite-only room as that user
        room_id = self.helper.create_room_as(user, is_public=False, tok=user_token)

        # Check that the room does not have an encryption state event
        self.helper.get_state(
            room_id=room_id,
            event_type=EventTypes.RoomEncryption,
            tok=user_token,
            expect_code=404,
        )

        # Create a non invite-only room as that user
        room_id = self.helper.create_room_as(user, is_public=True, tok=user_token)

        # Check that the room does not have an encryption state event
        self.helper.get_state(
            room_id=room_id,
            event_type=EventTypes.RoomEncryption,
            tok=user_token,
            expect_code=404,
        )

class RoomListTestCase(unittest.TestCase):
    def test_matches_room_entry_generic_search_term_name(self):
        room_entry = {"name": "Test Room", "topic": "Discussion", "canonical_alias": "#test:example.com"}
        search_filter = {"generic_search_term": "Test"}

        result = _matches_room_entry(room_entry, search_filter)

        self.assertTrue(result)

    def test_matches_room_entry_generic_search_term_topic(self):
        room_entry = {"name": "Test Room", "topic": "Discussion", "canonical_alias": "#test:example.com"}
        search_filter = {"generic_search_term": "Discussion"}

        result = _matches_room_entry(room_entry, search_filter)

        self.assertTrue(result)

    def test_matches_room_entry_generic_search_term_canonical_alias(self):
        room_entry = {"name": "Test Room", "topic": "Discussion", "canonical_alias": "#test:example.com"}
        search_filter = {"generic_search_term": "#test:example.com"}

        result = _matches_room_entry(room_entry, search_filter)

        self.assertTrue(result)

    def test_matches_room_entry_no_generic_search_term(self):
        room_entry = {"name": "Test Room", "topic": "Discussion", "canonical_alias": "#test:example.com"}
        search_filter = {}

        result = _matches_room_entry(room_entry, search_filter)

        self.assertTrue(result)

    def test_does_not_match_room_entry_with_generic_search_term(self):
        room_entry = {"name": "Test Room", "topic": "Discussion", "canonical_alias": "#test:example.com"}
        search_filter = {"generic_search_term": "Nonexistent"}

        result = _matches_room_entry(room_entry, search_filter)

        self.assertFalse(result)