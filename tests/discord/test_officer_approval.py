import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from views.officer_view import OfficerControlView
from schemas.db_schemas import CharacterStatusEnum


@pytest.fixture
def mock_settings():
    mock = MagicMock()
    mock.OFFICER_ROLE_IDS = [999, 888]
    mock.CHARACTER_SHEET_VAULT_CHANNEL_ID = 12345
    return mock


@pytest.mark.asyncio
async def test_approve_button_permission_denied(mock_interaction, mock_settings):
    # Setup: User does not have officer role
    mock_interaction.user.roles = [MagicMock(id=111)]  # Non-officer role

    view = OfficerControlView(bot=AsyncMock(), character_id=1)
    view.settings = mock_settings

    # Action: Call LOGIC method directly
    await view.approve_logic(mock_interaction)

    # Assert: Permission denied message
    mock_interaction.response.send_message.assert_called_with(
        "❌ Only officers can perform this action.", ephemeral=True
    )


@pytest.mark.asyncio
async def test_approve_button_success(mock_interaction, mock_settings, async_session):
    # Setup: User has officer role
    mock_interaction.user.roles = [MagicMock(id=999)]  # Officer role
    mock_interaction.channel.name = "[PENDING] Thorgar"
    mock_interaction.message = MagicMock()
    mock_interaction.message.edit = AsyncMock()

    # Mock DB service interaction
    with patch("views.officer_view.get_engine_and_session_maker") as mock_get_engine:
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = async_session
        mock_get_engine.return_value = (None, mock_session_maker)

        # We need a character in DB to approve
        from services.character_service import CharacterService
        from models.pydantic_models import CharacterCreate
        from schemas.db_schemas import CharacterRaceEnum, CharacterClassEnum

        service = CharacterService(async_session)
        char = await service.create_character(
            CharacterCreate(
                discord_user_id=123,
                discord_username="Applicant",
                name="Thorgar",
                race=CharacterRaceEnum.Orc,
                class_name=CharacterClassEnum.Warrior,
                backstory="...",
                trait_1="A",
                trait_2="B",
                trait_3="C",
            )
        )

        # Mock Bot
        mock_bot = MagicMock()  # Bot itself is synchronous container of methods
        mock_bot.get_channel = MagicMock()  # get_channel is sync
        mock_bot.fetch_channel = AsyncMock()  # fetch_channel is async

        view = OfficerControlView(bot=mock_bot, character_id=char.id)
        view.settings = mock_settings

        # Mock Discord Channel/Thread operations
        mock_vault_channel = AsyncMock()  # Channel actions are async
        mock_bot.get_channel.return_value = mock_vault_channel

        # Setup create_thread return value
        mock_thread_obj = MagicMock()
        mock_thread_obj.id = 99999
        mock_thread_obj.jump_url = "http://thread.url"

        mock_thread_message = MagicMock()
        mock_thread_message.thread = mock_thread_obj

        mock_vault_channel.create_thread.return_value = mock_thread_message

        # Action: Call LOGIC method directly
        await view.approve_logic(mock_interaction)

        # Assertions
        # 1. DB Status updated
        updated_char = await service.get_character_by_id(char.id)
        assert updated_char.status == CharacterStatusEnum.REGISTERED

        # 2. Vault Thread Created
        mock_vault_channel.create_thread.assert_called_once()

        # 3. Recruitment Thread Archived
        mock_interaction.channel.edit.assert_called_with(
            locked=True, archived=True, name="[APPROVED] Thorgar"
        )
