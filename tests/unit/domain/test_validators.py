from domain.validators import validate_race_class
import pytest

def test_validate_race_class_success():
    """Test valid race/class combinations."""
    assert validate_race_class("Human", "Warrior") == True
    assert validate_race_class("Night Elf", "Druid") == True
    assert validate_race_class("Undead", "Warlock") == True

def test_validate_race_class_failure():
    """Test invalid race/class combinations."""
    with pytest.raises(ValueError):
        validate_race_class("Human", "Druid") # Humans can't be Druids in Classic
    
    with pytest.raises(ValueError):
        validate_race_class("Gnome", "Paladin") 

    with pytest.raises(ValueError):
        validate_race_class("Tauren", "Rogue")

def test_validate_race_class_case_insensitivity():
    """Test that validation ignores case."""
    assert validate_race_class("human", "warrior") == True
    assert validate_race_class("HUMAN", "WARRIOR") == True
