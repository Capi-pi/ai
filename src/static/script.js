// quand on change de modèle dans le <select>
document.getElementById("model").addEventListener("change", async (e) => {
    const choice = e.target.value;

    const formData = new FormData();
    formData.append("model", choice);

    await fetch("/set_model", {
        method: "POST",
        body: formData
    });
});


document.getElementById("predictBtn").addEventListener("click", 
    async (event) => {
        event.preventDefault()          //prevent sending a basic form request
        console.log("j'ai cliqué sur le bouton")
        const text = document.getElementById("userText").value;
        console.log(text);

        // send a post request to flask
        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        });

        // get the response of the server
        console.log(response);
        const data = await response.json(); //json file with two key: classe_predites and distributions
        console.log(data);
        
        // add the result to the page
        createButtons(data)
        const detail = drawOverview(data.distribution); // affiche l'overview en haut et renvoie le container detail
    })


function createButtons(data)
{
    // si un nav existe déjà, on le supprime (évite les duplications)
    const oldNav = document.querySelector("nav.buttonsContainer");
    if (oldNav) oldNav.remove();

    // create a nav after the header then add an div called buttonContainer to it
    nav = document.createElement("nav");
    div = document.createElement("div")
    document.querySelector("header").insertAdjacentElement("afterend", nav);      
    nav.classList.add("buttonsContainer");
    div.classList.add("buttonsInner")
    nav.appendChild(div);

    // clear "main" content
    document.querySelector("main").innerHTML = "";

    // create buttons and attach listener with closure (capture la distribution)
    for (let i = 0; i < data.distribution.length; i++)
    {
        const button = document.createElement("button");
        button.classList.add("sentenceBtn");
        button.innerText = `Phrase${i+1}`;

        // capture la distribution dans la fermeture — c'est sûr et propre
        const dist = data.distribution[i];
        button.addEventListener("click", () => drawBarInto(document.getElementById("detail-container"), dist));
        div.appendChild(button);

    }
}


// crée l'overview proportionnel + zone de détail
function drawOverview(distributions) {
  // normaliser input (distributions : array of arrays)
  if (!Array.isArray(distributions) || distributions.length === 0) {
    console.warn("Aucune distribution fournie à drawOverview");
    return null;
  }
  // trouver une distribution modèle (la première qui soit un array)
  let model = distributions.find(d => Array.isArray(d)) || distributions[0];
  const classes = model.length;

  // labels & couleurs selon classes
  let LABELS = [], COLORS = [];
  if (classes === 3) {
    LABELS = ["Négatif", "Neutre", "Positif"];
    COLORS = ["#e74c3c","#95a5a6","#27ae60"];
  } else if (classes === 2) {
    LABELS = ["Négatif","Positif"];
    COLORS = ["#e74c3c","#27ae60"];
  } else {
    LABELS = Array.from({length: classes}, (_,i) => `Classe ${i}`);
    COLORS = Array.from({length: classes}, () => "#999");
  }

  // compter les prédictions (argmax par distribution)
  const counts = new Array(classes).fill(0);
  distributions.forEach(dist => {
    const arr = Array.isArray(dist[0]) && dist.length === 1 ? dist[0] : dist;
    let best = 0, bestIdx = 0;
    for (let i = 0; i < Math.min(arr.length, classes); i++) {
      const v = Number(arr[i]) || 0;
      if (i === 0 || v > best) { best = v; bestIdx = i; }
    }
    counts[bestIdx]++;
  });

  const total = distributions.length;
  const percents = counts.map(c => Math.round(c / total * 100));

  // construire DOM -> remplace main par overview + detail container
  const main = document.querySelector("main");
  main.innerHTML = ""; // on remplace le contenu du main

  const wrap = document.createElement("div");
  wrap.className = "overview-wrap";

  const title = document.createElement("h2");
  title.textContent = "Répartition des phrases (par classe prédite)";
  wrap.appendChild(title);

  // barre proportionnelle composée de segments
  const segBar = document.createElement("div");
  segBar.className = "seg-bar";
  // ajouter segments
  for (let i = 0; i < classes; i++) {
    const seg = document.createElement("div");
    seg.className = "seg";
    seg.style.width = percents[i] + "%";
    seg.style.backgroundColor = COLORS[i];
    seg.setAttribute("title", `${LABELS[i]} — ${counts[i]} (${percents[i]}%)`);
    segBar.appendChild(seg);
  }
  wrap.appendChild(segBar);

  // légende (label + count + %)
  const legend = document.createElement("div");
  legend.className = "overview-legend";
  for (let i = 0; i < classes; i++) {
    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `<span class="legend-color" style="background:${COLORS[i]}"></span>
                      <strong>${LABELS[i]}</strong> — ${counts[i]} (${percents[i]}%)`;
    legend.appendChild(item);
  }
  wrap.appendChild(legend);

  // zone qui contiendra le diagramme spécifique à une phrase
  const detail = document.createElement("div");
  detail.id = "detail-container";
  detail.className = "detail-container";
  // message par défaut
  detail.innerHTML = `<p class="hint">Clique sur une phrase pour voir sa distribution.</p>`;

  main.appendChild(wrap);
  main.appendChild(detail);

  // retourne le container détail pour que les autres fonctions l'utilisent
  return detail;
}

