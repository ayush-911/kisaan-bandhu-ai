/* =========================================================
   ✅ Kisan SuperAI - MASTER SCRIPT (ALL PAGES)
   ✅ SAFE: No crashes even if elements missing on some pages
   ✅ AI LOCK to prevent quota spam
   ✅ Offline fallback answers if Gemini quota exhausted
   ✅ Chat memory user_id
========================================================= */

let AI_LOCK = false;

/* ✅ Language (fixed to EN for now) */
function getLang(){
  return "en";
}

/* ✅ Stable User ID (for backend memory) */
function getUserId(){
  let uid = localStorage.getItem("kisan_user_id");
  if(!uid){
    uid = "user_" + Math.random().toString(16).slice(2) + "_" + Date.now();
    localStorage.setItem("kisan_user_id", uid);
  }
  return uid;
}

/* ✅ Theme handling */
function applyTheme(){
  const saved = localStorage.getItem("kisan_theme") || "dark";
  const t = document.getElementById("themeToggle");

  if(saved === "light"){
    document.body.classList.add("light");
    if(t) t.innerText = "☀️";
  }else{
    document.body.classList.remove("light");
    if(t) t.innerText = "🌙";
  }
}
function toggleTheme(){
  const isLight = document.body.classList.contains("light");
  localStorage.setItem("kisan_theme", isLight ? "dark" : "light");
  applyTheme();
}

/* ✅ Toast */
function showToast(msg){
  let t = document.getElementById("toast");
  if(!t){
    t = document.createElement("div");
    t.id = "toast";
    t.className = "toast hidden";
    document.body.appendChild(t);
  }
  t.innerText = msg;
  t.classList.remove("hidden");
  setTimeout(()=> t.classList.add("hidden"), 2200);
}

/* ✅ basic helper */
function togglePanel(id){
  const el = document.getElementById(id);
  if(el) el.classList.toggle("hidden");
}

/* =========================================================
   ✅ Premium Market Result UI builder
========================================================= */
function escapeHtml(str){
  return (str || "")
    .replaceAll("&","&amp;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;");
}

function extractKgRange(text){
  const t = text || "";
  const regex = /₹\s*(\d+)\s*[-–]\s*₹\s*(\d+)\s*\/\s*kg/gi;
  const m = regex.exec(t);
  if(!m) return null;
  const min = parseInt(m[1],10);
  const max = parseInt(m[2],10);
  if(isNaN(min) || isNaN(max)) return null;
  return {min, max};
}

function marketCardUI({crop, state, text}){
  const range = extractKgRange(text);
  let min = null, max = null, avg = null;

  if(range){
    min = range.min;
    max = range.max;
    avg = Math.round((min + max) / 2);
  }

  return `
    <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; align-items:flex-start;">
      <div>
        <div style="font-weight:1000; font-size:18px;">✅ Market Insight</div>
        <div class="muted" style="margin-top:4px;">Crop: <b>${escapeHtml(crop)}</b> • State: <b>${escapeHtml(state)}</b></div>
      </div>
    </div>

    ${min !== null ? `
      <div class="price-grid">
        <div class="price-card">
          <div class="price-top">
            <div style="font-weight:900;">📉 Min Price</div>
            <div class="muted">per kg</div>
          </div>
          <div class="price-mid">
            <div>
              <div class="muted">₹/kg</div>
              <h3>₹${min}</h3>
            </div>
            <div>
              <div class="muted">₹/quintal</div>
              <h3>₹${min*100}</h3>
            </div>
            <div>
              <div class="muted">Trend</div>
              <h3>Low</h3>
            </div>
          </div>
        </div>

        <div class="price-card">
          <div class="price-top">
            <div style="font-weight:900;">📈 Max Price</div>
            <div class="muted">per kg</div>
          </div>
          <div class="price-mid">
            <div>
              <div class="muted">₹/kg</div>
              <h3>₹${max}</h3>
            </div>
            <div>
              <div class="muted">₹/quintal</div>
              <h3>₹${max*100}</h3>
            </div>
            <div>
              <div class="muted">Trend</div>
              <h3>High</h3>
            </div>
          </div>
        </div>

        <div class="price-card" style="grid-column: 1 / -1;">
          <div class="price-top">
            <div style="font-weight:900;">⭐ Average Estimate</div>
            <div class="muted">best approx</div>
          </div>
          <div class="price-mid">
            <div>
              <div class="muted">₹/kg</div>
              <h3>₹${avg}</h3>
            </div>
            <div>
              <div class="muted">₹/quintal</div>
              <h3>₹${avg*100}</h3>
            </div>
            <div>
              <div class="muted">Suggestion</div>
              <h3>Sell Smart</h3>
            </div>
          </div>
          <div class="price-foot muted">⚠️ This is an approximate estimate. Please verify in nearest mandi ✅</div>
        </div>
      </div>
      <div class="divider"></div>
    ` : `<div class="divider"></div>`}

    <pre style="margin:0; white-space:pre-wrap; font-family:inherit;">${escapeHtml(text)}</pre>
  `;
}

