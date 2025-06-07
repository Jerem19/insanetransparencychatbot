// URL de l'API backend
const API_BASE = "http://localhost:5000/api";

// Initialisation de la carte Leaflet
const map = L.map("map", {
  zoomControl: false   
}).setView([46.3, 7.6], 9);

// Ajouter le fond de carte (OpenStreetMap)
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 18,
}).addTo(map);

// Sélection des éléments
const sidePanel = document.getElementById("side-panel");
const cityNameEl = document.getElementById("city-name");
const themesListEl = document.getElementById("themes-list");
const adminBtn = document.getElementById("admin-login-btn");

// --- Chatbot Loader & Éléments ---
const loader   = document.getElementById("chat-loader");
const input    = document.getElementById("chat-input");
const btn      = document.getElementById("chat-send-btn");
const messages = document.getElementById("chat-messages");

// Fermeture du panneau latéral
document.getElementById("close-side-panel").addEventListener("click", () => {
  sidePanel.classList.remove("visible");
  setTimeout(() => {
    adminBtn.style.display = "block";
  }, 300);
});

// Fonction pour récupérer et afficher les villes
async function loadCities() {
  try {
    const res = await fetch(`${API_BASE}/public/cities`);
    const cities = await res.json();
    cities.forEach((ville) => {
      const marker = L.marker([ville.latitude, ville.longitude]).addTo(map);
      marker.on("click", () => showCityInfo(ville));
    });
  } catch (err) {
    console.error("Erreur lors du chargement des villes :", err);
  }
}

// Fonction qui affiche les thèmes et contenus pour une ville
async function showCityInfo(ville) {
  try {
    cityNameEl.textContent = ville.name;
    themesListEl.innerHTML = "";

    const res = await fetch(`${API_BASE}/themes/${ville.id}`);
    const themes = await res.json();

    if (themes.length === 0) {
      const li = document.createElement("li");
      li.textContent = "Aucun thème disponible.";
      themesListEl.appendChild(li);
    } else {
      themes.forEach((theme) => {
        const li = document.createElement("li");
        const titleSpan = document.createElement("span");
        titleSpan.textContent = theme.theme_name;
        li.appendChild(titleSpan);

        if (theme.contents.length > 0) {
          const ulCont = document.createElement("ul");
          theme.contents.forEach((contenu) => {
            const liCont = document.createElement("li");
            const a = document.createElement("a");
            a.href = contenu.url;
            a.target = "_blank";
            a.textContent = contenu.title;
            liCont.appendChild(a);
            ulCont.appendChild(liCont);
          });
          li.appendChild(ulCont);
        } else {
          const p = document.createElement("p");
          p.textContent = "Pas de contenu.";
          li.appendChild(p);
        }
        themesListEl.appendChild(li);
      });
    }

    // Afficher le panneau latéral et masquer le bouton Admin
    sidePanel.classList.add("visible");
    adminBtn.style.display = "none";

  } catch (err) {
    console.error("Erreur lors de la récupération des thèmes :", err);
  }
}

// Lancement de l'application
loadCities();

// Listener du chatbot avec loader
btn.addEventListener("click", async () => {
  const message = input.value.trim();
  if (!message) return;

  // 1) afficher loader + désactiver input/button
  loader.classList.remove("hidden");
  input.disabled = true;
  btn.disabled   = true;

  // Affiche la question de l'utilisateur
  messages.innerHTML += `<div><strong>Vous :</strong> ${message}</div>`;
  input.value = "";

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();

    // Affiche la réponse du chatbot
    messages.innerHTML += `<div><strong>Gemma3 :</strong> ${data.response}</div>`;
    messages.scrollTop = messages.scrollHeight;
  } catch (err) {
    messages.innerHTML += `<div style="color:red;">Erreur avec le chatbot</div>`;
    console.error("Erreur chatbot :", err);
  } finally {
    // 2) masquer loader + réactiver input/button
    loader.classList.add("hidden");
    input.disabled = false;
    btn.disabled   = false;
  }
});