// variante de drawBar qui rend DANS un container sans écraser l'overview
function drawBarInto(container, probas) {
  if (!container) {
    console.error("drawBarInto: container invalide");
    return;
  }
  // normaliser probas 1D
  if (Array.isArray(probas[0]) && probas.length === 1) probas = probas[0];
  if (!Array.isArray(probas)) {
    console.error("drawBarInto: probas doit être un tableau");
    return;
  }

  // définir labels/colors selon longueur
  let LABELS, COLORS;
  if (probas.length === 3) {
    LABELS = ["Négatif","Neutre","Positif"];
    COLORS = ["#e74c3c","#95a5a6","#27ae60"];
  } else if (probas.length === 2) {
    LABELS = ["Négatif","Positif"];
    COLORS = ["#e74c3c","#27ae60"];
  } else {
    LABELS = probas.map((_,i)=>`Classe ${i}`);
    COLORS = probas.map(()=>"#999");
  }

  // vider le container détail puis insérer la "carte" phrase
  container.innerHTML = "";
  const card = document.createElement("div");
  card.className = "phrase-card";

  const heading = document.createElement("div");
  heading.className = "phrase-heading";
  heading.textContent = "Distribution de la phrase";
  card.appendChild(heading);

  // création des lignes comme dans drawBar original
  for (let i = 0; i < probas.length; i++) {
    const raw = Number(probas[i]) || 0;
    const pct = Math.round(Math.max(0, Math.min(1, raw)) * 100);

    const row = document.createElement("div");
    row.className = "bar-row";

    const label = document.createElement("div");
    label.className = "bar-label";
    label.textContent = LABELS[i];
    row.appendChild(label);

    const outer = document.createElement("div");
    outer.className = "bar-outer";
    const inner = document.createElement("div");
    inner.className = "bar-inner";
    inner.style.width = "0%";
    inner.style.backgroundColor = COLORS[i % COLORS.length];
    inner.setAttribute("role","progressbar");
    inner.setAttribute("aria-valuemin","0");
    inner.setAttribute("aria-valuemax","100");
    inner.setAttribute("aria-valuenow","0");
    outer.appendChild(inner);
    row.appendChild(outer);

    const pctSpan = document.createElement("div");
    pctSpan.className = "bar-pct";
    pctSpan.textContent = `${pct}%`;
    row.appendChild(pctSpan);

    card.appendChild(row);

    // animate
    (function(innerEl, target, pctEl) {
      // cascade optional
      setTimeout(() => {
        requestAnimationFrame(() => {
          innerEl.style.width = target + "%";
          innerEl.setAttribute("aria-valuenow", String(target));
          pctEl.textContent = target + "%";
        });
      }, i * 80);
    })(inner, pct, pctSpan);
  }

  container.appendChild(card);
}