/* =========================================================
   ✅ OFFLINE FALLBACK ANSWERS (12+ lines each)
========================================================= */
function offlineFallbackAnswer(msg){
  const m = (msg || "").toLowerCase();

  // ✅ Best winter crop
  if(m.includes("best winter") || (m.includes("best") && m.includes("winter crop")) || (m.includes("best") && m.includes("crop"))){
    return `👋 Hello farmer! 😊
✅ Before I guide you, tell me your City / Village (Gaav) 🌍

✅ Best Winter Crops (India) 🌾

🔸 North India (UP/Bihar/Punjab/Haryana)
✅ Wheat 🌾 (Low risk + stable)
✅ Mustard 🌿 (Less water)
✅ Potato 🥔 (High profit)
✅ Gram/Chana 🌰 (Dry area best)

🔸 East India (WB/Odisha/Jharkhand)
✅ Potato 🥔
✅ Mustard 🌿
✅ Pulses 🌱
✅ Vegetables 🥬

🔸 Central India (MP/Chhattisgarh)
✅ Wheat 🌾
✅ Gram 🌰
✅ Mustard 🌿

⭐ Quick Tips
✅ Low water → Gram/Mustard best
✅ High profit → Potato/Vegetables
✅ Soil test = best decision ✅`;
  }

  // ✅ Rain protection
  if(m.includes("rain")){
    return `👋 Hello farmer! 😊
✅ Heavy Rain Protection Plan 🌧️

1) ✅ Make field drainage channels
2) ✅ Remove standing water within 6–8 hours
3) ✅ Avoid urea during heavy rain days
4) ✅ Add soil bunds to stop erosion
5) ✅ Use mulch/straw to protect roots
6) ✅ Spray Mancozeb 2g/L after rain stops
7) ✅ If fungal risk high → Copper Oxychloride 2g/L
8) ✅ Use Trichoderma in soil (root protection)
9) ✅ Check leaf spots daily after rain
10) ✅ Remove infected leaves quickly
11) ✅ Avoid watering 2 days after rain
12) ✅ Spray only when wind is low ✅

✅ Tell me crop name + city for exact plan 🌾`;
  }

  // ✅ Wheat fertilizer plan
  if(m.includes("wheat") && (m.includes("fert") || m.includes("fertilizer") || m.includes("plan"))){
    return `👋 Hello farmer! 😊
✅ Wheat Fertilizer Plan (General per acre)

🔸 1) Base Dose (Before sowing)
✅ FYM/Compost: 1–2 t (if available)
✅ DAP: 50 kg OR SSP: 150 kg
✅ Urea: 20–25 kg (small start dose)
✅ MOP (Potash): 10–15 kg (if soil needs)

🔸 2) First Top Dressing (20–25 days)
✅ Urea: 25–30 kg
✅ Irrigation after applying ✅

🔸 3) Second Top Dressing (40–45 days)
✅ Urea: 25–30 kg

🔸 Extra Tips
✅ Zinc deficiency → ZnSO4 10kg/acre (if needed)
✅ Avoid urea before rain
✅ Soil test = best accuracy ✅`;
  }

  // ✅ Yellow leaves
  if(m.includes("yellow")){
    return `👋 Hello farmer! 😊
✅ Yellow Leaves Solution (Fast + Safe)

1) ✅ Check water first (waterlogging/drainage)
2) ✅ If soil dry → light irrigation
3) ✅ Nitrogen deficiency → Urea spray 2% (20g/L)
4) ✅ OR apply Urea 20–25kg/acre
5) ✅ If patchy yellow → Zinc Sulphate 5g/L
6) ✅ Mix Lime 2.5g/L with zinc spray
7) ✅ NPK 19:19:19 spray 5g/L (boost)
8) ✅ If pests (white insects) → Neem oil 5ml/L
9) ✅ If leaf spots → Mancozeb 2g/L
10) ✅ Repeat after 5–7 days if needed
11) ✅ Remove weeds (nutrition stealing)
12) ✅ Do not over-spray chemicals ✅

✅ Tell me crop + city, I’ll guide exact ✅`;
  }

  return `👋 Hello farmer! 😊
✅ AI quota is temporarily reached.
1) ✅ Wait 1–2 minutes and try again
2) ✅ Try shorter question
3) ✅ Ask about: fertilizer / pests / rain / disease
4) ✅ Provide crop + city for accurate help 🌍`;
}

