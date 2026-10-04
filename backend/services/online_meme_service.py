import hashlib
import json
import logging
import random
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("anchor.online_memes")

# 32+ Distinct Real-World Social Media Situations & Hard Roasts
# Direct CDN URLs from Reddit, Imgflip, Twitter, Know Your Meme
# Tone: HARD CRITICISM. Zero therapy coddling. Zero "aww you had it rough".
SITUATION_MEME_CATALOG: List[Dict[str, Any]] = [
    # 1. Left on delivered & replying in 2 seconds
    {
        "id": "delivered-fast-reply",
        "situation": "Left on delivered for hours/days and replying in 2 seconds",
        "keywords": ["delivered", "left on read", "read receipt", "replied fast", "replied immediately", "seconds", "unopened", "ignoring my text", "answered right away"],
        "phrases": ["on delivered", "left on read", "replied in", "texted back right away", "waited hours"],
        "meme_url": "https://i.imgflip.com/38el31.jpg",
        "verdict": "CLOWN SPEEDRUN",
        "critique": "They left you on delivered for two full business days and you replied in 1.4 seconds with a whole paragraph. Have some shame. Put your phone face-down and go do literally anything else with your life.",
        "source_title": "Putting on Clown Makeup (Reddit / Twitter)",
        "source_platform": "Reddit (r/me_irl)",
        "source_url": "https://knowyourmeme.com/memes/putting-on-clown-makeup",
        "query_used": "left on delivered replying immediately clown meme reddit"
    },

    # 2. Lending money while they party on Instagram
    {
        "id": "financed-their-weekend",
        "situation": "Lending money to someone who posts partying or luxury on social media",
        "keywords": ["money", "loan", "borrow", "debt", "pay back", "paid back", "cash", "rent", "lent", "lend", "lending", "$", "dollar", "owe", "owes", "stories", "party", "club"],
        "phrases": ["pay me back", "borrow money", "lent them", "owes me", "on instagram", "their story"],
        "meme_url": "https://i.imgflip.com/54hjww.jpg",
        "verdict": "UNPAID SPONSOR",
        "critique": "They swore they couldn't afford rent, but their Instagram story shows VIP table service and shopping bags. Congratulations, you just sponsored their weekend. You are an ATM with feelings. Stop giving handouts to people living better than you.",
        "source_title": "Trade Offer Meme (TikTok / Reddit)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/trade-offer",
        "query_used": "trade offer lent money instagram party meme"
    },

    # 3. 2 AM Location & Socials Stalking
    {
        "id": "unpaid-fbi-investigator",
        "situation": "Stalking someone's location, snap score, or active status late at night",
        "keywords": ["location", "stalk", "stalking", "snap score", "active now", "green dot", "find my", "who they with", "tracking", "checked their", "2am", "2 am", "3am"],
        "phrases": ["checked their location", "find my", "snap score", "active now", "who they are with"],
        "meme_url": "https://i.imgflip.com/1h7in3.jpg",
        "verdict": "UNPAID FBI INVESTIGATOR",
        "critique": "It's 2 AM and you're refreshing Find My, checking their snap score, and calculating time zones like an unpaid detective. If you need a full forensic team just to see if someone is faithful or lying, you already have your answer. Close the app.",
        "source_title": "Confused Math Lady Calculating (Reddit)",
        "source_platform": "Reddit (r/me_irl)",
        "source_url": "https://knowyourmeme.com/memes/math-lady-confused-lady",
        "query_used": "math lady calculating location snap score meme"
    },

    # 4. Texting the toxic ex when lonely / drunk
    {
        "id": "texting-the-ex",
        "situation": "Texting a toxic ex or blocked person late at night",
        "keywords": ["ex", "unblock", "unblocked", "texted him", "texted her", "lonely", "drunk text", "miss them", "reach out to them", "message my ex", "thinking of calling"],
        "phrases": ["text my ex", "called my ex", "unblock them", "drunk text", "thinking of reaching out"],
        "meme_url": "https://i.imgflip.com/1g8my4.jpg",
        "verdict": "DOWN HORRENDOUS",
        "critique": "One quiet Friday night and you're already typing 'Hey, thinking of you' to someone who treated your dignity like a suggestion. Throw your phone across the room before you embarrass yourself in front of your ancestors again.",
        "source_title": "Two Buttons / Daily Struggle (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/daily-struggle",
        "query_used": "two buttons daily struggle texting toxic ex meme"
    },

    # 5. Doomscrolling until 4 AM then complaining about life
    {
        "id": "doomscrolling-burnout",
        "situation": "Doomscrolling reels/TikTok until 4 AM and wondering why life is chaotic",
        "keywords": ["doomscroll", "doomscrolling", "tiktok", "reels", "scrolling", "phone at night", "4am", "4 am", "3am", "cant sleep", "tired all day", "exhausted", "sleep schedule"],
        "phrases": ["scrolling on my phone", "until 4am", "doom scrolling", "ruined my sleep", "watched reels"],
        "meme_url": "https://i.imgflip.com/wxica.jpg",
        "verdict": "CONSEQUENCES OF YOUR OWN ACTIONS",
        "critique": "You willingly blasted your retinas with brainrot reels until 4:30 AM and now you're acting like the universe cursed you with exhaustion. You built this disaster with your own two thumbs. Go to sleep.",
        "source_title": "This Is Fine Dog (Reddit / Twitter)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/this-is-fine",
        "query_used": "this is fine doomscrolling consequences meme"
    },

    # 6. Olympic level mental gymnastics excusing disrespect
    {
        "id": "olympic-mental-gymnastics",
        "situation": "Making ridiculous excuses for someone who blatantly disrespected you",
        "keywords": ["excuse", "excuses", "maybe they meant", "phone died", "so busy", "didnt mean to", "defending them", "just stressed", "good heart", "deep down"],
        "phrases": ["maybe their phone", "they are just stressed", "deep down they care", "did not mean it"],
        "meme_url": "https://i.imgflip.com/15yfd7.jpg",
        "verdict": "OLYMPIC MENTAL GYMNASTICS",
        "critique": "'Maybe their phone died, maybe they're just super overwhelmed.' Their phone worked just fine when they were posting on TikTok 10 minutes ago. Stop bending reality backwards to defend someone who couldn't care less.",
        "source_title": "Side Eye Chloe (Instagram / YouTube)",
        "source_platform": "Instagram",
        "source_url": "https://knowyourmeme.com/memes/side-eyeing-chloe",
        "query_used": "side eye chloe making excuses meme"
    },

    # 7. Professional victim complaining without changing
    {
        "id": "professional-victim",
        "situation": "Complaining constantly about the same toxic person without ever cutting them off",
        "keywords": ["again", "always does this", "complaining", "fed up", "same thing", "every time", "cant take it", "draining", "why do they always"],
        "phrases": ["did it again", "always does this", "every single time", "so sick of this"],
        "meme_url": "https://i.imgflip.com/392xtq.jpg",
        "verdict": "PROFESSIONAL VICTIM",
        "critique": "You have complained about this exact person twelve times this month and you still invite them over and answer their calls. At this point, the drama isn't happening to you—you're actively subscribing to it.",
        "source_title": "Disappointed Cricket Fan (Twitter / Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/disappointed-muhammad-sarim-akhtar",
        "query_used": "disappointed cricket fan complaining same thing meme"
    },

    # 8. Undercover Simp lurking in the friendzone
    {
        "id": "undercover-simp",
        "situation": "Pretending to be 'just a friend' hoping someone will magically fall for you",
        "keywords": ["crush", "friendzone", "bestie", "just friends", "driving them", "bought them coffee", "listened to them talk about their crush", "secretly like", "hoping they notice"],
        "phrases": ["just a friend", "secretly like", "drove them around", "bought them lunch", "talk about who they like"],
        "meme_url": "https://i.imgflip.com/1ur9b0.jpg",
        "verdict": "UNDERCOVER SIMP",
        "critique": "Buying them iced lattes, driving them across town, and listening to them complain about people they actually want to date. You are not a supportive bestie, you are a volunteer simp lurking in the friendzone waiting for crumbs. Stand up.",
        "source_title": "Distracted Boyfriend (Google Images)",
        "source_platform": "Google Images",
        "source_url": "https://knowyourmeme.com/memes/distracted-boyfriend",
        "query_used": "distracted boyfriend friendzone undercover simp meme"
    },

    # 9. Cryptic story for an audience of one
    {
        "id": "cringe-broadcast",
        "situation": "Posting cryptic songs, notes, or quotes hoping one specific person views it",
        "keywords": ["story", "instagram story", "note", "posted a song", "lyrics", "hoping they see", "viewed my story", "close friends", "cryptic"],
        "phrases": ["on my story", "posted a note", "check if they saw", "viewed my story", "hoping they watch"],
        "meme_url": "https://i.imgflip.com/265k.jpg",
        "verdict": "BROADCAST FOR AN AUDIENCE OF ONE",
        "critique": "Posting an obscure, moody Spotify song on your story just to see if their profile icon pops up in the viewers list. They skipped right past your story in 0.1 seconds without listening. Delete it before someone you respect sees it.",
        "source_title": "Awkward Monkey Puppet (Twitter / TikTok)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/awkward-look-monkey-puppet",
        "query_used": "monkey puppet posting story for one person meme"
    },

    # 10. Overanalyzing a single letter text like 'k'
    {
        "id": "hallucinating-drama",
        "situation": "Overthinking a 1-word text like 'k' or 'ok' into an apocalyptic crisis",
        "keywords": ["overthinking", "sent k", "said ok", "period at the end", "tone", "dry text", "one word", "analyzing", "why did they say", "mixed signals"],
        "phrases": ["they said ok", "sent a period", "dry texting", "overthinking the text", "said k"],
        "meme_url": "https://i.imgflip.com/345v97.jpg",
        "verdict": "HALLUCINATING DRAMA",
        "critique": "They sent a lowercase 'ok' and you've spent the last 45 minutes psychoanalyzing the absence of an exclamation point like it's ancient hieroglyphics. Drink a glass of cold water, you're literally fighting ghosts in your own head.",
        "source_title": "Brain Before Sleep (Reddit r/me_irl)",
        "source_platform": "Reddit (r/me_irl)",
        "source_url": "https://knowyourmeme.com/memes/are-you-going-to-sleep",
        "query_used": "brain before sleep overthinking dry text meme"
    },

    # 11. Shopping for enablers who agree with bad decisions
    {
        "id": "shopping-for-enablers",
        "situation": "Asking multiple people for advice until you find someone who tells you to make the bad choice",
        "keywords": ["advice", "asked my friends", "told me not to", "everyone says", "poll", "opinions", "enabler", "validation"],
        "phrases": ["my friends said", "asked 3 people", "everyone told me", "wanted another opinion"],
        "meme_url": "https://i.imgflip.com/30b1gx.jpg",
        "verdict": "SHOPPING FOR ENABLERS",
        "critique": "You ignored three sensible friends who told you to walk away, and kept polling people until you found the one unhinged friend who told you to double-text them. You don't want advice, you want an accomplice for your terrible decisions.",
        "source_title": "Drake Hotline Bling (Twitter / Instagram)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/drakeposting",
        "query_used": "drake hotline bling ignoring good advice meme"
    },

    # 12. Buying gifts / dinners hoping to buy affection
    {
        "id": "simping-bribery",
        "situation": "Paying for meals, drinks, or gifts hoping someone will finally like you back",
        "keywords": ["paid for dinner", "paid the bill", "bought them drinks", "bought a gift", "expensive", "treated them", "tab", "spent money on them", "never said thanks"],
        "phrases": ["paid for their", "bought them a gift", "picked up the tab", "paid the whole bill"],
        "meme_url": "https://i.imgflip.com/3oevdk.jpg",
        "verdict": "BRIBERY IS NOT AFFECTION",
        "critique": "You picked up their whole tab and bought them expensive gifts hoping it would buy their interest. Affection isn't an auction. If they weren't into you for free, paying for their dessert isn't going to change anything.",
        "source_title": "Bernie Asking For Support (Twitter)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/i-am-once-again-asking-for-your-financial-support",
        "query_used": "i am once again asking paying for dinner meme"
    },

    # 13. Procrastinating until 2 hours before deadline
    {
        "id": "procrastination-panic",
        "situation": "Leaving an exam, assignment, or work project until the final hour and panicking",
        "keywords": ["procrastinated", "exam", "assignment", "due tomorrow", "due in an hour", "deadline", "havent started", "crying over work", "cramming", "test"],
        "phrases": ["due in 2 hours", "due tomorrow morning", "havent started yet", "cramming all night"],
        "meme_url": "https://i.imgflip.com/2ya12p.jpg",
        "verdict": "SELF-INFLICTED PANIC",
        "critique": "You had three whole weeks to work on this, spent 20 days playing games and reorganizing your desk drawers, and now you're having an existential breakdown over 'unreasonable workloads'. Take your accountability with your triple espresso.",
        "source_title": "Ah Shit, Here We Go Again (GTA / Twitter)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/ah-shit-here-we-go-again",
        "query_used": "ah shit here we go again procrastination deadline meme"
    },

    # 14. Fake nonchalance: Claiming 'I literally don't care' in a 500-word rant
    {
        "id": "fake-nonchalance",
        "situation": "Pretending to be completely unbothered while visibly boiling with rage",
        "keywords": ["dont care", "unbothered", "couldnt care less", "whatever", "im fine", "doesnt bother me", "not even mad", "chill"],
        "phrases": ["literally do not care", "could not care less", "i am so unbothered", "im not even mad"],
        "meme_url": "https://i.imgflip.com/w2k5w.jpg",
        "verdict": "FAKE NONCHALANCE",
        "critique": "'I'm so unbothered, I literally don't even care.' You just wrote 600 words detailing how much you don't care. You are bothered down to your molecular level. Just admit you're furious and stop the tough-guy performance.",
        "source_title": "Kermit Sipping Tea (Instagram / Twitter)",
        "source_platform": "Instagram",
        "source_url": "https://knowyourmeme.com/memes/but-thats-none-of-my-business",
        "query_used": "kermit sipping tea fake nonchalance unbothered meme"
    },

    # 15. Doormat behavior: Apologizing to the person who wronged you
    {
        "id": "gaslight-apology",
        "situation": "Apologizing to someone who mistreated you just to avoid awkward tension",
        "keywords": ["apologized to them", "said sorry first", "kept the peace", "didnt want conflict", "awkward silence", "felt bad", "apology", "guilt trip"],
        "phrases": ["i apologized to them", "said sorry even though", "to keep the peace", "did not want an argument"],
        "meme_url": "https://i.imgflip.com/1tkjq9.jpg",
        "verdict": "DOORMAT BEHAVIOR",
        "critique": "They insulted you, broke their promise, and somehow YOU ended up sending a 3-paragraph apology text because you couldn't handle 20 minutes of tension? Stand on your own two feet, stop apologizing for having a pulse.",
        "source_title": "Spider-Man Pointing (Reddit / Twitter)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/spider-man-pointing-at-spider-man",
        "query_used": "spider-man pointing doormat apology meme"
    },

    # 16. Financial delusion: Broke with expensive taste
    {
        "id": "financial-delusion",
        "situation": "Spending money you do not have on luxury meals or clothes",
        "keywords": ["broke", "shopping", "ubereats", "doordash", "expensive", "credit card", "negative balance", "overdraft", "splurged", "treat myself"],
        "phrases": ["treated myself", "ordered ubereats", "on my credit card", "have no money left"],
        "meme_url": "https://i.imgflip.com/24y43o.jpg",
        "verdict": "FINANCIAL DELUSION",
        "critique": "Your bank account balance has two digits in it and you just ordered a $35 artisanal sandwich on DoorDash with priority delivery. You're living like an oil baron on an intern's debit card. Put the phone down and eat pasta.",
        "source_title": "Change My Mind (Twitter / Reddit)",
        "source_platform": "Google Images",
        "source_url": "https://knowyourmeme.com/memes/steven-crowders-change-my-mind-mug",
        "query_used": "change my mind broke with expensive taste meme"
    },

    # 17. The toxic sequel: Getting back with an ex for round 4
    {
        "id": "toxic-sequel",
        "situation": "Getting back with someone who has broken your heart 3 times already",
        "keywords": ["back together", "give them another chance", "round 4", "fourth time", "swore they changed", "promised to be better", "rekindled"],
        "phrases": ["got back together", "giving them another chance", "swore they changed", "this time will be different"],
        "meme_url": "https://i.imgflip.com/2ya12p.jpg",
        "verdict": "THE TOXIC SEQUEL",
        "critique": "Season 4 of the exact same trainwreck. You know the script, you know how every argument goes, and you still bought a front-row ticket. Don't act shocked when the season finale ends in tears and blocked numbers again.",
        "source_title": "Ah Shit Here We Go Again (Reddit)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/ah-shit-here-we-go-again",
        "query_used": "ah shit here we go again toxic ex sequel meme"
    },

    # 18. Nostalgia tax: Clinging to 10-year friendship that expired
    {
        "id": "nostalgia-tax",
        "situation": "Enduring disrespect because you've been friends since childhood",
        "keywords": ["years", "known each other", "history", "nostalgia", "old friend", "childhood", "used to be", "known them for years", "high school", "middle school"],
        "phrases": ["known them for", "years of friendship", "since high school", "since childhood", "used to be close"],
        "meme_url": "https://i.imgflip.com/1ur9b0.jpg",
        "verdict": "THE NOSTALGIA TAX",
        "critique": "You've been tolerating disrespect and one-sided energy for three years purely on the memory of sharing markers in seventh grade. Longevity is not loyalty when the respect expired half a decade ago. Wake up.",
        "source_title": "Distracted Boyfriend (Reddit / Twitter)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/distracted-boyfriend",
        "query_used": "distracted boyfriend nostalgia trap fake friend meme"
    },

    # 19. Ghosting cowardice: Avoiding a 30-second honest text
    {
        "id": "ghosting-cowardice",
        "situation": "Ghosting someone because an honest 30-second text is 'too uncomfortable'",
        "keywords": ["ghosted", "ghosting", "flaked", "avoiding them", "didnt reply", "vanished", "too awkward", "confrontation"],
        "phrases": ["just ghosted", "did not text back", "avoiding the confrontation", "pretended i was asleep"],
        "meme_url": "https://i.imgflip.com/15yfd7.jpg",
        "verdict": "CERTIFIED COWARDICE",
        "critique": "Too cowardly to send a simple 'Hey, I'm not feeling this' text, so you turned off your read receipts and pretended you fell off the planet. Vanishing into thin air isn't boundary-setting, it's emotional kindergarten.",
        "source_title": "Side Eye Chloe (Instagram)",
        "source_platform": "Instagram",
        "source_url": "https://knowyourmeme.com/memes/side-eyeing-chloe",
        "query_used": "side eye chloe ghosting cowardice meme"
    },

    # 20. TikTok psychiatry: Diagnosing people with 10 mental disorders
    {
        "id": "tiktok-psychiatry",
        "situation": "Diagnosing someone who annoyed you as a narcissist after 2 TikTok videos",
        "keywords": ["narcissist", "gaslight", "gaslighting", "trauma bond", "toxic", "bpd", "avoidant", "discard", "tiktok diagnosis", "manipulative"],
        "phrases": ["they are a narcissist", "avoidant attachment", "covert narcissist", "trauma bonded"],
        "meme_url": "https://i.imgflip.com/1h7in3.jpg",
        "verdict": "TIKTOK PSYCHIATRY",
        "critique": "Someone took 3 hours to text you back and you've already diagnosed them with covert narcissistic personality disorder and an avoidant attachment wound. Put the phone down. Sometimes people are just rude or uninterested.",
        "source_title": "Math Lady Calculating (Twitter)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/math-lady-confused-lady",
        "query_used": "math lady tiktok psychiatry diagnosing narcissist meme"
    },

    # 21. Gym cosplayer: Buying $200 gear and quitting on day 2
    {
        "id": "gym-cosplayer",
        "situation": "Buying workout clothes and protein powder then never going to the gym",
        "keywords": ["gym", "workout", "fitness", "protein", "supplements", "villain arc", "locked in", "diet", "quit gym"],
        "phrases": ["bought gym clothes", "villain arc", "locked in for the gym", "day 1 of fitness"],
        "meme_url": "https://i.imgflip.com/38el31.jpg",
        "verdict": "FITNESS COSPLAYER",
        "critique": "You spent $160 on matching gym sets and strawberry protein powder, posted a story saying 'entering my villain arc', and haven't touched a dumbbell since Tuesday. Buying the costume doesn't make you an athlete.",
        "source_title": "Clown Makeup Progression (TikTok)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/putting-on-clown-makeup",
        "query_used": "clown makeup fitness villain arc quitting meme"
    },

    # 22. Silent treatment mind-reading
    {
        "id": "mind-reading-fallacy",
        "situation": "Giving the silent treatment and expecting people to read your mind",
        "keywords": ["silent treatment", "they should know", "should have guessed", "not telling them", "giving cold shoulder", "pouting", "mad at them"],
        "phrases": ["they should know why", "giving the silent treatment", "not going to tell them", "they should just know"],
        "meme_url": "https://i.imgflip.com/15yfd7.jpg",
        "verdict": "MIND-READER EXPECTATIONS",
        "critique": "'They should just know what they did wrong.' Nobody is telepathic. Hiding in the corner with your arms crossed like an angry toddler solves zero problems. Open your mouth and state the issue.",
        "source_title": "Side Eye Chloe (Twitter)",
        "source_platform": "Instagram",
        "source_url": "https://knowyourmeme.com/memes/side-eyeing-chloe",
        "query_used": "side eye chloe silent treatment mind reader meme"
    },

    # 23. Chaos addiction: Rejecting nice people because they are 'boring'
    {
        "id": "chaos-addiction",
        "situation": "Getting 'the ick' from healthy, kind people because you crave toxicity",
        "keywords": ["the ick", "too nice", "boring", "miss the drama", "good on paper", "no spark", "healthy relationship", "red flags attracted to"],
        "phrases": ["got the ick", "they are too nice", "there is no spark", "i miss the chaos"],
        "meme_url": "https://i.imgflip.com/30b1gx.jpg",
        "verdict": "ADDICTED TO CHAOS",
        "critique": "Someone treats you with respect, answers your texts on time, and values your peace, and you get 'the ick' because there's no manufactured crisis to cry about. You are addicted to emotional rollercoasters. Fix your taste.",
        "source_title": "Drake Rejecting and Accepting (TikTok)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/drakeposting",
        "query_used": "drake hotline bling rejecting nice people wanting red flags meme"
    },

    # 24. Two-faced gossip: Smiling to their face, trashing them in the car
    {
        "id": "two-faced-gossip",
        "situation": "Hanging out with people you secretly despise and gossiping about them instantly",
        "keywords": ["talked behind their back", "fake friend", "hate them", "annoying", "talked trash", "car ride", "hugged them goodbye", "cant stand them"],
        "phrases": ["in the car after", "hugged them but", "talked about them behind", "hate hanging out with"],
        "meme_url": "https://i.imgflip.com/1tkjq9.jpg",
        "verdict": "TWO-FACED CONNOISSEUR",
        "critique": "You spent four hours laughing at their jokes and hugging them goodbye, then didn't even make it past the driveway before tearing their entire personality apart. If you despise them that much, stop accepting their invitations.",
        "source_title": "Spider-Man Pointing at Spider-Man (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/spider-man-pointing-at-spider-man",
        "query_used": "spider-man fake friend talking behind back meme"
    },

    # 25. Chronic apologizer: Apologizing for breathing
    {
        "id": "chronic-apologizer",
        "situation": "Saying sorry constantly for asking normal questions or taking up space",
        "keywords": ["sorry to bother", "sorry if dumb", "said sorry", "apologize too much", "afraid of annoying", "took up space"],
        "phrases": ["sorry to bother you", "sorry if this is dumb", "apologized for asking", "always saying sorry"],
        "meme_url": "https://i.imgflip.com/265k.jpg",
        "verdict": "CHRONIC APOLOGIZER",
        "critique": "You said 'sorry' three times before asking where the restroom was. You are a human being allowed to occupy physical and conversational space. Stop apologizing for literally existing.",
        "source_title": "Monkey Puppet Looking Away (Twitter)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/awkward-look-monkey-puppet",
        "query_used": "monkey puppet chronic apologizer saying sorry meme"
    },

    # 26. Social media envy: Comparing your real life to staged reels
    {
        "id": "social-media-envy",
        "situation": "Getting depressed comparing your behind-the-scenes to other people's highlight reels",
        "keywords": ["jealous", "envy", "everyone is succeeding", "everyone is rich", "vacation pictures", "falling behind", "loser", "comparisons"],
        "phrases": ["saw them on vacation", "everyone is doing better", "falling behind in life", "comparing myself to"],
        "meme_url": "https://i.imgflip.com/392xtq.jpg",
        "verdict": "COMPARISON POISON",
        "critique": "They took 600 takes, argued with their partner for two hours, and posted the one 10-second clip where the lighting looked rich. And here you are having a mid-life crisis over their staged vacation. Close Instagram.",
        "source_title": "Disappointed Cricket Fan (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/disappointed-muhammad-sarim-akhtar",
        "query_used": "disappointed cricket fan comparing on instagram meme"
    },

    # 27. First date interrogation / trauma dump
    {
        "id": "first-date-trauma-dump",
        "situation": "Trauma-dumping your entire psychiatric history on a casual date",
        "keywords": ["first date", "trauma dump", "told them everything", "told my ex story", "cried on the date", "scared them away", "overshared"],
        "phrases": ["on the first date", "trauma dumped", "overshared with them", "scared them off"],
        "meme_url": "https://i.imgflip.com/265k.jpg",
        "verdict": "FIRST DATE AMBUSH",
        "critique": "They asked what kind of music you like and within fifteen minutes you were dissecting your childhood abandonment issues and your toxic ex's blood type. Let the poor person order their appetizer first.",
        "source_title": "Monkey Puppet (TikTok / Twitter)",
        "source_platform": "TikTok",
        "source_url": "https://knowyourmeme.com/memes/awkward-look-monkey-puppet",
        "query_used": "monkey puppet oversharing first date trauma dump meme"
    },

    # 28. Flaking and celebrating canceling plans
    {
        "id": "flake-celebration",
        "situation": "Canceling plans at the last minute and celebrating staying home in pajamas",
        "keywords": ["cancelled plans", "called in sick", "stayed in bed", "so happy they canceled", "avoided going out", "flaked on dinner"],
        "phrases": ["cancelled last minute", "flaked on plans", "glad they cancelled", "texted that i was sick"],
        "meme_url": "https://i.imgflip.com/w2k5w.jpg",
        "verdict": "UNRELIABLE FRIEND",
        "critique": "You let them get fully dressed, start their car, and then sent 'So sorry, feeling under the weather!' while you were already cozy in sweatpants eating cereal. You're not an introvert, you're just unreliable.",
        "source_title": "Kermit Sipping Tea (Twitter / Reddit)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/but-thats-none-of-my-business",
        "query_used": "kermit tea cancelling plans staying home meme"
    },

    # 29. Gaslighting deflection in arguments
    {
        "id": "argument-deflection",
        "situation": "Bringing up unrelated ancient history when called out on bad behavior",
        "keywords": ["argued", "defensive", "brought up 3 years ago", "yelling", "turned it on me", "screaming", "deflection", "fight"],
        "phrases": ["brought up the past", "turned it back on me", "started screaming", "attacked my tone"],
        "meme_url": "https://i.imgflip.com/1tkjq9.jpg",
        "verdict": "HISTORICAL DEFLECTION",
        "critique": "Notice how the moment you brought up a valid issue, they immediately brought up something you did back in 2021 to avoid answering for today. That's not communication, that's courtroom deflection.",
        "source_title": "Spider-Man Pointing (Reddit / Twitter)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/spider-man-pointing-at-spider-man",
        "query_used": "spider-man argument deflection bringing up past meme"
    },

    # 30. Imposter syndrome panic
    {
        "id": "imposter-panic",
        "situation": "Panicking that you are an unqualified fraud when you earned your spot",
        "keywords": ["imposter syndrome", "fraud", "unqualified", "going to get fired", "panic at work", "dont know what im doing"],
        "phrases": ["imposter syndrome", "feel like a fraud", "unqualified for this", "faked my way in"],
        "meme_url": "https://i.imgflip.com/1h7in3.jpg",
        "verdict": "IMPOSTER HYSTERIA",
        "critique": "You've convinced yourself you're an unqualified imposter who tricked everyone. They didn't pick your resume out of a bingo cage. Stop panicking, open your laptop, and do the work you were hired to do.",
        "source_title": "Math Lady (LinkedIn / Reddit)",
        "source_platform": "Reddit (r/me_irl)",
        "source_url": "https://knowyourmeme.com/memes/math-lady-confused-lady",
        "query_used": "math lady imposter syndrome panic meme"
    },

    # 31. Performance wealth
    {
        "id": "performance-wealth",
        "situation": "Agreeing to crazy expensive activities to look cool in front of fake friends",
        "keywords": ["cant afford it", "agreed to go", "expensive restaurant", "bill split", "peer pressure", "pretend to have money"],
        "phrases": ["could not afford it but", "split the bill", "expensive dinner with friends", "wanted to look cool"],
        "meme_url": "https://i.imgflip.com/24y43o.jpg",
        "verdict": "PERFORMANCE WEALTH",
        "critique": "You agreed to a $120 dinner you can't afford in front of people who won't even remember what shoes you wore. Now you're eating ramen for two weeks to impress acquaintances. Drop the fake lifestyle.",
        "source_title": "Change My Mind (Twitter)",
        "source_platform": "Google Images",
        "source_url": "https://knowyourmeme.com/memes/steven-crowders-change-my-mind-mug",
        "query_used": "change my mind performance wealth expensive dinner meme"
    },

    # 32. General hard reality check
    {
        "id": "general-hard-reality",
        "situation": "General life reality check",
        "keywords": ["reality", "truth", "realize", "hard lesson", "done with this", "finally learned"],
        "phrases": ["finally learned", "hard lesson", "realized the truth"],
        "meme_url": "https://i.imgflip.com/24y43o.jpg",
        "verdict": "UNDISPUTED REALITY",
        "critique": "Actions reveal commitment; words just reveal intentions. Stop evaluating people based on potential or sweet apologies, and start evaluating them on consistent behavior. Change my mind.",
        "source_title": "Change My Mind (Google Images / Reddit)",
        "source_platform": "Google Images",
        "source_url": "https://knowyourmeme.com/memes/steven-crowders-change-my-mind-mug",
        "query_used": "change my mind harsh reality check meme"
    },

    # 33. Surprised Pikachu
    {
        "id": "surprised-pikachu",
        "situation": "Acting completely shocked when someone does the exact thing they always do",
        "keywords": ["shocked", "surprised", "disbelief", "blindsided", "unexpected", "how could they", "speechless", "pikachu"],
        "phrases": ["shocked that they", "could not believe", "did it again and i was shocked", "how could they do this"],
        "meme_url": "https://i.imgflip.com/2kbn1e.jpg",
        "verdict": "SURPRISED PIKACHU",
        "critique": "Touch hot stove. Hand gets scorched. Stare in absolute jaw-dropped shock. You knew their exact track record and you still gave the stunned Pikachu face when they did the exact thing they've done eight times in a row.",
        "source_title": "Surprised Pikachu (Reddit / Twitter)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/surprised-pikachu",
        "query_used": "surprised pikachu predictable outcome meme"
    },

    # 34. Buff Doge vs Cheems
    {
        "id": "buff-doge-cheems",
        "situation": "Planning a savage confrontation in your head vs mumbling 'no worries haha' in person",
        "keywords": ["shower argument", "confront", "chickened out", "said no worries", "held my tongue", "quiet", "scared to speak", "cheems"],
        "phrases": ["in my head i was going to", "in person i just said", "shower argument", "too nervous to speak up", "said it was fine"],
        "meme_url": "https://i.imgflip.com/43a45p.jpg",
        "verdict": "IMAGINARY TOUGH GUY",
        "critique": "In your shower fantasies, you deliver an Oscar-worthy monologue putting them in their place. In actual reality, you swallowed your pride, muttered 'no worries all good haha', and stared at your sneakers.",
        "source_title": "Swole Doge vs. Cheems (Reddit)",
        "source_platform": "Reddit (r/dogelore)",
        "source_url": "https://knowyourmeme.com/memes/swole-doge-vs-cheems",
        "query_used": "swole doge vs cheems confrontation fantasy vs reality meme"
    },

    # 35. Ralph Wiggum Danger
    {
        "id": "ralph-wiggum-danger",
        "situation": "Voluntarily stepping into an obvious toxic disaster with zero survival instinct",
        "keywords": ["danger", "hazard", "red flag", "know its bad", "bad idea", "disaster", "stupid idea", "ralph"],
        "phrases": ["bad idea but", "know i should not", "heading into a mess", "about to get hurt", "walking into fire"],
        "meme_url": "https://i.imgflip.com/261o3j.jpg",
        "verdict": "IM IN DANGER",
        "critique": "'Haha, I'm in danger!' You smiled, brushed off three warnings from close friends, and walked straight into a category 5 toxic disaster. Ralph Wiggum has better crisis awareness than you right now.",
        "source_title": "Ralph Wiggum In Danger (Twitter / Reddit)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/im-in-danger",
        "query_used": "ralph wiggum im in danger meme twitter"
    },

    # 36. Always has been
    {
        "id": "always-has-been",
        "situation": "Belatedly realizing you were just being used for rides, homework, or money",
        "keywords": ["used", "using me", "user", "ride", "homework", "favors", "convenience", "leech", "astronaut"],
        "phrases": ["used me for", "only called when they needed", "realized they never cared", "wait they were using me"],
        "meme_url": "https://i.imgflip.com/46e43q.jpg",
        "verdict": "ALWAYS HAS BEEN",
        "critique": "'Wait, they only invited me because I have a car and pay for parking?' Always has been. The only person surprised by this realization is you.",
        "source_title": "Wait It's All Ohio? Always Has Been (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/wait-its-all-ohio-always-has-been",
        "query_used": "always has been astronaut being used meme"
    },

    # 37. Gru's Masterplan Collapse
    {
        "id": "grus-plan-disaster",
        "situation": "Devising a petty strategy that completely backfired on you",
        "keywords": ["plan", "backfired", "revenge", "jealous", "masterplan", "failed plan", "scheme", "gru"],
        "phrases": ["tried to make them", "backfired completely", "my plan was", "thought it would work", "stared in horror"],
        "meme_url": "https://i.imgflip.com/26jxvz.jpg",
        "verdict": "GRU MASTERPLAN COLLAPSE",
        "critique": "Panel 1: Try to make them jealous. Panel 2: Post someone else on your story. Panel 3: They mute and unfollow you. Panel 4: Stare in horror at your own failure. Outstanding tactical mind.",
        "source_title": "Gru's Plan (Reddit / Know Your Meme)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/grus-plan",
        "query_used": "grus plan presentation backfired meme"
    },

    # 38. Anakin & Padme Delusional Bargaining
    {
        "id": "anakin-padme-delusion",
        "situation": "Reaching out because 'they matured' while knowing deep down they haven't",
        "keywords": ["changed right", "matured", "different now", "grown up", "reformed", "sweet now", "anakin", "padme"],
        "phrases": ["because they changed right", "they matured right", "giving them a pass", "hope they are better"],
        "meme_url": "https://i.imgflip.com/5c7lwq.jpg",
        "verdict": "DELUSIONAL BARGAINING",
        "critique": "'I unblocked them and invited them out.' 'Because they took accountability and apologized, right?' '...' 'Because they apologized, right??' You know damn well they haven't changed an inch.",
        "source_title": "For the Better, Right? (Twitter / Reddit)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/for-the-better-right",
        "query_used": "for the better right anakin padme meme"
    },

    # 39. Party Corner Lurker
    {
        "id": "party-corner-lurker",
        "situation": "Sulking in the corner of social gatherings feeling misunderstood",
        "keywords": ["party", "gathering", "corner", "isolated", "social anxiety", "superior", "dont know", "awkward"],
        "phrases": ["at the party", "nobody talked to me", "standing in the corner", "felt so out of place", "staring at my phone"],
        "meme_url": "https://i.imgflip.com/4pn1an.jpg",
        "verdict": "PARTY CORNER LURKER",
        "critique": "'They don't know I have profound emotional depth and refined music taste.' Nobody cares. You're standing by the hummus bowl refreshing Twitter waiting for someone to adopt you. Go talk to someone.",
        "source_title": "They Don't Know Party Corner (Reddit)",
        "source_platform": "Reddit (r/me_irl)",
        "source_url": "https://knowyourmeme.com/memes/i-wish-i-was-at-home-they-dont-know",
        "query_used": "they dont know party corner lurker meme"
    },

    # 40. Bare Minimum Romanticizer
    {
        "id": "bare-minimum-romanticizer",
        "situation": "Mistaking basic politeness or manners for deep romantic interest",
        "keywords": ["held the door", "manners", "polite", "bare minimum", "romanticizing", "wedding", "in love with me", "pigeon"],
        "phrases": ["held the door", "smiled at me", "asked how i was", "does this mean they like me", "must have feelings"],
        "meme_url": "https://i.imgflip.com/2fm6x0.jpg",
        "verdict": "BARE MINIMUM ROMANTICIZER",
        "critique": "They held the elevator door and said 'have a good weekend', and you've spent the evening planning your future children's names. That is basic civil etiquette, not a divine soulmate contract.",
        "source_title": "Is This a Pigeon? (Twitter / Reddit)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/is-this-a-pigeon",
        "query_used": "is this a pigeon bare minimum politeness meme"
    },

    # 41. Left Exit Swerve into Chaos
    {
        "id": "left-exit-swerve-chaos",
        "situation": "Passing up peace and choosing immediate drama and self-destruction",
        "keywords": ["swerve", "exit", "chose drama", "could have ignored", "instead of letting it go", "double text", "blew up", "ramp"],
        "phrases": ["could have let it go", "decided to argue", "sent 5 texts instead", "chose violence", "swerved into"],
        "meme_url": "https://i.imgflip.com/22bdq6.jpg",
        "verdict": "EMERGENCY SWERVE INTO CHAOS",
        "critique": "Straight highway: Mute the group chat, watch Netflix, and get 8 hours of sleep. Sharp exit ramp: Fire off three passive-aggressive paragraphs with screenshot receipts. You swerved across four lanes without braking.",
        "source_title": "Left Exit 12 Off Ramp (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/left-exit-12-off-ramp",
        "query_used": "left exit 12 swerving highway chaos meme"
    },

    # 42. Stick in Bicycle Spokes
    {
        "id": "baton-in-bicycle-spokes",
        "situation": "Actively causing your own problem and blaming everyone else",
        "keywords": ["sabotage", "self sabotage", "shot myself in the foot", "own fault", "victim of my own", "why did this happen", "bicycle"],
        "phrases": ["caused my own problem", "why did this happen to me", "shot myself in the foot", "ruined my own day"],
        "meme_url": "https://i.imgflip.com/1bip.jpg",
        "verdict": "STICK IN BICYCLE SPOKES",
        "critique": "You jammed a metal rod directly into your own bicycle wheel, flew over the handlebars onto concrete, and started screaming 'Why would they do this to me?!' You engineered this entire wreck.",
        "source_title": "Baton Rouge / Bicycle Fall (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/baton-rouge-bike-fall",
        "query_used": "bicycle fall stick in spokes self sabotage meme"
    },

    # 43. Squidward Window Sulker
    {
        "id": "squidward-window-sulking",
        "situation": "Refusing invitations then being bitter that people had fun without you",
        "keywords": ["squidward", "left out", "bitter", "fomo", "had fun without me", "sulking", "jealous of plans", "excluded"],
        "phrases": ["did not invite me", "had fun without me", "saw their pictures", "sulking at home", "bitter that they went"],
        "meme_url": "https://i.imgflip.com/145qvv.jpg",
        "verdict": "SQUIDWARD WINDOW SULKER",
        "critique": "Watching everyone else laugh through the blinds while you sit inside in the dark nursing resentment. You rejected their last three invitations and now you're mad they stopped begging you. Fix your attitude.",
        "source_title": "Squidward Looking Out Window (Twitter)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/squidward-looking-out-the-window",
        "query_used": "squidward looking out window fomo sulking meme"
    },

    # 44. Panik Kalm Panik
    {
        "id": "panik-kalm-panik",
        "situation": "Briefly finding peace before inventing an even worse scenario to panic about",
        "keywords": ["panik", "kalm", "panic again", "spiral", "false alarm", "even worse", "heart rate"],
        "phrases": ["calmed down then", "thought it was fine until", "started panicking again", "spiral started over"],
        "meme_url": "https://i.imgflip.com/3qqcim.jpg",
        "verdict": "PANIK KALM PANIK",
        "critique": "Kalm: 'Maybe they're just taking a nap.' Panik: 'Their Spotify status just changed to workout hype tracks.' Kalm: 'Maybe it's a playlist on shuffle.' Panik: 'They just liked someone's selfie.' Your cortisol levels are weeping.",
        "source_title": "Panik Kalm Panik (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/panik-kalm-panik",
        "query_used": "panik kalm panik meme reddit"
    },

    # 45. Hard to Swallow Pills
    {
        "id": "hard-to-swallow-pills",
        "situation": "Refusing to accept the simple rule: If they wanted to, they would",
        "keywords": ["hard pill", "hard truth", "if they wanted to", "too busy", "no time", "excuse for not calling", "pills"],
        "phrases": ["if they wanted to they would", "too busy to call", "hard truth", "refusing to accept", "pills"],
        "meme_url": "https://i.imgflip.com/271ps6.jpg",
        "verdict": "HARD TO SWALLOW PILLS",
        "critique": "Hard pill to swallow: People check their phones 150 times a day. If they wanted to text you, they would. If they wanted to make plans, they would. Stop writing fanfiction excuses for someone who treats you like an option.",
        "source_title": "Hard to Swallow Pills (Reddit / Twitter)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/hard-to-swallow-pills",
        "query_used": "hard to swallow pills if they wanted to they would meme"
    },

    # 46. Skeleton Waiting on Bench
    {
        "id": "skeleton-waiting-bench",
        "situation": "Holding out for closure or an apology from someone incapable of accountability",
        "keywords": ["closure", "waiting for apology", "admit it", "own up", "never said sorry", "skeleton", "bench"],
        "phrases": ["waiting for an apology", "need closure", "waiting for them to admit", "waiting for closure", "admit they were wrong"],
        "meme_url": "https://i.imgflip.com/2ybsoo.jpg",
        "verdict": "SKELETON WAITING FOR CLOSURE",
        "critique": "Sitting on the park bench waiting for an immature person to have a sudden moral awakening and deliver a heartfelt apology. You will turn into fossilized limestone before that day arrives. Closure is what you give yourself.",
        "source_title": "Waiting Skeleton on Bench (Know Your Meme)",
        "source_platform": "Google Images",
        "source_url": "https://knowyourmeme.com/memes/waiting-skeleton",
        "query_used": "waiting skeleton on bench closure apology meme"
    },

    # 47. Flex Tape on a Sinking Ship
    {
        "id": "flex-tape-slap",
        "situation": "Trying to fix fundamental disrespect with a superficial gift or date",
        "keywords": ["flex tape", "band aid", "surface fix", "bought flowers", "cute date", "pretend its fine", "temporary fix", "phil swift"],
        "phrases": ["bought them flowers to fix", "cute date to forget", "pretending it fixed everything", "band aid on"],
        "meme_url": "https://i.imgflip.com/28j0te.jpg",
        "verdict": "FLEX TAPE ON A SINKING SHIP",
        "critique": "Slapping a cute sushi dinner and a heart emoji over three months of emotional dishonesty like Flex Tape over a blown engine block. The water is already up to your neck, captain. Patching the surface changes nothing.",
        "source_title": "Flex Tape Phil Swift (YouTube / Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/flex-tape",
        "query_used": "flex tape slapping water leak superficial fix meme"
    },

    # 48. They Had Us in the First Half
    {
        "id": "they-had-us-in-first-half",
        "situation": "Getting buttered up with sweet words only to be hit with a massive favor request",
        "keywords": ["first half", "sweet text", "buttering me up", "then asked for", "favor request", "catch", "string attached"],
        "phrases": ["started so sweet then", "asked for a huge favor", "said they missed me then", "they had us in the first half"],
        "meme_url": "https://i.imgflip.com/2zjn96.jpg",
        "verdict": "THEY HAD US IN THE FIRST HALF",
        "critique": "'Hey bestie, I've been thinking about how amazing you are and how lucky I am to know you... anyway, can you watch my dog for 5 days and lend me $200?' They had you in the first half, but the con is transparent.",
        "source_title": "They Had Us in the First Half (Twitter / Reddit)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/they-had-us-in-the-first-half",
        "query_used": "they had us in the first half not gonna lie meme"
    },

    # 49. Galaxy Brain Overthinking
    {
        "id": "galaxy-brain-overthinking",
        "situation": "Inventing absurd cosmic theories to justify why someone treated you poorly",
        "keywords": ["galaxy brain", "twin flame", "karmic", "inner child", "astrology excuse", "mercury retrograde", "deep reasons"],
        "phrases": ["twin flame", "karmic lesson", "divine timing", "their inner child", "galaxy brain"],
        "meme_url": "https://i.imgflip.com/1jwhww.jpg",
        "verdict": "GALAXY BRAIN MENTAL GYM",
        "critique": "Level 1: They flaked. Level 2: They are stressed. Level 3: Their unhealed inner child is scared of intimacy. Level 4: We are twin flames enduring karmic alignment. Stop doing spiritual acrobatics to justify basic flakiness.",
        "source_title": "Galaxy Brain / Expanding Brain (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/galaxy-brain",
        "query_used": "galaxy brain expanding brain mental gymnastics meme"
    },

    # 50. Selective Outrage Shaq
    {
        "id": "sleeping-shaq-selective",
        "situation": "Ignoring huge betrayals but having a nuclear meltdown over a minor perceived slight",
        "keywords": ["selective", "shaq", "wrong thing", "blew up over nothing", "let them get away with", "misdirected anger"],
        "phrases": ["let the big things slide", "freaked out over an emoji", "sleeping shaq", "mad about the wrong thing"],
        "meme_url": "https://i.imgflip.com/1jxfea.jpg",
        "verdict": "SELECTIVE OUTRAGE",
        "critique": "Sleeping Shaq: They disrespect your goals, lie about plans, and ignore your boundaries for months. Real Shit: They used a thumbs-up reaction instead of a heart emoji. Your threat-detection radar is completely broken.",
        "source_title": "I Sleep / Real Shit Shaq (Twitter / Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/sleeping-shaq",
        "query_used": "sleeping shaq real shit selective outrage meme"
    },

    # 51. Evil Kermit Whisper
    {
        "id": "evil-kermit-whisper",
        "situation": "Listening to the toxic little voice in your head telling you to stir up drama",
        "keywords": ["evil kermit", "intrusive thought", "petty", "stir the pot", "gave in", "retaliate", "petty revenge"],
        "phrases": ["evil voice told me", "knew i should not do it", "intrusive thought won", "listened to my worst impulse"],
        "meme_url": "https://i.imgflip.com/1e7ql7.jpg",
        "verdict": "EVIL KERMIT SURRENDER",
        "critique": "Reasonable You: 'Leave the chat, block the drama, drink chamomile tea.' Hooded Evil Kermit: 'Screenshot the message, post it on your close friends with eye emojis, and start a war.' You obey the hood every single time.",
        "source_title": "Evil Kermit / Hooded Kermit (Twitter)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/evil-kermit",
        "query_used": "evil kermit whispering intrusive thoughts meme"
    },

    # 52. Boardroom Defenestration
    {
        "id": "boardroom-defenestration",
        "situation": "Suggesting simple honesty or accountability and being attacked for 'ruining the vibe'",
        "keywords": ["boardroom", "villain for speaking up", "ruining the vibe", "accountability", "truth hurts", "thrown out window"],
        "phrases": ["called them out and became the villain", "asked for honesty", "ruining the mood", "turned on me"],
        "meme_url": "https://i.imgflip.com/m78d.jpg",
        "verdict": "DEFENESTRATED FOR COMMON SENSE",
        "critique": "The whole friend group: Making excuses for bad behavior. You: 'How about we just tell the truth and stop pretending it's fine?' Everyone: 'Wow, why are you being so toxic and ruining the vibe?!' Standard defenestration.",
        "source_title": "Boardroom Meeting Suggestion (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/boardroom-suggestion",
        "query_used": "boardroom meeting suggestion thrown out window meme"
    },

    # 53. Delusional 0.001% Hope
    {
        "id": "dumber-chance-hope",
        "situation": "Clinging to hopeless odds when someone explicitly told you they don't want you",
        "keywords": ["dumb and dumber", "chance", "emotionally unavailable", "told me not looking", "not ready", "hope they commit"],
        "phrases": ["so you are telling me there is a chance", "said they are not looking for anything", "hoping they change their mind"],
        "meme_url": "https://i.imgflip.com/2fm6x0.jpg",
        "verdict": "DELUSIONAL 0.001% HOPE",
        "critique": "They explicitly stated they are emotionally unavailable, talking to four other people, and moving across the country in two months. You: 'So you're telling me there's a chance!' Have some self-worth and pack your bags.",
        "source_title": "So You're Telling Me There's a Chance (Reddit)",
        "source_platform": "Reddit (r/memes)",
        "source_url": "https://knowyourmeme.com/memes/so-youre-telling-me-theres-a-chance",
        "query_used": "so youre telling me theres a chance meme"
    },

    # 54. Arthur's Clenched Fist
    {
        "id": "arthur-fist-rage",
        "situation": "Suppressing pure homicidal irritation at a passive-aggressive coworker or friend",
        "keywords": ["arthur", "clenched fist", "boiling inside", "passive aggressive", "smiling while screaming", "rage inside"],
        "phrases": ["arthurs fist", "clenching my teeth", "smiling while furious", "passive aggressive coworker", "internal rage"],
        "meme_url": "https://i.imgflip.com/1bip.jpg",
        "verdict": "ARTHUR'S CLENCHED FIST",
        "critique": "Yellow sweater, white knuckles clenched so tight the blood stopped flowing. You're typing 'Sounds great, thanks for the update! :)' in Slack while actively hallucinating flipping your desk through the drywall.",
        "source_title": "Arthur's Fist (Twitter / Tumblr)",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/arthurs-fist",
        "query_used": "arthurs fist clenched yellow sweater anger meme",
        "collection_type": "social"
    },

    # --- MY MEME COLLECTION (Folder Assets) ---
    {
        "id": "monkey-thinking-iced-coffee",
        "collection_type": "my_collection",
        "situation": "Overthinking life choices and rationalizing sweet treats or impulse coping mechanisms",
        "keywords": ["coffee", "croissant", "monkey", "thinking", "impulse", "snack", "treat", "latte", "overthinking", "rationalize", "sweet treat", "spend", "bought"],
        "phrases": ["iced coffee", "sweet treat", "need a treat", "finger on my chin", "thinking about", "sitting here thinking", "almond croissant"],
        "meme_url": "/memes/meme10.jpg",
        "verdict": "OVERTHINKING MONKEY",
        "critique": "You're sitting there with your finger on your chin looking like an ancient philosopher, but all you're really doing is rationalizing spending $14 on an iced coffee and a pastry to soothe 15 minutes of mild inconvenience. Put the wallet away.",
        "source_title": "Monkey Thinking / Iced Coffee Dilemma",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme10.jpg",
        "query_used": "monkey thinking finger on chin iced coffee croissant meme"
    },
    {
        "id": "green-snake-judging-decisions",
        "collection_type": "my_collection",
        "situation": "Making questionable choices while suspicious people watch, fake friends judge, or you judge yourself",
        "keywords": ["snake", "green snake", "judging", "squint", "side eye", "shady", "fake friend", "trusting", "sus", "suspicious", "watching", "judgement"],
        "phrases": ["green snake", "judging me", "side eye", "sus behavior", "fake friends", "shady friend", "staring at me"],
        "meme_url": "/memes/meme7.jpg",
        "verdict": "SNEAKY JUDGING VIPER",
        "critique": "That green snake with stick arms has reviewed your decision history and is giving you the exact squint you deserve. You keep telling private business to people who would trade your loyalty for half a pack of gum. Stop being naive.",
        "source_title": "Green Snake Judging with Stick Arms",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme7.jpg",
        "query_used": "green snake judging stick arms hand on chin meme"
    },
    {
        "id": "run-we-are-in-ohio",
        "collection_type": "my_collection",
        "situation": "Entering a completely cursed, unhinged, chaotic situation and needing to flee immediately",
        "keywords": ["ohio", "run", "peter", "chaos", "bombs", "explosions", "cursed", "toxic environment", "flee", "get out", "disaster zone"],
        "phrases": ["run we are in ohio", "get out of here", "red flag zone", "disaster waiting to happen", "absolute chaos"],
        "meme_url": "/memes/meme1.jpg",
        "verdict": "RUN WE ARE IN OHIO",
        "critique": "Peter Griffin is sprinting for his life from falling explosives, and that should be your exact cardio routine right now. You walked straight into a toxic hazard and you're still debating whether to stay. Run and do not look back.",
        "source_title": "Run We Are In Ohio (Peter Griffin)",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme1.jpg",
        "query_used": "run we are in ohio peter griffin meme"
    },
    {
        "id": "mocking-spongebob-excuses",
        "collection_type": "my_collection",
        "situation": "Repeating ridiculous excuses or childish drama that already failed previously",
        "keywords": ["spongebob", "mocking", "childish", "excuses", "clowning", "again", "repeating", "he promised", "she promised", "they said"],
        "phrases": ["mocking spongebob", "they promised they would change", "maybe this time", "giving them another chance"],
        "meme_url": "/memes/meme2.jpg",
        "verdict": "MOCKING SPONGEBOB",
        "critique": "'BuT tHeY pRoMiSeD tHeY wOuLd ChAnGe!' Do you ever get tired of running the exact same clown script? You already know how this movie ends because you paid full price to watch it blow up three weeks ago.",
        "source_title": "Mocking SpongeBob",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme2.jpg",
        "query_used": "mocking spongebob alternating caps meme"
    },
    {
        "id": "hr-staring-dad-disbelief",
        "collection_type": "my_collection",
        "situation": "Audacious demands, corporate exploitation, or being asked to do absurd favors without compensation",
        "keywords": ["hr", "without pay", "boss", "work", "unpaid", "audacity", "speechless", "disbelief", "favor", "overtime", "salary"],
        "phrases": ["work without pay", "asked me for free", "sheer audacity", "staring in disbelief", "speechless at work"],
        "meme_url": "/memes/meme3.jpg",
        "verdict": "SPEECHLESS DISBELIEF",
        "critique": "They looked you dead in the eye with an audacious demand and actually expected you to smile and comply. The sheer cheek has you staring into the distance like your soul logged out. The word you are looking for is 'No'.",
        "source_title": "Monster House Dad Staring in Disbelief",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme3.jpg",
        "query_used": "hr work without pay dad staring disbelief meme"
    },
    {
        "id": "thanos-gen-z-dread",
        "collection_type": "my_collection",
        "situation": "Late-stage adulting misery, economic burnout, feeling exhausted by the cost of living and responsibilities",
        "keywords": ["gen z", "thanos", "rent", "paycheck", "degree", "economy", "houses", "stress", "stressed", "exhausted", "burnout", "bills"],
        "phrases": ["life of gen z", "cost of living", "rent is half my paycheck", "exhausted from adulting", "everything is expensive"],
        "meme_url": "/memes/meme4.jpeg",
        "verdict": "GEN Z EXISTENTIAL BURNOUT",
        "critique": "Rent is half your paycheck, groceries cost an organ, and older generations are asking why you're not glowing with optimism. Thanos sitting on the farm is your spirit animal. Go take a nap, the economy will still be broken when you wake up.",
        "source_title": "Thanos Life of Gen Z",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme4.jpeg",
        "query_used": "life of gen z thanos farm rent paycheck meme"
    },
    {
        "id": "cringe-button-wheeze",
        "collection_type": "my_collection",
        "situation": "Witnessing or committing terminal cringe, second-hand embarrassment, laughing at absolute absurdity",
        "keywords": ["cringe", "wheeze", "embarrassing", "embarrassed", "second hand", "cringing", "awkward", "uncomfortable", "laughing through pain"],
        "phrases": ["pressed the cringe button", "cringe overload", "second hand embarrassment", "dying of laughter", "pure cringe"],
        "meme_url": "/memes/meme5.jpeg",
        "verdict": "TERMINAL CRINGE BUTTON",
        "critique": "You smashed that cringe button with maximum hydraulic pressure. Everyone in the room physically recoiled. The only dignified solution is to fake your death, delete all accounts, and become a goat farmer in the Alps.",
        "source_title": "Cringe Button & Wheeze",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme5.jpeg",
        "query_used": "cringe button minion wheeze meme"
    },
    {
        "id": "silent-snake-stare",
        "collection_type": "my_collection",
        "situation": "Seeing straight through someone's lie and maintaining unbroken judgment",
        "keywords": ["snake stare", "lying", "caught in 4k", "bullshit", "fake", "deceit", "looking right at you"],
        "phrases": ["i know you are lying", "snake stare", "silent judgment", "caught them lying"],
        "meme_url": "/memes/meme6.jpg",
        "verdict": "SILENT VIPER JUDGMENT",
        "critique": "Look at those narrow reptilian eyes. It knows you're lying, you know you're lying, and the universe knows you're lying. Stop constructing fake narratives to justify bad choices.",
        "source_title": "Green Snake Silent Stare",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme6.jpg",
        "query_used": "green snake narrow eyes stare meme"
    },
    {
        "id": "cat-traumatizing-lore",
        "collection_type": "my_collection",
        "situation": "Trauma-dumping casual emotional lore in the middle of a light conversation then staring blankly",
        "keywords": ["lore", "trauma", "dump", "cat", "stare", "oversharing", "unhinged", "confession", "casual"],
        "phrases": ["traumatizing lore", "trauma dump", "overshared", "staring at them like this", "dropped emotional damage"],
        "meme_url": "/memes/meme8.jpg",
        "verdict": "UNHINGED TRAUMA LORE CAT",
        "critique": "They just asked 'How was your weekend?' and you hit them with four seasons of psychological character development and unresolved childhood baggage. Look at that cat face. Give those civilians some warning next time.",
        "source_title": "Traumatizing Lore Cat",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme8.jpg",
        "query_used": "traumatizing lore cat staring face meme"
    },
    {
        "id": "lost-chihuahua-crisis",
        "collection_type": "my_collection",
        "situation": "Having an existential crisis where you don't even know what you're doing with your life",
        "keywords": ["point", "chihuahua", "lost", "direction", "confused", "quarter life", "crisis", "no idea", "what am i doing", "paralyzed"],
        "phrases": ["dont know the point", "at a point in my life", "have no direction", "what am i doing with my life"],
        "meme_url": "/memes/meme9.jpg",
        "verdict": "POINTLESS BUT POINTING",
        "critique": "'I'm at a point in my life where I don't even know what point I'm at.' Your big ears are pinned back, your eyes are vibrating, and you're staring at the ceiling fan questioning your entire existence. Just pick a direction and start walking.",
        "source_title": "Chihuahua Existential Crisis Point",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme9.jpg",
        "query_used": "chihuahua point in my life dont know the point meme"
    },
    {
        "id": "spiderman-presentation-lecture",
        "collection_type": "my_collection",
        "situation": "Giving an unsolicited lecture, over-explaining petty drama, or typing 10 paragraphs to explain common sense",
        "keywords": ["spiderman", "presentation", "lecture", "explaining", "paragraphs", "essay", "ted talk", "slides"],
        "phrases": ["today we are going to learn", "wrote an essay", "spiderman presentation", "giving a lecture"],
        "meme_url": "/memes/meme11.jpeg",
        "verdict": "UNSOLICITED TED TALK",
        "critique": "You just drafted a 12-slide auditorium presentation about a situation that required a simple two-letter text: 'No.' Nobody enrolled in your lecture series. Save your energy.",
        "source_title": "Spider-Man Lecture on Memes",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme11.jpeg",
        "query_used": "today we are going to learn about memes spiderman presentation"
    },
    {
        "id": "barbie-disheveled-monday",
        "collection_type": "my_collection",
        "situation": "Returning to work or responsibilities completely wrecked after a weekend of endless domestic chores",
        "keywords": ["barbie", "disheveled", "weekend chores", "laundry", "cleaning", "grocery", "exhausted monday", "messy hair", "fried"],
        "phrases": ["refreshing two days", "cleaning and laundry", "wrecked after the weekend", "returning to work looking like", "exhausted after cleaning"],
        "meme_url": "/memes/meme12.jpeg",
        "verdict": "REFRESHED & DESTROYED",
        "critique": "Your 'recharging weekend' was 48 straight hours of folding bedsheets, scrubbing grout, and buying $200 worth of vegetables that will rot in the crisper drawer. You're rolling into Monday looking like Barbie survived a hurricane.",
        "source_title": "Messy Hair Barbie Post-Weekend",
        "source_platform": "My Meme Collection",
        "source_url": "/memes/meme12.jpeg",
        "query_used": "returning to work refreshing two days cleaning barbie messy hair meme"
    },

    # --- TRENDING SOCIAL MEDIA MEMES (Viral 2024-2025 Culture) ---
    {
        "id": "chill-guy-trending",
        "collection_type": "trending",
        "situation": "Pretending to be a totally unbothered 'chill guy' while your entire life is actively burning down",
        "keywords": ["chill guy", "chill", "unbothered", "not caring", "fine", "cool", "dog with coat", "hands in pockets", "acting cool"],
        "phrases": ["im just a chill guy", "just a chill guy", "totally unbothered", "im chill about it", "does not bother me"],
        "meme_url": "https://i.imgflip.com/9a5z9i.jpg",
        "verdict": "FAKE CHILL GUY",
        "critique": "You are posting 'I'm just a chill guy who doesn't care about anything' while your heart rate is 145 bpm and you've rewritten the same unsent message 17 times. You are NOT chill. You are vibrating with anxiety in a fleece jacket.",
        "source_title": "Chill Guy (Viral TikTok / Twitter)",
        "source_platform": "TikTok / Twitter",
        "source_url": "https://knowyourmeme.com/memes/chill-guy",
        "query_used": "chill guy viral meme dog hands in pocket"
    },
    {
        "id": "aura-loss-negative",
        "collection_type": "trending",
        "situation": "Humiliating yourself in public, fumbling an interaction, or doing desperate acts that tank your dignity",
        "keywords": ["aura", "aura points", "-1000", "-100000", "fumble", "fumbled", "embarrassed", "tripped", "stumbled", "desperate"],
        "phrases": ["lost aura", "minus aura", "aura points", "lost 100000 aura", "fumbled completely"],
        "meme_url": "https://i.imgflip.com/8pmli5.jpg",
        "verdict": "-1,000,000 AURA LOSS",
        "critique": "You just lost more aura in 15 seconds than a villain falling off a bridge in the anime pilot. The ground gave way and your dignity plummeted into the earth's mantle. There is no recovery statement. Take the negative balance and go silent.",
        "source_title": "-100,000 Aura Fall (TikTok / IG Reels)",
        "source_platform": "TikTok / Instagram",
        "source_url": "https://knowyourmeme.com/memes/aura-points",
        "query_used": "lost aura points minus aura anime meme"
    },
    {
        "id": "bombastic-side-eye-dog",
        "collection_type": "trending",
        "situation": "Observing shady, suspicious, or downright offensive behavior from someone you know is lying",
        "keywords": ["bombastic", "side eye", "criminal offensive", "dog side eye", "shady", "suspicious", "sus", "caught"],
        "phrases": ["bombastic side eye", "criminal offensive side eye", "giving side eye", "suspicious story"],
        "meme_url": "https://i.imgflip.com/7ecqsp.jpg",
        "verdict": "BOMBASTIC SIDE EYE",
        "critique": "That entire explanation smells like a damp dumpster behind a seafood restaurant. Why are you entertaining their transparent lies? Bombastic side eye, criminal offensive side eye.",
        "source_title": "Bombastic Side Eye Dog",
        "source_platform": "TikTok / Twitter",
        "source_url": "https://knowyourmeme.com/memes/bombastic-side-eye",
        "query_used": "bombastic side eye dog criminal offensive meme"
    },
    {
        "id": "let-him-cook-disaster",
        "collection_type": "trending",
        "situation": "Letting someone explain or cook, only for them to burn down everything in sight",
        "keywords": ["cook", "let him cook", "let them cook", "never cook again", "burned", "disaster chef", "terrible advice"],
        "phrases": ["let him cook", "never let him cook again", "let them explain", "cooking disaster"],
        "meme_url": "https://i.imgflip.com/7vj27c.jpg",
        "verdict": "NEVER LET HIM COOK AGAIN",
        "critique": "We told you to let them cook, and they managed to set off every smoke detector in a five-mile radius. Revoke their apron, confiscate the stove, and permanently bar them from entering the kitchen.",
        "source_title": "Let Him Cook / Never Cook Again",
        "source_platform": "Twitter / X",
        "source_url": "https://knowyourmeme.com/memes/let-him-cook",
        "query_used": "let him cook never cook again burning stove meme"
    },
    {
        "id": "gigachad-stand-on-business",
        "collection_type": "trending",
        "situation": "Realizing you need to stop begging, stand on business, hit the gym, and eliminate nonsense from your life",
        "keywords": ["gigachad", "chad", "stand on business", "gym", "block them", "self respect", "alpha", "jawline", "no more games"],
        "phrases": ["stand on business", "hit the gym", "gigachad", "cut them off for good", "choosing self respect"],
        "meme_url": "https://i.imgflip.com/5c7lwq.jpg",
        "verdict": "STAND ON BUSINESS",
        "critique": "A true legend does not check read receipts, send quadruple follow-ups, or seek validation from flakey amateurs. Block the number, hit the weights, drink a gallon of water, and never look back.",
        "source_title": "GigaChad Stand On Business",
        "source_platform": "Reddit (r/chadposting)",
        "source_url": "https://knowyourmeme.com/memes/gigachad",
        "query_used": "gigachad stand on business self respect meme"
    },
    {
        "id": "distracted-boyfriend-toxicity",
        "collection_type": "trending",
        "situation": "Walking away from peace and stability to chase red flags and emotional chaos",
        "keywords": ["distracted", "boyfriend", "red flag", "toxic", "choosing drama", "ignoring good", "walking away"],
        "phrases": ["distracted boyfriend", "chasing red flags", "ignoring peace", "choosing chaos"],
        "meme_url": "https://i.imgflip.com/1ur9b0.jpg",
        "verdict": "ADDICTED TO CHAOS",
        "critique": "Peace, good sleep, and emotional stability were holding your hand, and you turned your whole torso around to leer at a walking biohazard. You don't want peace; you want the drama.",
        "source_title": "Distracted Boyfriend",
        "source_platform": "Twitter / Reddit",
        "source_url": "https://knowyourmeme.com/memes/distracted-boyfriend",
        "query_used": "distracted boyfriend meme chasing red flags"
    },
    {
        "id": "disaster-girl-smirk",
        "collection_type": "trending",
        "situation": "Instigating massive drama or burning bridges and smiling serenely while everything crumbles",
        "keywords": ["disaster girl", "fire", "burning", "drama", "instigator", "burned bridges", "smiling", "chaos"],
        "phrases": ["disaster girl", "watching it burn", "burned that bridge", "instigated the drama"],
        "meme_url": "https://i.imgflip.com/23ls.jpg",
        "verdict": "DISASTER INSTIGATOR",
        "critique": "You lit the fuse, threw the match into the gasoline, and now you're posing with a pleasant smirk asking why everyone is so sensitive. Stop pretending you were an innocent bystander.",
        "source_title": "Disaster Girl (House Fire)",
        "source_platform": "Know Your Meme",
        "source_url": "https://knowyourmeme.com/memes/disaster-girl",
        "query_used": "disaster girl house burning smirk meme"
    },
    {
        "id": "they-dont-know-party-wallflower",
        "collection_type": "trending",
        "situation": "Forcing yourself into an awkward party or social event and immediately regretting leaving your bed",
        "keywords": ["they dont know", "party", "corner", "wallflower", "regret going", "awkward", "lonely at party"],
        "phrases": ["they don't know", "standing in the corner", "regret coming to this party", "wish i stayed home"],
        "meme_url": "https://i.imgflip.com/43a45p.jpg",
        "verdict": "UNCOMFORTABLE WALLFLOWER",
        "critique": "You left your comfortable bed to attend a function where you don't even like the playlist, clutching a lukewarm drink in the corner. Go home. Your bed is not going to judge you.",
        "source_title": "They Don't Know (I Wish I Was At Home)",
        "source_platform": "Reddit (r/me_irl)",
        "source_url": "https://knowyourmeme.com/memes/i-wish-i-was-at-home-they-dont-know",
        "query_used": "they dont know party corner wallflower meme",
        "category": "trending"
    },

    # --- SPONGEBOB MEMES ---
    {
        "id": "spongebob-imma-head-out",
        "category": "spongebob",
        "collection_type": "spongebob",
        "situation": "Recognizing an awkward, cursed situation or toxic conversation and exiting immediately",
        "keywords": ["head out", "leaving", "awkward exit", "chair", "spongebob leaving", "nope", "getting out of here", "uncomfortable situation"],
        "phrases": ["ight imma head out", "imma head out", "getting out of here", "saw myself out", "time to leave"],
        "meme_url": "https://i.imgflip.com/392x58.jpg",
        "verdict": "IGHT IMMA HEAD OUT",
        "critique": "The second the conversation turned weird, your instinct to stand up from that armchair and vanish into the ocean was 100% correct. Don't linger. Save yourself the second-hand embarrassment.",
        "source_title": "Ight Imma Head Out SpongeBob",
        "source_platform": "SpongeBob SquarePants",
        "source_url": "https://knowyourmeme.com/memes/ight-imma-head-out",
        "query_used": "ight imma head out spongebob chair exit meme"
    },
    {
        "id": "spongebob-burning-paper",
        "category": "spongebob",
        "collection_type": "spongebob",
        "situation": "Throwing away common sense, solid advice, or your own promises into the garbage fire",
        "keywords": ["burning", "fire", "advice", "ignoring advice", "threw away", "paper in fire", "waste", "rules"],
        "phrases": ["threw the advice away", "burning paper", "ignored every warning", "did it anyway"],
        "meme_url": "https://i.imgflip.com/2wqy8r.jpg",
        "verdict": "THROWING ADVICE IN THE FIRE",
        "critique": "Your friends gave you pristine, bulletproof advice and you literally dropped it straight into the campfire like SpongeBob in Bikini Bottom. Stop asking people for advice when you're just going to do the dumbest thing possible anyway.",
        "source_title": "SpongeBob Burning Paper in Fire",
        "source_platform": "SpongeBob SquarePants",
        "source_url": "https://knowyourmeme.com/memes/spongebob-burning-paper",
        "query_used": "spongebob throws paper in fire meme"
    },
    {
        "id": "handsome-squidward-delusion",
        "category": "spongebob",
        "collection_type": "spongebob",
        "situation": "Acting like a majestic enlightened philosopher when you're just being dramatic and pretentious",
        "keywords": ["handsome squidward", "jawline", "pretentious", "majestic", "dramatic", "acting deep", "philosopher"],
        "phrases": ["handsome squidward", "acting like a philosopher", "pretending to be deep", "dramatic entrance"],
        "meme_url": "https://i.imgflip.com/15h77m.jpg",
        "verdict": "HANDSOME SQUIDWARD DELUSION",
        "critique": "You're posing like Handsome Squidward with an exaggerated jawline acting like your 2 AM thoughts are Pulitzer material. You had a minor disagreement over laundry. Relax, Shakespeare.",
        "source_title": "Handsome Squidward",
        "source_platform": "SpongeBob SquarePants",
        "source_url": "https://knowyourmeme.com/memes/handsome-squidward",
        "query_used": "handsome squidward jawline dramatic pose meme"
    },
    {
        "id": "patrick-star-inner-machinations",
        "category": "spongebob",
        "collection_type": "spongebob",
        "situation": "Overthinking a problem until your brain produces a spilled carton of milk",
        "keywords": ["patrick", "enigma", "milk", "no thoughts", "empty head", "brain empty", "overthinking nothing"],
        "phrases": ["inner machinations of my mind", "brain empty", "head empty", "thinking so hard my head hurts"],
        "meme_url": "https://i.imgflip.com/26103j.jpg",
        "verdict": "INNER MACHINATIONS ARE AN ENIGMA",
        "critique": "'The inner machinations of my mind are an enigma.' *Carton of milk spills in slow motion.* That is your entire cognitive process right now. You spent three hours analyzing a one-word text.",
        "source_title": "Patrick Star Milk Carton",
        "source_platform": "SpongeBob SquarePants",
        "source_url": "https://knowyourmeme.com/memes/the-inner-machinations-of-my-mind-are-an-enigma",
        "query_used": "patrick star milk spilling inner machinations meme"
    },

    # --- ANIME MEMES ---
    {
        "id": "death-note-light-manic-laugh",
        "category": "anime",
        "collection_type": "anime",
        "situation": "Thinking you hatched a 200 IQ mastermind plan when you're walking into an obvious disaster",
        "keywords": ["death note", "light yagami", "mastermind", "evil laugh", "revenge", "plan", "genius", "scheming"],
        "phrases": ["evil plan", "light yagami laugh", "all according to keikaku", "they will pay", "calculated revenge"],
        "meme_url": "https://i.imgflip.com/2wif8m.jpg",
        "verdict": "DELUSIONAL ANIME MASTERMIND",
        "critique": "You are writing a five-step revenge scheme like Light Yagami laughing maniacally with a fountain pen. In reality, they forgot who you were three days ago. Close the Death Note and go touch some grass.",
        "source_title": "Light Yagami Laugh (Death Note)",
        "source_platform": "Anime (Death Note)",
        "source_url": "https://knowyourmeme.com/memes/light-yagami-laugh",
        "query_used": "light yagami manic laugh death note meme"
    },
    {
        "id": "sad-naruto-swing-alone",
        "category": "anime",
        "collection_type": "anime",
        "situation": "Throwing yourself an exaggerated pity party and sitting alone waiting for someone to rescue you",
        "keywords": ["naruto", "swing", "sad", "alone", "pity party", "nobody loves me", "lonely", "victim"],
        "phrases": ["naruto swing", "sitting on the swing", "nobody cares about me", "all alone in the world"],
        "meme_url": "https://i.imgflip.com/4qepd0.jpg",
        "verdict": "SAD NARUTO ON THE SWING",
        "critique": "The sad flute music is playing and you're swinging alone like 8-year-old Naruto outside the Academy. Stop waiting for a whole village to apologize to you. Get off the swing and take responsibility.",
        "source_title": "Sad Naruto on the Swing",
        "source_platform": "Anime (Naruto)",
        "source_url": "https://knowyourmeme.com/memes/naruto-on-a-swing",
        "query_used": "sad naruto swing alone flute meme"
    },
    {
        "id": "jojo-approaching-me",
        "category": "anime",
        "collection_type": "anime",
        "situation": "Walking directly toward conflict or toxic people you have zero chance of defeating",
        "keywords": ["jojo", "dio", "jotaro", "approaching", "walking towards", "picking a fight", "confrontation"],
        "phrases": ["oh you're approaching me", "approaching me", "walking right into it", "jojo walk"],
        "meme_url": "https://i.imgflip.com/39flw2.jpg",
        "verdict": "OH? YOU'RE APPROACHING ME?",
        "critique": "Instead of running away, you're walking right toward them with dramatic JoJo posing. You are not Jotaro, and they are about to hit you with emotional road-roller. Turn around.",
        "source_title": "Oh? You're Approaching Me? (JoJo)",
        "source_platform": "Anime (JoJo's Bizarre Adventure)",
        "source_url": "https://knowyourmeme.com/memes/oh-youre-approaching-me-jojo",
        "query_used": "oh youre approaching me jojo dio meme"
    },
    {
        "id": "is-this-a-pigeon-butterfly",
        "category": "anime",
        "collection_type": "anime",
        "situation": "Confusing the absolute bare minimum effort or mild politeness with unconditional love",
        "keywords": ["pigeon", "butterfly", "is this", "bare minimum", "confused", "reading into it", "polite"],
        "phrases": ["is this a pigeon", "bare minimum", "they held the door", "confused kindness for love"],
        "meme_url": "https://i.imgflip.com/2cjr7j.jpg",
        "verdict": "IS THIS A PIGEON?",
        "critique": "They said 'Hey, thanks!' and you're pointing at a butterfly asking 'Is this my soulmate?' It was basic social etiquette from a cashier. Stop drafting wedding vows in your Notes app.",
        "source_title": "Is This a Pigeon? (Anime Butterfly)",
        "source_platform": "Anime (The Brave Fighter of Sun Fighbird)",
        "source_url": "https://knowyourmeme.com/memes/is-this-a-pigeon",
        "query_used": "is this a pigeon anime butterfly meme"
    },

    # --- MOVIES & HOLLYWOOD MEMES ---
    {
        "id": "leo-pointing-once-upon-time",
        "category": "hollywood",
        "collection_type": "hollywood",
        "situation": "Spotting the exact red flag or betrayal you were warned about weeks ago",
        "keywords": ["leo", "pointing", "leonardo dicaprio", "spotted", "red flag", "called it", "knew it", "beer"],
        "phrases": ["pointing at the screen", "called it from day one", "knew this would happen", "spotted the red flag"],
        "meme_url": "https://i.imgflip.com/3vzejg.jpg",
        "verdict": "LEO POINTING AT THE SCREEN",
        "critique": "You're sitting on the sofa with a beer pointing at the screen shouting 'LOOK! THAT'S THE RED FLAG!' You knew they were toxic in chapter 1 and you still bought tickets for the sequel.",
        "source_title": "Leonardo DiCaprio Pointing (Hollywood)",
        "source_platform": "Hollywood (Once Upon a Time in Hollywood)",
        "source_url": "https://knowyourmeme.com/memes/leonardo-dicaprio-pointing",
        "query_used": "leonardo dicaprio pointing tv once upon time hollywood meme"
    },
    {
        "id": "leo-laughing-django",
        "category": "hollywood",
        "collection_type": "hollywood",
        "situation": "Smugly laughing at someone who tried to play you and failed miserably",
        "keywords": ["leo laughing", "django", "calvin candie", "laughing with drink", "smug", "played themselves", "exposed"],
        "phrases": ["laughing at their excuse", "played themselves", "leo laughing with drink", "smug satisfaction"],
        "meme_url": "https://i.imgflip.com/4acd7j.jpg",
        "verdict": "DJANGO LEO LAUGH",
        "critique": "Holding the champagne glass, head thrown back laughing at the most pathetic lie ever whispered. They really thought you wouldn't find out. Pour another drink and let them squirm.",
        "source_title": "Leonardo DiCaprio Laughing (Django Unchained)",
        "source_platform": "Hollywood (Django Unchained)",
        "source_url": "https://knowyourmeme.com/memes/leonardo-dicaprio-laughing-django",
        "query_used": "leonardo dicaprio laughing drink django meme"
    },
    {
        "id": "patrick-bateman-headphones-walk",
        "category": "hollywood",
        "collection_type": "hollywood",
        "situation": "Pretending you're a cold, mysterious lone wolf when you're just terrible at social interaction",
        "keywords": ["bateman", "american psycho", "headphones", "suit", "sigma", "cold", "lone wolf", "walk"],
        "phrases": ["patrick bateman walk", "headphones on ignoring world", "sigma male", "cold and detached"],
        "meme_url": "https://i.imgflip.com/6j8x61.jpg",
        "verdict": "PATRICK BATEMAN SIGMA WALK",
        "critique": "You put in your AirPods, tighten your coat, and do the Patrick Bateman hallway strut thinking you look formidable. You're not an enigmatic corporate predator; you just have social anxiety. Say hi to people.",
        "source_title": "Patrick Bateman Walking with Headphones",
        "source_platform": "Hollywood (American Psycho)",
        "source_url": "https://knowyourmeme.com/memes/patrick-bateman-walking",
        "query_used": "patrick bateman walk headphones american psycho meme"
    },
    {
        "id": "godfather-massacred-my-boy",
        "category": "hollywood",
        "collection_type": "hollywood",
        "situation": "Returning to a project, relationship, or plan only to find it completely dismantled and ruined",
        "keywords": ["godfather", "massacred", "ruined", "look how they", "destroyed", "vito corleone", "marlon brando"],
        "phrases": ["look how they massacred my boy", "ruined my hard work", "everything is ruined", "look what they did"],
        "meme_url": "https://i.imgflip.com/241ycf.jpg",
        "verdict": "LOOK HOW THEY MASSACRED MY BOY",
        "critique": "'Look how they massacred my boy.' You stepped away for 45 minutes and they managed to demolish your entire week's effort. Don't weep over the wreckage; fire the consultants.",
        "source_title": "Look How They Massacred My Boy (The Godfather)",
        "source_platform": "Hollywood (The Godfather)",
        "source_url": "https://knowyourmeme.com/memes/look-how-they-massacred-my-boy",
        "query_used": "look how they massacred my boy godfather meme"
    },

    # --- TOLLYWOOD & INDIAN CINEMA MEMES ---
    {
        "id": "brahmanandam-deep-thinking-scratch",
        "category": "tollywood",
        "collection_type": "tollywood",
        "situation": "Baffled by completely illogical excuses or trying to comprehend insane drama",
        "keywords": ["brahmanandam", "tollywood", "scratching head", "telugu", "dookudu", "confused", "thinking hard", "baffled"],
        "phrases": ["brahmanandam thinking", "scratching my head", "what kind of logic is this", "enti idi", "tollywood comedy"],
        "meme_url": "/memes/meme10.jpg",
        "verdict": "BRAHMANANDAM INTENSE SCRATCHING",
        "critique": "You are sitting here scratching your forehead like King of Comedy Brahmanandam trying to decipher alien logic. There is no hidden wisdom in their excuse. It's just plain nonsense. Stop stressing your brain cells.",
        "source_title": "Brahmanandam Deep Confusion (Tollywood)",
        "source_platform": "Tollywood (Telugu Cinema)",
        "source_url": "https://knowyourmeme.com",
        "query_used": "brahmanandam thinking scratch head telugu meme"
    },
    {
        "id": "brahmanandam-enti-comedy-aa",
        "category": "tollywood",
        "collection_type": "tollywood",
        "situation": "Someone blatantly disrespecting you and expecting you to laugh it off as a joke",
        "keywords": ["enti comedy aa", "brahmanandam", "joke", "disrespect", "acting funny", "laugh it off", "tollywood"],
        "phrases": ["enti comedy aa", "is this comedy to you", "treating me like a joke", "not laughing"],
        "meme_url": "/memes/meme2.jpg",
        "verdict": "ENTI COMEDY AA?!",
        "critique": "'Enti comedy aa?' They insulted you in front of five mutual acquaintances and added 'just kidding bro!' like it covers the damage. You are not their stand-up comedy prop. Put your foot down.",
        "source_title": "Brahmanandam 'Enti Comedy Aa?'",
        "source_platform": "Tollywood (Telugu Cinema)",
        "source_url": "https://knowyourmeme.com",
        "query_used": "brahmanandam enti comedy aa shocked dialogue meme"
    },
    {
        "id": "pushpa-thaggedhe-le-ego",
        "category": "tollywood",
        "collection_type": "tollywood",
        "situation": "Refusing to apologize or back down even though you are 100% in the wrong due to pure stubbornness",
        "keywords": ["pushpa", "thaggedhe le", "allu arjun", "stubborn", "ego", "refuse to apologize", "jhukega nahi"],
        "phrases": ["thaggedhe le", "jhukega nahi", "pushpa attitude", "refuse to back down", "too proud to say sorry"],
        "meme_url": "/memes/meme7.jpg",
        "verdict": "THAGGEDHE LE EGO CRASH",
        "critique": "You hit the chin with the Pushpa beard-swipe whispering 'Thaggedhe Le!' while standing in the middle of a sinkhole you dug yourself. Having stubborn pride when you're clearly wrong is not heroic; it's expensive. Apologize.",
        "source_title": "Pushpa Thaggedhe Le (Allu Arjun)",
        "source_platform": "Tollywood (Pushpa)",
        "source_url": "https://knowyourmeme.com",
        "query_used": "allu arjun pushpa thaggedhe le beard swipe meme"
    },
    {
        "id": "vennela-kishore-sarcasm",
        "category": "tollywood",
        "collection_type": "tollywood",
        "situation": "Delivering deadpan sarcasm to someone asking for absurd favors or drama",
        "keywords": ["vennela kishore", "sarcasm", "deadpan", "tollywood", "mari intha direct ga", "side eye", "disbelief"],
        "phrases": ["vennela kishore sarcasm", "deadpan reaction", "mari intha direct ga adigithe", "dry sarcasm"],
        "meme_url": "/memes/meme6.jpg",
        "verdict": "VENNELA KISHORE DEADPAN SARCASM",
        "critique": "'Mari intha direct ga unte ela?' The deadpan side-eye you gave them was so sharp it could cut diamonds. Keep that exact energy. Don't soften your boundaries just because someone acts surprised.",
        "source_title": "Vennela Kishore Deadpan Sarcasm",
        "source_platform": "Tollywood (Telugu Cinema)",
        "source_url": "https://knowyourmeme.com",
        "query_used": "vennela kishore deadpan sarcastic expression meme"
    }
]


