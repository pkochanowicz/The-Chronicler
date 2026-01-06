#Turtle WoW Talent tree notes

This document is to facilitate forming of Talent trees for our app, ones that will be reflected within data_schemas that all the functionalities concerning talents will have to adhear to.
Data we had problem auto-reading with beautifulsoupv4 were following fields: requires, required_by (parent, child schema), tier. Points in specific tree required can be basically counted as follows: points_in_tree_required is solely (tier-1)*5, hence there's no need to keep that data stored. I'm not sure if we should just perhaps keep one of requires/required_by properties, since they can also be logically deduced on single of the two values - you make the call please, here ill only include requires, in talent trees the relation is usually pictured as an arrow pointing from talent required_by heading to one that requires with the slightly pointy end. Keep in mind that talent needs to be maxed to unlocked required_by talent of his). Talent brief descriptions also might be an useful field under Talent data-type. Please, conpress this info, and take whatever you find helpful throughout project and keep it in proper files/cache/memory. Since i'm working manually i'll only fill the missed needed fields that were made placeholders, I wont mention correct ones (Level is not a sensible property for that data type I'm afraid). The links next to each tree name, present a link to Classic wow background of particular talent tree. I would like every tree to be pictured by proper background - and for every character talents configuring only total of 3 trees aviable for the given class would show up on any talent related actions). While preparing functionality, prepare a script that will check presence of all needed graphics on our discord server (After thinking a while - it would be wise to store them properly in our Google Sheets Database, please include links to graphics in there, make a on-app-launch script checking if all required images for all the functionalities are present in Google Sheets - if any empty field near some feature that's supposed to have graphics, throw a clear, informative warning that will be addressed and visible only to @Trailwarden(s). Make sure, once posted all the images lead to our #graphics-vault proper graphics, which are groupped in a very tidy and clean way there), for ex. (#graphics-vault -> talents -> warrior -> arms -> Improved Heroic Strike.ico/png/jpg.webp (choose format on your own and keep it consistent, please)) or (#graphics-vault-members -> <registering_char_name> -> ) Please,  with the use of The-Chronicler own discord mcp server, for its own purpose, post, in a proper, clean way on #graphics-vault and then properly linked in database proper object and then on discord message, which is to fit database schema - once Google Sheets already get optionally auto-formatted during first use). I will not supply link for each of those talents, but i'd like you to find them under [following talent-tree-sub-sites](https://talent-builder.haaxor1689.dev/c/1.18.1), please include each talent tree icon and background as well as each talent icon (look for those in html code and css - previously we used beautifulsoup - perhpas there's a more efficent way?) below I'll supply only backgrounds. I'm certain the talent tree backgrounds can be not only handy while crafting talent trees but also, once character has selected talents with talent calculator, he/she might get his character sheet adorned in favorite, most point invested talent tree background too. Necessarly add "Notes" long text field to talent-tree data-type. It is important that one Discord user can /register_character multiple characters + add talent_tree or use any IC guild functionality on their (characters, every single one separated, pointing at one user, one-user-to-many-characters) behalf - keep it in mind.:

##WARRIOR:

###ARMS: https://i.imgur.com/dG8sqvo.jpeg
####Tier1:
- Improved Heroic Strike
- Tactical Mastery
- Improved Rend (required_by -> Deep Wounds)

####Tier2:
- Improved Charge
- Deflection
- Improved Thunder Clap

####Tier3:
- Master Strike (required by -> Master of Arms)
- Improved Overpower
- Deep Wounds (required by -> Impale)

####Tier4:
- Two-Handed Weapon Specialization
- Impale

####Tier5:
- Master of Arms
- Sweeping Strikes (required_by -> Mortal Strike)
- Precision Cut (Required by Boundless Anger)
- Improved Disciplines

####Tier6:
- Improved Slam
- Boundless Anger


####Tier7:
- Mortal Strike

###FURY: https://i.imgur.com/zksnzOE.jpeg
####Tier1:
- Booming Voice
- Cruelty

####Tier2:
- Dual-Wield Specialization
- Unbridled Wrath

####Tier3:
- Improved Shouts
- Piercing Howl
- Blood Craze

####Tier4:
- Battlefield Mobility
- Enrage (required_by Blood Drinker)
- Improved Pummel

####Tier5:
- Improved Whirlwind
- Death Wish (required_by Flurry)
- Improved Execute

####Tier6:
- Improved Berserker Rage
- Flurry
- Blood Drinker

####Tier7:
- Bloodthirst

###PROTECTION: https://i.imgur.com/nBFGuoD.jpeg
####Tier1:
- Improved Bloodrage (required_by Last Stand)
- Shield Specialization
- Anticipation

####Tier2:
- Iron Will
- Toughness

####Tier3:
- Last Stand
- Improved Intervene
- Improved Taunt
- Improved Revange (required_by Reprisal)

####Tier4:
- Gag Order
- Improved Disarm
- Defiance

####Tier5:
- One-Handed Weapon Specialization
- Shieldslam (required_by Improved Shield slam, required_by Concussion Blow)
- Improved Shield Slam
- Reprisal

####Tier6:
- Improved Shield Wall
- Defensive Tactics

####Tier7:
- Concussion Blow

---
##PALADIN:

###HOLY: https://i.imgur.com/JP8Gl2N.jpeg
####Tier1:
- Divine Strength
- Divine Intellect

####Tier2:
- Holy Judgement
- Spiritual Focus
- Improved Seal Of Righteousness

####Tier3:
- Healing Light
- Sanctity Aura
- Improved Lay On Hands
- Unyielding Faith

####Tier4:
- Improved Concentration Aura
- Illumination
- Ironclad

####Tier5:
- Divine Favor
- Holy Shock (required_by Divine Favor, required_by Blessed Strikes, required_by Daybreak)

####Tier6:
- Holy Power
- Blessed Strikes

####Tier7:
- Daybreak

###PROTECTION: https://i.imgur.com/tXyypuW.jpeg
####Tier1:
- Improved Devotion Aura
- Redoubt (required_by Shield Specialization)

####Tier2:
- Precision
- Guardian's Favor
- Toughness

####Tier3:
- Improved Righteous Fury (required_by Righteous Defense)
- Blessing of Santuary
- Shield Specialization
- Anticipation

####Tier4:
- Improved Hand of Reckoning
- Improved Hammer of Justice

####Tier5:
- Righteous Defense
- Holy Shield (required_by Bulwark of the Righteous)
- Reckoning

####Tier6:
- Righteous Strikes

####Tier7:
- Bulwark of the Righteous

###RETRIBUTION: https://i.imgur.com/13blQWM.jpeg
####Tier1:
- Improved Blessings
- Benediction

####Tier2:
- Improved Judgement
- Improved Seal of The Crusader
- Deflection

####Tier3:
- Improved Retribution Aura
- Conviction (required_by Vengeance)
- Blessing of Kings
- Pursuit of Justice

####Tier4:
- Two-Handed Weapon Specialization
- Vindication

####Tier5:
- Eye for an Eye
- Vengeance
- Seal Of Command

####Tier6:
- Vengeful Strikes

####Tier7:
- Repentance

---
##HUNTER:

###BEAST MASTERY: https://i.imgur.com/9IDZKjk.jpeg
####Tier1:
- Swift Aspects
- Endurance Training

####Tier2:
- Improved Eyes Of The Beast
- Improved Primal Aspects
- Thick Hide
- Improved Revive Pet

####Tier3:
- Pathfinding
- Coordinated Assault
- Unleashed Fury

####Tier4:
- Bestial Discipline
- Improved Mend Pet
- Ferocity (required_by Frenzy)

####Tier5:
- Intimidation
- Kill Command (required_by Baited Shot)
- Bestial Precision

####Tier6:
- Spirit Bond
- Frenzy

####Tier7:
- Baited Shot

###MARKSMANSHIP: https://i.imgur.com/imOT6iL.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

###SURVIVAL: https://i.imgur.com/cehCppw.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:

####Tier7:
-
---
##ROGUE:

###ASSASSINATION: https://i.imgur.com/wdMMU0H.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

###COMBAT: https://i.imgur.com/YwK1PZa.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

###SUBTLETY: https://i.imgur.com/MCiw1vw.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-
---
##PRIEST:

###DISCIPLINE: https://i.imgur.com/jb539sB.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

###HOLY: https://i.imgur.com/Ff4JPx7.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

###SHADOW: https://i.imgur.com/WdvVXDq.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

---
##SHAMAN:

###ELEMENTAL: https://i.imgur.com/tZhxnJZ.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:



####Tier7:
-

###ENHANCEMENT: https://i.imgur.com/l5mMLXR.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:



####Tier7:
-

###RESTORAION: https://i.imgur.com/92yXUuM.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:



####Tier7:
-

---
##MAGE:

###ARCANE: https://i.imgur.com/jEEi4Sm.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:



####Tier7:
-

###FIRE: https://i.imgur.com/stbVfwD.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

###FROST:
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

---
##WARLOCK:

###AFFLICTION: https://i.imgur.com/95rcgS7.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

###DEMONOLOGY: https://i.imgur.com/ntFjD9G.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

###DESTRUCITON: https://i.imgur.com/S8X1OtI.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

---
##DRUID:

###BALANCE: https://i.imgur.com/Ob3ScSl.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:


####Tier7:
-

###FERAL COMBAT: https://i.imgur.com/TQZ5NPN.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:



####Tier7:
-

###RESTORATION: https://i.imgur.com/ElJPrb1.jpeg
####Tier1:



####Tier2:




####Tier3:




####Tier4:




####Tier5:




####Tier6:



####Tier7:
-
---

While implementing the solution, make sure to populate currently existed, automatically red with beautiful soup data on Turtle WoW talents, where those fields remained placeholders, then, proper docs/*.md - especially architecture_UI_UX.md, TECHNICAL.MD, TEST-SUITE.md and anything related to functions using talents, Google Sheets shape as well as data related to talents validation.
