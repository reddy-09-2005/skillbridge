/* =========================================================
   SKILLBRIDGE VOICE BOT
   Simple assistant using the browser's built-in Web Speech
   API. Treats any typed/spoken text as a job title by
   default and looks up skill recommendations for it.
   Speaks replies using a male-sounding voice when available.
========================================================= */

(function () {

    const SpeechRecognitionAPI =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    const micBtn = document.getElementById("voicebot-mic-btn");
    const textInput = document.getElementById("voicebot-text-input");
    const sendBtn = document.getElementById("voicebot-send-btn");
    const log = document.getElementById("voicebot-log");

    if (!micBtn || !log) {
        return;
    }

    let cachedVoices = [];

    function loadVoices() {
        cachedVoices = window.speechSynthesis
            ? window.speechSynthesis.getVoices()
            : [];
    }

    loadVoices();

    if (window.speechSynthesis) {
        window.speechSynthesis.addEventListener("voiceschanged", loadVoices);
    }

    function pickMaleVoice() {

        if (!cachedVoices.length) {
            return null;
        }

        const maleNameHints = [
            "male", "david", "mark", "james", "guy",
            "daniel", "george", "alex", "fred", "ryan"
        ];

        const englishVoices =
            cachedVoices.filter(v => v.lang && v.lang.toLowerCase().startsWith("en"));

        const pool = englishVoices.length ? englishVoices : cachedVoices;

        const match = pool.find(v =>
            maleNameHints.some(hint => v.name.toLowerCase().includes(hint))
        );

        return match || null;
    }

    function speak(text) {

        if (!window.speechSynthesis) {
            return;
        }

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1;
        utterance.pitch = 0.9;

        const maleVoice = pickMaleVoice();

        if (maleVoice) {
            utterance.voice = maleVoice;
        }

        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
    }

    function addMessage(sender, text) {

        const el = document.createElement("div");
        el.className = `voicebot-msg voicebot-${sender}`;
        el.textContent = text;
        log.appendChild(el);
        log.scrollTop = log.scrollHeight;
    }

    async function handleCommand(text) {

        addMessage("user", text);

        const lower = text.toLowerCase().trim();

        // Command: help
        if (lower === "help" || lower.includes("what can you do")) {

            const reply =
                "Just say or type any job title — like cloud engineer, data analyst, " +
                "or product manager — and I'll tell you what skills to learn.";

            addMessage("bot", reply);
            speak(reply);
            return;
        }

        // Strip common filler phrases if present, but don't require them
        const role =
            lower
                .replace(/^(recommend skills for|what should i learn for|skills for|show me skills for)\s*/i, "")
                .trim();

        if (!role) {

            const reply = "Tell me a job title, like cloud engineer or data analyst.";
            addMessage("bot", reply);
            speak(reply);
            return;
        }

        addMessage("bot", `Looking up skills for ${role}...`);

        try {

            const data = await SkillBridgeAPI.getSkillRecommendations(role);

            if (data.error) {
                addMessage("bot", data.error);
                speak(data.error);
                return;
            }

            const missing =
                data.recommended_skills.map(s => s.skill).slice(0, 5).join(", ");

            const reply =
                `For ${role}, based on ${data.based_on_postings} current postings, ` +
                `you have a ${data.match_percentage} percent match. ` +
                (missing
                    ? `You should focus on learning: ${missing}.`
                    : `You already match every skill found.`);

            addMessage("bot", reply);
            speak(reply);

        } catch (error) {

            const msg = "Sorry, I could not fetch recommendations right now.";
            addMessage("bot", msg);
            speak(msg);
        }
    }


    // Text input fallback (always available)
    if (sendBtn && textInput) {

        sendBtn.addEventListener("click", () => {

            const value = textInput.value.trim();

            if (!value) {
                return;
            }

            handleCommand(value);
            textInput.value = "";
        });

        textInput.addEventListener("keydown", event => {

            if (event.key === "Enter") {
                sendBtn.click();
            }
        });
    }


    // Voice input (Chrome/Edge only)
    if (SpeechRecognitionAPI) {

        const recognition = new SpeechRecognitionAPI();
        recognition.lang = "en-US";
        recognition.continuous = false;
        recognition.interimResults = false;

        let listening = false;

        micBtn.addEventListener("click", () => {

            if (listening) {
                recognition.stop();
                return;
            }

            recognition.start();
        });

        recognition.addEventListener("start", () => {
            listening = true;
            micBtn.classList.add("listening");
        });

        recognition.addEventListener("end", () => {
            listening = false;
            micBtn.classList.remove("listening");
        });

        recognition.addEventListener("result", event => {

            const transcript = event.results[0][0].transcript;
            handleCommand(transcript);
        });

        recognition.addEventListener("error", () => {

            addMessage("bot", "I couldn't hear that clearly. Try again, or type instead.");
        });

    } else {

        micBtn.style.display = "none";
        addMessage(
            "bot",
            "Voice input isn't supported in this browser. Try Chrome or Edge, or use the text box below."
        );
    }

})();