class OnlineMemeService:
    """
    Situational Social Media & Google Meme Engine.
    Matches exact situations and delivers hard, blunt, non-therapeutic reality-check roasts.
    """

    def __init__(self):
        self.catalog = SITUATION_MEME_CATALOG

    def score_situation(self, entry_text: str, situation: Dict[str, Any]) -> int:
        """
        Calculates how closely an entry matches a specific social media situation.
        Multi-word phrases give high weight, keywords give regular weight.
        """
        text = entry_text.lower()
        score = 0

        # Exact multi-word situational phrases (high confidence match)
        for phrase in situation.get("phrases", []):
            if phrase.lower() in text:
                score += 5

        # Individual keyword matches
        for kw in situation.get("keywords", []):
            if kw.lower() in text:
                score += 2

        return score

    def find_best_online_meme(self, text: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Finds the specific social media situation that best matches the journal entry.
        Guarantees distinct, situation-specific matching and eliminates repetitive defaults.
        """
        combined = f"{title or ''} {text}".strip()

        scored = []
        for item in self.catalog:
            s = self.score_situation(combined, item)
            if s > 0:
                scored.append((s, item))

        if scored:
            # Sort by score descending
            scored.sort(key=lambda x: x[0], reverse=True)
            top_score = scored[0][0]
            # If multiple items tie for top score, use a deterministic hash of the text so
            # the same entry always gets the same meme, but different entries vary
            top_candidates = [item for score, item in scored if score >= top_score * 0.8]
            
            # Deterministic selection based on content hash for stable, diverse results
            h = int(hashlib.md5(combined.encode("utf-8")).hexdigest(), 16)
            chosen = top_candidates[h % len(top_candidates)]
            return chosen

        # If no explicit keyword match, pick deterministically based on hash of text
        # across the full catalog to avoid always returning the first item
        h = int(hashlib.md5(combined.encode("utf-8")).hexdigest(), 16)
        return self.catalog[h % len(self.catalog)]

    def evaluate(self, text: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluates a journal entry and returns a situation-specific meme critique with hard criticism.
        """
        meme = self.find_best_online_meme(text, title)

        return {
            "meme_url": meme["meme_url"],
            "verdict": meme["verdict"],
            "critique": meme["critique"],
            "source_title": meme.get("source_title", "Viral Meme"),
            "source_platform": meme.get("source_platform", "Social Media"),
            "source_url": meme.get("source_url", "https://knowyourmeme.com"),
            "query_used": meme.get("query_used", f"{meme.get('situation', 'relatable')} meme"),
            "situation": meme.get("situation", "Real-world dilemma"),
            "meme_file": meme["meme_url"],
            "category": meme.get("category", meme.get("collection_type", "social")),
            "collection_type": meme.get("collection_type", meme.get("category", "social"))
        }

    def shuffle(self, text: str, current_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Cycles to an alternative relevant meme from social media for this entry.
        """
        combined = text.strip()
        scored = []
        for item in self.catalog:
            s = self.score_situation(combined, item)
            if item["meme_url"] != current_url:
                scored.append((s, item))

        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            # Pick from top half of matches or random from pool
            top_candidates = [item for s, item in scored[:4]]
            picked = random.choice(top_candidates)
        else:
            candidates = [m for m in self.catalog if m["meme_url"] != current_url] or self.catalog
            picked = random.choice(candidates)

        return {
            "meme_url": picked["meme_url"],
            "verdict": picked["verdict"],
            "critique": picked["critique"],
            "source_title": picked.get("source_title", "Viral Meme"),
            "source_platform": picked.get("source_platform", "Social Media"),
            "source_url": picked.get("source_url", "https://knowyourmeme.com"),
            "query_used": picked.get("query_used", f"{picked.get('situation', 'relatable')} meme"),
            "situation": picked.get("situation", "Real-world dilemma"),
            "meme_file": picked["meme_url"],
            "category": picked.get("category", picked.get("collection_type", "social")),
            "collection_type": picked.get("collection_type", picked.get("category", "social"))
        }

    def search_online_memes(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches memes across social media and Google by situation, verdict, or keywords.
        """
        q_lower = query.lower()
        results = []

        for m in self.catalog:
            searchable = f"{m.get('situation', '')} {m.get('source_title', '')} {m.get('verdict', '')} {m.get('critique', '')} {' '.join(m.get('keywords', []))}".lower()
            if any(term in searchable for term in q_lower.split()):
                results.append(m)

        if not results:
            results = self.catalog[:8]

        return results


online_meme_service = OnlineMemeService()
