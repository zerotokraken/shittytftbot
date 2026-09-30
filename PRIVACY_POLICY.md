# Privacy Policy

**Last Updated:** September 30, 2026

This Privacy Policy explains how **ShittyTFTBot** ("the Bot", "we", "us", "our") collects, uses, stores, and protects information when you interact with the Bot on Discord. By using the Bot, you consent to the practices described in this policy.

---

## 1. Information We Collect

### 1.1 Information You Provide Directly

When you use Bot commands, we may collect the following information that you voluntarily provide:

| Data | When Collected | Purpose |
|------|---------------|---------|
| **Discord User ID** | When using `.set`, `.suggest`, or other commands | To link your settings and data to your account |
| **TFT Game Name & Tag** | When using the `.set` command | To look up your TFT stats, match history, and ranked data |
| **Region Preference** | When using the `.set` command | To query the correct Riot Games API regional endpoint |
| **Suggestions** | When using the `.suggest` command | To record feature suggestions for the Bot |

### 1.2 Information Collected Automatically

The Bot may automatically collect and store the following data:

| Data | When Collected | Purpose |
|------|---------------|---------|
| **Channel Messages** | Hourly from designated channels | To power the `.malding`, `.fault`, `.psyop`, and `.ragebait` commands |
| **Message Metadata** | When messages are stored | Includes message ID, author ID, author name, content, and timestamp |
| **Deleted Messages** | When a message is deleted in the target server | Logged to a moderation channel for server administration |
| **Command Usage** | When invalid commands are used | Stored for tracking common misspellings and improving the Bot |

### 1.3 Information We Do NOT Collect

- We do **not** collect direct messages (DMs).
- We do **not** collect voice or video data.
- We do **not** collect your email address, IP address, or any information outside of Discord.
- We do **not** sell, trade, or rent your personal information to third parties.
- We do **not** use your data for advertising purposes.

## 2. How We Use Your Information

We use the collected information for the following purposes:

- **Providing Bot Services:** To respond to your commands, look up TFT data, and deliver the Bot's features.
- **User Settings:** To remember your TFT name, tag, and region so you don't have to re-enter them for every command.
- **Entertainment Features:** Channel messages are stored to power randomized message commands (`.malding`, `.fault`, `.psyop`, `.ragebait`).
- **Moderation:** Deleted message logging and moderation tools are used by server administrators to maintain community standards.
- **Improvement:** Suggestion data and command-not-found logs help us improve the Bot.

## 3. Data Storage and Security

- All data is stored in a **PostgreSQL database** hosted on **Heroku** with SSL encryption enabled (`sslmode='require'`).
- Access to the database is restricted to the Bot's runtime environment through environment variables.
- We take reasonable measures to protect your data, but no method of electronic storage is 100% secure. We cannot guarantee absolute security.

## 4. Data Retention

| Data Type | Retention Period |
|-----------|-----------------|
| **User Settings** (TFT name, tag, region) | Retained until you update them via `.set` or request deletion |
| **Suggestions** | Retained indefinitely for Bot improvement purposes |
| **Channel Messages** | Retained indefinitely for entertainment command functionality |
| **Deleted Message Logs** | Retained in the moderation log channel; subject to Discord's own data retention |
| **Command-Not-Found Logs** | Retained indefinitely for Bot improvement purposes |


## 5. Data Sharing

We do **not** share your personal data with third parties, except in the following limited circumstances:

- **Riot Games API:** Your TFT game name, tag, and region are sent to the Riot Games API to retrieve your game data. This is subject to [Riot Games' Privacy Policy](https://www.riotgames.com/en/privacy-notice).
- **tactics.tools:** Your TFT game name and tag may be used to generate links to your profile on tactics.tools.
- **Discord:** All Bot interactions occur on Discord's platform and are subject to [Discord's Privacy Policy](https://discord.com/privacy).
- **Heroku:** Our database is hosted on Heroku's platform, subject to [Heroku's Privacy Policy](https://www.heroku.com/policy/privacy).
- **Legal Requirements:** We may disclose your data if required by law or in response to valid legal processes.

## 6. Your Rights and Choices

### 6.1 Access and Update
- You can view your stored TFT settings by using relevant Bot commands.
- You can update your TFT name, tag, and region at any time by re-running the `.set` command.

### 6.2 Deletion
- You may request deletion of your stored data by contacting us at **ztk.cmg@gmail.com**.
- Please include your Discord User ID in your request so we can locate your records.
- We will process deletion requests in a reasonable timeframe.

### 6.3 Opt-Out
- You can stop using the Bot at any time. Simply do not interact with Bot commands.
- If you do not want your channel messages stored, please contact your server administrator about the channels being monitored.
- Server administrators can remove the Bot from their server at any time.

## 7. Children's Privacy

The Bot is not intended for use by individuals under the age of 13 (or the minimum age required by Discord in your jurisdiction). We do not knowingly collect personal information from children. If we become aware that we have collected data from a child under the applicable age, we will take steps to delete that information.


## 8. Third-Party Links and Services

The Bot may provide links to external websites and services (e.g., tactics.tools, Riot Games). We are not responsible for the privacy practices of these third-party services. We encourage you to review their privacy policies.

## 9. Message Logging Disclosure

Server administrators should be aware that the Bot includes a **message logging** feature:

- When enabled, deleted messages in the target server are logged to a designated moderation channel.
- This includes the message content, author information, channel, and timestamp.
- Ban and kick events are also logged with relevant user information.
- This feature is intended for moderation purposes only.

Server administrators are responsible for informing their members about message logging in accordance with applicable laws and Discord's guidelines.

## 10. Changes to This Privacy Policy

We may update this Privacy Policy from time to time. Changes will be reflected by updating the "Last Updated" date at the top of this document. We encourage you to review this policy periodically. Continued use of the Bot after changes constitutes acceptance of the updated policy.

## 11. Open Source

ShittyTFTBot is open-source software licensed under the [GNU General Public License v3 (GPL-3.0)](LICENSE). You can review the Bot's source code to verify our data practices.

## 12. Contact

If you have any questions, concerns, or requests regarding this Privacy Policy or your data, please contact us at:

📧 **Email:** ztk.cmg@gmail.com

---

*ShittyTFTBot is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.*

