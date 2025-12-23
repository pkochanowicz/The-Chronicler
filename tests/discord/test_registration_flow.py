import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from flows.registration_flow import RegistrationFlow
from models.pydantic_models import CharacterCreate
from schemas.db_schemas import CharacterRaceEnum, CharacterClassEnum, CharacterRoleEnum

@pytest.mark.asyncio
async def test_registration_finalize_success(mock_interaction, async_session):
    # Setup
    flow = RegistrationFlow(mock_interaction)
    flow.user = mock_interaction.user
    
    # Pre-construct the valid model as step_preview would
    char_create = CharacterCreate(
        discord_user_id=123456789,
        discord_username="TestUser",
        name="TestChar",
        race=CharacterRaceEnum.Human,
        class_name=CharacterClassEnum.Warrior,
        roles=[CharacterRoleEnum.Tank, CharacterRoleEnum.DPS],
        professions=["Mining", "Blacksmithing"],
        backstory="A long story...",
        personality="Gruff",
        quotes="For the King!",
        portrait_url="http://img.url",
        trait_1="Brave",
        trait_2="Strong",
        trait_3="Loyal",
        request_sdxl=False
    )
    
    flow.data = {
        "confirmed": True,
        "valid_model": char_create,
        "preview_embeds": [] # simplified
    }
    
    # Mocking external dependencies
    with patch("flows.registration_flow.get_engine_and_session_maker") as mock_get_engine:
        # Mock session maker to return our async_session fixture
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = async_session
        mock_get_engine.return_value = (None, mock_session_maker)
        
        with patch("flows.registration_flow.handle_post_to_recruitment", new_callable=AsyncMock) as mock_post_recruitment:
            # Execute
            await flow.finalize()
            
            # Verify DB insertion
            from services.character_service import CharacterService
            service = CharacterService(async_session)
            char = await service.get_character_by_discord_id(123456789)
            
            assert char is not None
            assert char.name == "TestChar"
            assert char.race == CharacterRaceEnum.Human
            assert char.class_name == CharacterClassEnum.Warrior
            
            # Verify Webhook/Thread creation trigger
            mock_post_recruitment.assert_called_once()