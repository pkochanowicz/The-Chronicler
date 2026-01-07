# The Chronicler v1.3.0 - Guild Announcement Pack

## 📢 #guild-news Announcement

Copy this entire message and post it to your #guild-news channel:

---

```
@everyone

🏛️ **THE ARCHIVES ARE NOW OPEN** 🏛️

*The ancient halls echo with the sound of turning pages...*

Greetings, heroes of **Azeroth Bound**!

After months of preparation, the Guild Council is proud to announce the arrival of **The Chronicler** — an arcane construct designed to preserve our legends, manage our records, and honor our fallen.

**Meet Chronicler Thaldrin**, your guide through the registration ritual. He awaits those brave enough to inscribe their names in our archives.

---

## 🖋️ **Join Our Ranks: The Sacred Ritual**

Ready to officially join Azeroth Bound? The process is simple:

**1️⃣ Invoke the Ritual**
Type `/register_character` in any channel

**2️⃣ Answer the Call**
Chronicler Thaldrin will greet you in a private vision (only you can see it). Follow his 12-step guided journey to share:
- Your character's name, race, and class
- Your preferred roles (Tank/Healer/DPS)
- Your professions
- Your backstory
- Your portrait

**3️⃣ Await Officer Review**
Your application will appear in <#1452099464109228254> (📋 recruitment) as a new thread. Our officers (Pathfinders & Trailwardens) will review your submission.

**4️⃣ Welcome Home**
✅ **Approved?** Your character sheet will be immortalized in <#1448017278909157446> (📚 character-sheet-vault), and you'll receive a welcome DM.
❌ **Needs changes?** Officers may request edits or provide feedback.

---

## ⚰️ **For Hardcore Heroes: The Rite of Remembrance**

Death is part of the journey. When a hero falls, officers perform the **Burial Rite** (`/bury`), moving their legend to <#1450075549853548670> (⚰️ cemetery) where they will be honored forever.

---

## 🏦 **Additional Features**

The Chronicler does more than registration:
- **Guild Bank:** `/bank deposit`, `/bank view`, `/bank withdraw`
- **Talent Validation:** `/talent audit` (ensures your build is Classic+ legal)

Full documentation available in our pinned resources.

---

## 🎯 **Get Started Today**

Type `/register_character` right now and let Chronicler Thaldrin guide you through your initiation!

*For the Guild! For the Code! For Azeroth!*

— **The Guild Council**
```

---

## 📚 #character_sheet_vault Instructions Post

Post this as the **first pinned message** in #character_sheet_vault:

---

```
📚 **WELCOME TO THE CHARACTER SHEET VAULT** 📚

*A massive archive stretches before you, filled with glowing threads of approved characters...*

---

## 🛡️ **What is this channel?**

This is the **permanent archive** for all **approved characters** in Azeroth Bound. Each thread in this forum represents one officially recognized guild member.

Only characters that have passed officer review appear here. This is your guild roster — the living record of our heroes.

---

## 📋 **How do characters get here?**

1. A member uses `/register_character` to submit their application
2. The application appears in <#1452099464109228254> (recruitment) for review
3. An officer (Pathfinder/Trailwarden) clicks **Approve**
4. The Chronicler automatically creates a thread here with the character's full sheet
5. The recruitment thread is locked and archived

**You cannot post directly to this channel.** All entries are created by The Chronicler bot after officer approval.

---

## 🔍 **What's in each thread?**

Every character sheet includes:
- **Identity:** Name, Race, Class, Level
- **Roles:** Tank, Healer, DPS preferences
- **Professions:** Crafting specializations
- **Backstory:** The hero's tale
- **Portrait:** Character image
- **Discord Link:** Who plays this character

---

## 📖 **How to use this vault**

- **Browse:** Scroll through threads to see all active guild members
- **Search:** Use Discord's search to find specific characters
- **Reference:** Officers and members can view sheets anytime
- **Respect:** These are official records — treat them with care

---

## ❓ **Questions?**

- **Want to register?** Use `/register_character` in any channel
- **Need edits to your sheet?** Contact an officer (Pathfinder/Trailwarden)
- **Technical issues?** Ping <@381579719428276224> or a Trailwarden

---

*The Vault is maintained by Chronicler Thaldrin*
*Last Updated: 2026-01-06 | The Chronicler v1.3.0*
```

---

## 🎯 Additional Recommendations

### Before Launch Checklist

- [ ] **Test with 2-3 trusted members first** (have them run `/register_character`)
- [ ] **Brief officers** on the Approve/Reject/Request Edit buttons (they're simple, but walk through once)
- [ ] **Verify bot permissions** in all 3 forum channels (recruitment, vault, cemetery)
- [ ] **Pin both announcements** (guild-news and character-sheet-vault instructions)
- [ ] **Update server rules/welcome message** to mention `/register_character` as the official way to join

### Day 1 Monitoring

- [ ] **Watch first 5-10 registrations** closely for any unexpected issues
- [ ] **Have an officer online** during peak hours to approve quickly
- [ ] **Be ready to help** users who get stuck or confused
- [ ] **Celebrate!** Congratulate the first approved characters in chat

### Optional Enhancements

**Create a #bot-commands quick reference:**
```
🤖 **THE CHRONICLER - QUICK REFERENCE**

**For Everyone:**
`/register_character` - Join the guild (official registration)
`/bank view` - Check guild bank inventory
`/bank deposit <item> <qty>` - Donate items to bank
`/bank mydeposits` - See your contribution history
`/talent audit <character>` - Validate a talent build

**For Officers Only:**
`/bury` - Perform the Rite of Remembrance (for fallen heroes)

**Need Help?**
- Read <#1448017278909157446> for character sheet info
- Ask in #bot-commands for general questions
- Ping an officer for registration issues
```

**Update Server Welcome Channel (if you have one):**
Add a line like:
> "Once you're settled, use `/register_character` to officially join our guild ranks!"

**Consider a Role Requirement:**
If you want to gate `/register_character` behind a verification or "Prospect" role, update your `.env`:
```
WANDERER_ROLE_ID=<role_id>
```
Only users with that role will be able to register.

---

## 🎉 Launch Message Template

If you want to hype it up even more, post this RIGHT before the announcement:

```
@everyone

⚡ **INCOMING TRANSMISSION** ⚡

In 5 minutes, something ancient awakens...

The Guild Council will make an important announcement regarding guild membership.

Stand by.
```

Then post the main announcement 5 minutes later.

---

## 📞 Support

If members encounter issues:
1. Check bot permissions (does it have "Create Public Threads" in forums?)
2. Verify role requirements (do they have Wanderer/Seeker/Pathfinder/Trailwarden?)
3. Check logs: `/home/pfunc/data/Kody/The-Chronicler/logs/` (if running locally)
4. Restart bot if needed: `python main.py`

---

**Good luck with the launch, hero! For Azeroth Bound!** 🛡️