/* =========================================================
   ✅ MARKET PRICE FEATURE (LOCK + PREMIUM UI)
========================================================= */
async function getMarketPrice(){
  if(AI_LOCK){
    showToast("⏳ Please wait...");
    return;
  }
  AI_LOCK = true;

  const crop = document.getElementById("mCrop")?.value?.trim();
  const state = document.getElementById("mState")?.value?.trim();
  const loader = document.getElementById("mLoader");
  const result = document.getElementById("mResult");

  if(!crop || !state){
    AI_LOCK = false;
    showToast("⚠️ Enter crop + state");
    return;
  }

  loader?.classList.remove("hidden");
  result?.classList.add("hidden");

  try{
    const res = await fetch("/market_prices",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ crop, state, lang: getLang() })
    });

    const data = await res.json();
    loader?.classList.add("hidden");

    if(!data.ok){
      showToast(data.error || "Market lookup failed");
      return;
    }

    if(result){
      result.classList.remove("hidden");
      result.innerHTML = marketCardUI({
        crop,
        state,
        text: data.ai_price || "No data found"
      });
    }
  }catch(e){
    loader?.classList.add("hidden");
    showToast("❌ Server error in market.");
    console.error(e);
  }finally{
    AI_LOCK = false;
  }
}

/* =========================================================
   ✅ PREDICTOR FEATURE
========================================================= */
async function getPrediction(){
  const location = document.getElementById("location")?.value?.trim();
  const crop = document.getElementById("crop")?.value;
  const acres = document.getElementById("acres")?.value;

  const loader = document.getElementById("loader");
  const dashboard = document.getElementById("dashboard");

  if(!location || !crop || !acres){
    showToast("⚠️ Fill location + crop + acres");
    return;
  }

  loader?.classList.remove("hidden");
  dashboard?.classList.add("hidden");

  try{
    const res = await fetch("/predict",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ location, crop, acres, lang: getLang() })
    });

    const data = await res.json();
    loader?.classList.add("hidden");

    if(!data.ok){
      showToast(data.error || "Prediction failed");
      return;
    }

    dashboard?.classList.remove("hidden");

    const prob = Number(data.probability || 0);
    document.getElementById("probBadge") && (document.getElementById("probBadge").innerText = `${prob}%`);
    document.getElementById("ringValue") && (document.getElementById("ringValue").innerText = `${prob}%`);
    document.getElementById("bestTime") && (document.getElementById("bestTime").innerText = data.best_time || "—");
    document.getElementById("currentSummary") && (document.getElementById("currentSummary").innerText = data.summary || "—");

    const ring = document.getElementById("ringProg");
    if(ring){
      const r = 48;
      const c = 2 * Math.PI * r;
      ring.style.strokeDasharray = c;
      ring.style.strokeDashoffset = c - (prob/100) * c;
    }

    const rain = Number(data.rain_risk || 0);
    const wind = Number(data.wind_risk || 0);
    const heat = Number(data.heat_risk || 0);

    document.getElementById("rainRisk") && (document.getElementById("rainRisk").innerText = `${rain}%`);
    document.getElementById("windRisk") && (document.getElementById("windRisk").innerText = `${wind}%`);
    document.getElementById("heatRisk") && (document.getElementById("heatRisk").innerText = `${heat}%`);

    document.getElementById("rainFill") && (document.getElementById("rainFill").style.width = `${rain}%`);
    document.getElementById("windFill") && (document.getElementById("windFill").style.width = `${wind}%`);
    document.getElementById("heatFill") && (document.getElementById("heatFill").style.width = `${heat}%`);

    document.getElementById("seedNeed") && (document.getElementById("seedNeed").innerText = data.seed_need || "—");
    document.getElementById("duration") && (document.getElementById("duration").innerText = data.duration || "—");

    const riskStatus = document.getElementById("riskStatus");
    if(riskStatus){
      riskStatus.innerText = (rain > 70 || wind > 70 || heat > 70)
        ? "⚠️ High risk detected. Follow the solutions below."
        : "✅ Weather looks okay.";
    }

    const fertPlan = document.getElementById("fertPlan");
    if(fertPlan){
      fertPlan.innerHTML = "";
      (data.fertilizer_plan || ["—"]).forEach(x=>{
        const li = document.createElement("li");
        li.innerText = x;
        fertPlan.appendChild(li);
      });
    }

    const irrPlan = document.getElementById("irrPlan");
    if(irrPlan){
      irrPlan.innerHTML = "";
      (data.irrigation_plan || ["—"]).forEach(x=>{
        const li = document.createElement("li");
        li.innerText = x;
        irrPlan.appendChild(li);
      });
    }

    const solutions = document.getElementById("solutions");
    if(solutions){
      solutions.innerHTML = "";
      (data.solutions || ["—"]).forEach(x=>{
        const div = document.createElement("div");
        div.className = "sol";
        div.innerText = x;
        solutions.appendChild(div);
      });
    }

    showToast("✅ Prediction complete!");
  }catch(e){
    loader?.classList.add("hidden");
    showToast("❌ Server error in prediction.");
    console.error(e);
  }
}

