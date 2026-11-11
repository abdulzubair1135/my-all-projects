with open('auto_factory_batch.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """def refill_viral_topics_if_needed():
    topics = get_remaining_topics()
    if len(topics) >= 4:
        return

    log("Topics list low! DeepSeek se naye topics mangwaye ja rahe hain...", "[REFILL]")
    prompt = (
        "Give me 10 hilarious, highly relatable conversational banter topics between a Boy and a Girl for 2D stickman animations (e.g. who eats more food, late replies, driving directions, shopping, packing luggage, paying restaurant bill). "
        '(topics like college attendance, late night hunger, friend asking for money, job interview viva panic, gym day 1). '
        'Strictly output a single raw JSON array of strings only. Example: ["topic 1", "topic 2"]'
    )

    try:
        import direct_deepseek
        raw_text = direct_deepseek.ask_deepseek(prompt, max_wait_sec=60)
        match = re.search(r'\\[.*\\]', raw_text, re.DOTALL)
        if match:
            new_topics = json.loads(match.group(0))
            with open(TOPICS_FILE, "a", encoding="utf-8") as f:
                for item in new_topics:
                    clean_item = re.sub(r'^\\d+[\\.\\-\\s]+', '', str(item)).strip()
                    if clean_item:
                        f.write(f"{clean_item}\\n")
            log("10 naye viral topics topics.txt me add ho gaye!", "[SUCCESS]")
    except Exception as e:
        log(f"Auto-refill skip: {e}", "[WARN]")"""

replacement = """VIRAL_TOPICS_RESERVOIR = [
    "Group project where only 1 guy does all the work",
    "Trying to secretly look at the topper exam sheet",
    "When mom cleans the room and everything disappears into thin air",
    "Father reacting to AC temperature set to 18 degrees",
    "Saying 'Bas 5 minute mein uth raha hoon' and sleeping 3 hours",
    "Hostel mess Sunday paneer mystery",
    "When guest relative tries to secretly give 500 Rs note at the door",
    "Walking past street dogs at night pretending to be fearless",
    "Watching horror movie alone vs hearing utensil drop in kitchen",
    "Online shopping delivery boy calling 15 times for house address",
    "Going to barber shop and coming out with completely different hairstyle",
    "Rehearsing what to say on phone call for 10 minutes before dialing",
    "Pretending to study intensely when father enters the room",
    "Trying to open chips packet silently at 2 AM without waking anyone",
    "When teacher says 'Form a group of two' and you look at your best friend",
    "Splitting restaurant bill when one person ordered dry fruit shake",
    "Buying gym membership on Jan 1st vs never visiting after Jan 3rd",
    "Asking friend to wake you up at 6 AM and both wake up at 12 PM"
]

def refill_viral_topics_if_needed():
    topics = get_remaining_topics()
    if len(topics) >= 4:
        return

    log("Topics list low! Naye viral topics refill kiye ja rahe hain...", "[REFILL]")
    prompt = (
        "Give me 10 hilarious, highly relatable conversational banter topics between a Boy and a Girl for 2D stickman animations (e.g. who eats more food, late replies, driving directions, shopping, packing luggage, paying restaurant bill). "
        'Strictly output a single raw JSON array of strings only. Example: ["topic 1", "topic 2"]'
    )

    added = False
    try:
        import direct_deepseek
        raw_text = direct_deepseek.ask_deepseek(prompt, max_wait_sec=45)
        match = re.search(r'\\[.*\\]', raw_text, re.DOTALL)
        if match:
            new_topics = json.loads(match.group(0))
            with open(TOPICS_FILE, "a", encoding="utf-8") as f:
                for item in new_topics:
                    clean_item = re.sub(r'^\\d+[\\.\\-\\s]+', '', str(item)).strip()
                    if clean_item and clean_item not in topics:
                        f.write(f"{clean_item}\\n")
            log("10 naye viral topics DeepSeek se topics.txt me add ho gaye!", "[SUCCESS]")
            added = True
    except Exception as e:
        log(f"DeepSeek online refill note ({e}) - using viral reservoir pool", "[INFO]")

    if not added:
        import random
        pool = [t for t in VIRAL_TOPICS_RESERVOIR if t not in topics]
        selected = random.sample(pool, min(10, len(pool)))
        with open(TOPICS_FILE, "a", encoding="utf-8") as f:
            for item in selected:
                f.write(f"{item}\\n")
        log(f"{len(selected)} naye viral topics reservoir se topics.txt me add ho gaye! Queue kabhi empty nahi hogi!", "[SUCCESS]")"""

norm_text = text.replace('\r\n', '\n')
norm_target = target.replace('\r\n', '\n')

if norm_target in norm_text:
    new_text = norm_text.replace(norm_target, replacement)
    with open('auto_factory_batch.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESS: auto_factory_batch.py updated with immortal topic reservoir!")
else:
    print("FAILED: Target not matched")
