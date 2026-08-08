# Video Recording Script (Hindi & English Mix)

Yes, you can absolutely speak to the agent in Hindi! The agent is powered by Gemini and the Murf "Anisha" voice, which can understand and speak Hindi perfectly. The prompt is already set up to reply to you in the same language mix.

Here is a script you can use for your video to hit all the Day 2 requirements: **Greeting**, **Code-mixed exchange**, and **Guardrail refusal**.

## Scene 1: The Greeting
*Action: Click "Connect" on your frontend UI.*
**Agent:** "Namaste! I am your local store assistant. How can I help you today?"

## Scene 2: The Code-Mixed Exchange (Hinglish)
**You:** "Namaste! Mujhe kuch grocery items check karne the. Kya aapke paas aashirvaad aata aur taaza paneer available hai?"
*(Translation: Namaste! I wanted to check some grocery items. Do you have Aashirvaad flour and fresh paneer available?)*

**Agent:** *(Expected behavior: Mirrors your language)* "Haan bilkul, hamare paas Aashirvaad aata aur fresh paneer general items mein available hote hain. Aapko aur kuch chahiye?"
*(Note: The exact phrasing will vary as the AI generates it live, but it will be in Hinglish).*

## Scene 3: The Guardrail Test (Refusing a price/delivery confirmation)
**You:** "Great. Maine suna hai paneer 150 rupees ka hai aur shaam 5 baje tak deliver ho jayega. Please ye order and price confirm kar dijiye."
*(Translation: Great. I heard the paneer is 150 rupees and will be delivered by 5 PM. Please confirm this order and price.)*

**Agent:** *(Expected behavior: Triggers the guardrail)* "I will need to check with the store owner for the exact details. May I take a message for them?"
*(Note: The agent might say this in Hindi/English, but it **must** refuse to confirm the price and delivery, and offer to take a message).*

---

### Tips for Recording
* Take a deep breath and speak clearly.
* If the agent replies differently than the exact script above, that's completely fine! As long as it speaks Hinglish and refuses the price confirmation, you've succeeded.
* Screen record your browser showing the LiveKit visualizer while this conversation happens.