/* ✅ PDF download */
function downloadPDF(){
  window.open("/download_pdf", "_blank");
}

/* =========================================================
   ✅ CHATBOT UI (Gemini → Offline Swift Switch)
========================================================= */
function addBubble(text, type="bot"){
  const box = document.getElementById("chatBubbles");
  if(!box) return;

  const div = document.createElement("div");
  div.className = type === "user" ? "user-bubble" : "bot-bubble";
  div.innerText = text;

  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function setTyping(show=true){
  const box = document.getElementById("chatBubbles");
  if(!box) return;

  let t = document.getElementById("typingBubble");
  if(show){
    if(t) return;
    t = document.createElement("div");
    t.id = "typingBubble";
    t.className = "bot-bubble typing";
    t.innerText = "Typing...";
    box.appendChild(t);
    box.scrollTop = box.scrollHeight;
  }else{
    if(t) t.remove();
  }
}

async function sendFloatingChat(){
  if(AI_LOCK){
    showToast("⏳ Wait bro...");
    return;
  }

  const input = document.getElementById("floatQuestion");
  const msg = input?.value?.trim();

  if(!msg){
    showToast("Type a message");
    return;
  }

  AI_LOCK = true;

  addBubble(msg, "user");
  input.value = "";
  setTyping(true);

  try{
    const res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({
        message: msg,
        lang: getLang(),
        user_id: getUserId()
      })
    });

    const data = await res.json();
    setTyping(false);

    if(!data.ok){
      const err = (data.error || "").toString();

      // ✅ FAST switch Gemini → Offline fallback
      if(err.includes("429") || err.includes("RESOURCE_EXHAUSTED") || err.includes("quota")){
        addBubble(offlineFallbackAnswer(msg), "bot");
        return;
      }

      addBubble(data.error || "Chat error. Try again.", "bot");
      return;
    }

    addBubble(data.reply || "No reply received.", "bot");
  }catch(err){
    setTyping(false);

    // ✅ In server down also give offline fallback
    addBubble(offlineFallbackAnswer(msg), "bot");
    console.error(err);
  }finally{
    AI_LOCK = false;
  }
}

function toggleChatBox(){
  const chat = document.getElementById("floatingChat");
  const icon = document.getElementById("chatToggleIcon");
  if(!chat) return;

  chat.classList.toggle("collapsed");
  if(icon){
    icon.innerText = chat.classList.contains("collapsed") ? "▲" : "▼";
  }
}

function openFloatingChat(){
  const chat = document.getElementById("floatingChat");
  const icon = document.getElementById("chatToggleIcon");
  if(!chat) return;

  chat.classList.remove("collapsed");
  if(icon) icon.innerText = "▼";
}

function sendChipFromUI(chipKey){
  const chipMap = {
    chip_yellow: "My crop leaves are turning yellow. What should I do?",
    chip_best: "Which is the best winter crop for my area?",
    chip_rain: "Heavy rain is coming. How can I protect my crop?",
    chip_fert: "Suggest the best fertilizer plan for wheat."
  };

  const q = chipMap[chipKey] || "Help me with my crop problem.";
  const input = document.getElementById("floatQuestion");
  if(input) input.value = q;
  sendFloatingChat();
}

function startVoice(){
  const input = document.getElementById("floatQuestion");
  if(!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)){
    showToast("Voice not supported in this browser");
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recog = new SpeechRecognition();
  recog.lang = "en-IN";
  recog.interimResults = false;
  recog.maxAlternatives = 1;

  recog.onresult = (event) => {
    const text = event.results?.[0]?.[0]?.transcript || "";
    if(input) input.value = text;
  };
  recog.onerror = () => showToast("Voice error");
  recog.start();
}

/* ✅ INIT */
window.addEventListener("load", () => {
  try {
    applyTheme();
  } catch (e) {}

  const chatInput = document.getElementById("floatQuestion");
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        sendFloatingChat();
      }
    });
  }
});
