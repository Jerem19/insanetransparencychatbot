// URL de l'API backend
const API_BASE = "http://localhost:5000/api";

// Initialisation de la carte Leaflet
const map = L.map("map").setView([46.3, 7.6], 9);

// Ajouter le fond de carte (OpenStreetMap)
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 18,
}).addTo(map);

// Élément du modal d'info
const infoDiv = document.getElementById("info");
const cityNameEl = document.getElementById("city-name");
const themesListEl = document.getElementById("themes-list");
const closeInfoBtn = document.getElementById("close-info");

// Cacher le modal
closeInfoBtn.addEventListener("click", () => {
  infoDiv.classList.add("hidden");
});

// Fonction pour récupérer et afficher les villes
async function loadCities() {
  try {
    const res = await fetch(`${API_BASE}/cities`);
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
    infoDiv.classList.remove("hidden");
  } catch (err) {
    console.error("Erreur lors de la récupération des thèmes :", err);
  }
}

loadCities();
