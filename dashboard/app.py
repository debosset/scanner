from flask import Flask, jsonify, render_template_string
import json
import time
import os

app = Flask(__name__)

# Detect paths automatically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

GEN_STATUS = os.path.join(PARENT_DIR, "generator", "status.json")
PUZ_STATUS = os.path.join(PARENT_DIR, "puzzleweb", "status.json")

# Fallback to /opt/ if files not found
if not os.path.exists(GEN_STATUS):
    GEN_STATUS = "/opt/generator/status.json"
if not os.path.exists(PUZ_STATUS):
    PUZ_STATUS = "/opt/puzzleweb/status.json"

TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Scanner Dashboard - Optimized</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <script>
    // Auto-refresh toutes les 5 secondes
    setInterval(function() {
      fetch('/api/status')
        .then(r => r.json())
        .then(data => updateDashboard(data))
        .catch(console.error);
    }, 5000);
  </script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">
  <div class="max-w-6xl mx-auto py-8 px-4 space-y-6">

    <!-- HEADER -->
    <header class="space-y-1">
      <h1 class="text-3xl font-bold">🚀 Scanner Dashboard - OPTIMIZED</h1>
      <p class="text-sm text-slate-400">
        Generator (ETH+BTC random) &amp; Bitcoin Puzzle #71 &mdash; auto-refresh toutes les 5s.
      </p>
      <p class="text-xs text-emerald-400">
        ✨ Version optimisée : 10-15x plus rapide avec monitoring complet
      </p>
    </header>

    <!-- GLOBAL SUMMARY -->
    <section class="bg-slate-800 rounded-2xl p-4 shadow-lg">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold">Vue d'ensemble</h2>
          <p class="text-xs text-slate-400">
            Total global de clés testées (generator + puzzle) et vitesses actuelles.
          </p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
          <div class="bg-slate-900/60 rounded-xl px-3 py-2">
            <div class="text-xs text-slate-400">Total global de clés</div>
            <div id="global-total-keys" class="font-mono text-lg">-</div>
          </div>
          <div class="bg-slate-900/60 rounded-xl px-3 py-2">
            <div class="text-xs text-slate-400">Vitesse Generator</div>
            <div id="global-speed-gen" class="font-mono text-lg">-</div>
          </div>
          <div class="bg-slate-900/60 rounded-xl px-3 py-2">
            <div class="text-xs text-slate-400">Vitesse Puzzle</div>
            <div id="global-speed-puz" class="font-mono text-lg">-</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CARDS -->
    <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Generator Card -->
      <div class="bg-slate-800 rounded-2xl p-5 shadow-lg" id="card-generator">
        <div class="flex justify-between items-center mb-3">
          <h2 class="text-xl font-semibold">Generator</h2>
          <span class="text-xs px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-300">
            ETH + BTC random
          </span>
        </div>
        <div class="space-y-1 text-sm">
          <p><span class="text-slate-400">Session keys :</span>
             <span id="gen-keys" class="font-mono">-</span></p>
          <p><span class="text-slate-400">Total global :</span>
             <span id="gen-total" class="font-mono">-</span></p>
          <p><span class="text-slate-400">Speed :</span>
             <span id="gen-speed" class="font-mono">-</span> keys/s</p>
          <p><span class="text-slate-400">Elapsed :</span>
             <span id="gen-elapsed" class="font-mono">-</span></p>
          <p><span class="text-slate-400">Last ETH :</span>
             <span id="gen-eth" class="font-mono text-xs break-all">-</span></p>
          <p><span class="text-slate-400">Last BTC :</span>
             <span id="gen-btc" class="font-mono text-xs break-all">-</span></p>
          <p><span class="text-slate-400">Hits :</span>
             <span id="gen-hits" class="font-mono">ETH 0 / BTC 0</span></p>
          <p class="text-xs text-slate-500">Last update :
             <span id="gen-update">-</span></p>
        </div>
      </div>

      <!-- Puzzle Card -->
      <div class="bg-slate-800 rounded-2xl p-5 shadow-lg" id="card-puzzle">
        <div class="flex justify-between items-center mb-3">
          <h2 class="text-xl font-semibold">Puzzle #71</h2>
          <span class="text-xs px-2 py-1 rounded-full bg-cyan-500/20 text-cyan-300">
            BTC random search
          </span>
        </div>
        <div class="space-y-1 text-sm">
          <p><span class="text-slate-400">Target :</span>
             <span id="puz-target" class="font-mono text-xs break-all">-</span></p>
          <p><span class="text-slate-400">Range :</span>
             <span id="puz-range" class="font-mono text-xs break-all">-</span></p>
          <p><span class="text-slate-400">Session keys :</span>
             <span id="puz-keys" class="font-mono">-</span></p>
          <p><span class="text-slate-400">Total global :</span>
             <span id="puz-total" class="font-mono">-</span></p>
          <p><span class="text-slate-400">Speed :</span>
             <span id="puz-speed" class="font-mono">-</span> keys/s</p>
          <p><span class="text-slate-400">Elapsed :</span>
             <span id="puz-elapsed" class="font-mono">-</span></p>
          <p><span class="text-slate-400">Last key :</span>
             <span id="puz-lastkey" class="font-mono text-xs break-all">-</span></p>
          <p><span class="text-slate-400">Found :</span>
             <span id="puz-found" class="font-mono">false</span></p>
          <p class="text-xs text-slate-500">Last update :
             <span id="puz-update">-</span></p>
        </div>
      </div>
    </section>

    <!-- PUZZLE RANGE + COVERAGE -->
    <section class="bg-slate-800 rounded-2xl p-5 shadow-lg">
      <div class="flex justify-between items-center mb-2">
        <h2 class="text-xl font-semibold">Position & couverture du range Puzzle</h2>
        <span id="puz-range-pos-text" class="text-xs text-slate-300">-</span>
      </div>
      <p class="text-xs text-slate-400 mb-3">
        La barre représente le range complet (min → max). Le curseur indique la position de la dernière clé testée.
      </p>
      <div class="w-full h-4 bg-slate-700 rounded-full relative overflow-hidden mb-1">
        <div class="absolute inset-0 bg-gradient-to-r from-slate-700 via-slate-600 to-slate-700 opacity-70"></div>
        <div id="puz-range-marker"
             class="absolute top-0 h-4 w-1.5 bg-cyan-400 rounded-full shadow-[0_0_10px_rgba(34,211,238,0.9)]"
             style="left: 0%;">
        </div>
      </div>
      <div class="flex justify-between text-[10px] text-slate-500 mb-2">
        <span id="puz-range-min">min</span>
        <span id="puz-range-max">max</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs mt-3">
        <div class="bg-slate-900/60 rounded-xl px-3 py-2">
          <div class="text-slate-400">Couverture session</div>
          <div id="puz-coverage-session" class="font-mono text-sm">-</div>
        </div>
        <div class="bg-slate-900/60 rounded-xl px-3 py-2">
          <div class="text-slate-400">Couverture globale</div>
          <div id="puz-coverage-global" class="font-mono text-sm">-</div>
        </div>
        <div class="bg-slate-900/60 rounded-xl px-3 py-2">
          <div class="text-slate-400">ETA (100% du range)</div>
          <div id="puz-eta-full" class="font-mono text-sm">-</div>
        </div>
      </div>
    </section>

    <!-- SPEED HISTORY CHART -->
    <section class="bg-slate-800 rounded-2xl p-5 shadow-lg">
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-xl font-semibold">Historique des vitesses</h2>
        <span class="text-xs text-slate-400">
          Keys/s pour Generator et Puzzle (dernières minutes).
        </span>
      </div>
      <canvas id="speedChart" height="80"></canvas>
    </section>

    <footer class="text-xs text-slate-500 text-center pt-4">
      Dashboard temps réel optimisé. Version 2.0 avec monitoring complet.
    </footer>
  </div>

  <script>
    let speedChart = null;
    let speedHistoryLabels = [];
    let speedHistoryGen = [];
    let speedHistoryPuz = [];
    const MAX_POINTS = 60;  // ~5 minutes si refresh 5s

    function formatNumber(n) {
      if (n === null || n === undefined) return "-";
      return n.toLocaleString("en-US");
    }

    function formatSeconds(sec) {
      if (sec === null || sec === undefined) return "-";
      var s = Math.floor(sec);
      var m = Math.floor(s / 60);
      var h = Math.floor(m / 60);
      var d = Math.floor(h / 24);
      var y = Math.floor(d / 365);
      s = s % 60;
      m = m % 60;
      h = h % 24;
      d = d % 365;

      if (y > 0) return y + "y " + d + "d";
      if (d > 0) return d + "d " + h + "h";
      if (h > 0) return h + "h " + m + "m";
      if (m > 0) return m + "m " + s + "s";
      return s + "s";
    }

    function parseHexToBigInt(h) {
      if (!h) return null;
      try {
        return BigInt(h);
      } catch (e) {
        return null;
      }
    }

    function updateDashboard(data) {
      const gen = data.generator || {};
      const puz = data.puzzle || {};

      // === GENERATOR ===
      document.getElementById("gen-keys").textContent   = formatNumber(gen.keys_tested);
      document.getElementById("gen-total").textContent  = formatNumber(gen.total_keys_tested);
      document.getElementById("gen-speed").textContent  = (gen.speed_keys_per_sec || 0).toFixed(2);
      document.getElementById("gen-elapsed").textContent= formatSeconds(gen.elapsed_seconds);
      document.getElementById("gen-eth").textContent    = gen.last_eth_address || "-";
      document.getElementById("gen-btc").textContent    = gen.last_btc_address || "-";
      document.getElementById("gen-hits").textContent   =
        "ETH " + (gen.eth_hits || 0) + " / BTC " + (gen.btc_hits || 0);
      document.getElementById("gen-update").textContent = gen.last_update || "-";

      // === PUZZLE ===
      document.getElementById("puz-target").textContent = puz.target_address || "-";
      const rangeStr = (puz.range_start_hex || "?") + " → " + (puz.range_end_hex || "?");
      document.getElementById("puz-range").textContent  = rangeStr;
      document.getElementById("puz-keys").textContent   = formatNumber(puz.keys_checked);
      document.getElementById("puz-total").textContent  = formatNumber(puz.total_keys_tested);
      document.getElementById("puz-speed").textContent  = (puz.keys_per_second || 0).toFixed(2);
      document.getElementById("puz-elapsed").textContent= formatSeconds(puz.elapsed_seconds);
      document.getElementById("puz-lastkey").textContent= puz.last_key_hex || "-";
      document.getElementById("puz-found").textContent  = puz.found ? "true" : "false";
      document.getElementById("puz-update").textContent = puz.updated_at_utc || "-";

      // === GLOBAL SUMMARY ===
      const totalGen = gen.total_keys_tested || 0;
      const totalPuz = puz.total_keys_tested || 0;
      const globalTotal = totalGen + totalPuz;

      document.getElementById("global-total-keys").textContent = formatNumber(globalTotal);
      document.getElementById("global-speed-gen").textContent  =
        (gen.speed_keys_per_sec || 0).toFixed(2) + " keys/s";
      document.getElementById("global-speed-puz").textContent  =
        (puz.keys_per_second || 0).toFixed(2) + " keys/s";

      // === RANGE BAR & COVERAGE (PUZZLE) ===
      const startHex = puz.range_start_hex;
      const endHex   = puz.range_end_hex;
      const lastHex  = puz.last_key_hex;

      document.getElementById("puz-range-min").textContent = startHex || "min";
      document.getElementById("puz-range-max").textContent = endHex   || "max";

      const startBI = parseHexToBigInt(startHex);
      const endBI   = parseHexToBigInt(endHex);
      const lastBI  = parseHexToBigInt(lastHex);

      let posPercent = null;
      let covSession = null;
      let covGlobal  = null;
      let etaText    = "-";

      if (startBI !== null && endBI !== null && endBI > startBI) {
        const rangeSize = endBI - startBI + 1n;

        // Position de la dernière clé
        if (lastBI !== null) {
          const pos = lastBI - startBI;
          let ratioPos = Number(pos * 1000000n / rangeSize) / 1000000;
          if (ratioPos < 0) ratioPos = 0;
          if (ratioPos > 1) ratioPos = 1;
          posPercent = ratioPos * 100;
        }

        // Couverture session
        const sessionKeys = BigInt(puz.keys_checked || 0);
        const totalKeys   = BigInt(puz.total_keys_tested || 0);

        covSession = Number(sessionKeys * 100000000n / rangeSize) / 1000000;
        covGlobal  = Number(totalKeys   * 100000000n / rangeSize) / 1000000;

        // ETA global (temps pour 100% à la vitesse actuelle)
        const speed = puz.keys_per_second || 0;
        if (speed > 0) {
          let remaining = rangeSize - totalKeys;
          if (remaining < 0n) remaining = 0n;
          let remainingSec = Number(remaining) / speed;
          if (!isFinite(remainingSec) || remainingSec < 0) {
            etaText = "inatteignable";
          } else {
            etaText = formatSeconds(remainingSec);
          }
        }
      }

      // Position curseur
      const marker = document.getElementById("puz-range-marker");
      const posText = document.getElementById("puz-range-pos-text");
      if (posPercent === null) {
        marker.style.left = "0%";
        posText.textContent = "Position inconnue";
      } else {
        marker.style.left = posPercent.toFixed(6) + "%";
        posText.textContent = "Position dans le range : " + posPercent.toFixed(6) + " %";
      }

      // Couverture & ETA
      document.getElementById("puz-coverage-session").textContent =
        covSession === null ? "-" : covSession.toFixed(8) + " %";
      document.getElementById("puz-coverage-global").textContent =
        covGlobal === null ? "-" : covGlobal.toFixed(8) + " %";
      document.getElementById("puz-eta-full").textContent = etaText;

      // === SPEED HISTORY CHART ===
      const nowLabel = new Date().toLocaleTimeString();
      const genSpeed = gen.speed_keys_per_sec || 0;
      const puzSpeed = puz.keys_per_second    || 0;

      speedHistoryLabels.push(nowLabel);
      speedHistoryGen.push(genSpeed);
      speedHistoryPuz.push(puzSpeed);

      if (speedHistoryLabels.length > MAX_POINTS) {
        speedHistoryLabels.shift();
        speedHistoryGen.shift();
        speedHistoryPuz.shift();
      }

      const ctx = document.getElementById("speedChart").getContext("2d");
      if (!speedChart) {
        speedChart = new Chart(ctx, {
          type: "line",
          data: {
            labels: speedHistoryLabels,
            datasets: [
              {
                label: "Generator (keys/s)",
                data: speedHistoryGen,
                borderColor: "rgb(16, 185, 129)",
                backgroundColor: "rgba(16, 185, 129, 0.1)",
                borderWidth: 2,
                tension: 0.2
              },
              {
                label: "Puzzle (keys/s)",
                data: speedHistoryPuz,
                borderColor: "rgb(34, 211, 238)",
                backgroundColor: "rgba(34, 211, 238, 0.1)",
                borderWidth: 2,
                tension: 0.2
              }
            ]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                labels: { color: "#cbd5f5" }
              }
            },
            scales: {
              x: {
                ticks: { color: "#cbd5f5", maxRotation: 45, minRotation: 0 },
                grid: { display: false }
              },
              y: {
                beginAtZero: true,
                ticks: { color: "#cbd5f5" }
              }
            }
          }
        });
      } else {
        speedChart.data.labels = speedHistoryLabels;
        speedChart.data.datasets[0].data = speedHistoryGen;
        speedChart.data.datasets[1].data = speedHistoryPuz;
        speedChart.update();
      }
    }

    // Initial load
    fetch('/api/status')
      .then(r => r.json())
      .then(data => updateDashboard(data))
      .catch(console.error);
  </script>
</body>
</html>
"""


def read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


@app.route("/api/status")
def api_status():
    gen = read_json(GEN_STATUS)
    puz = read_json(PUZ_STATUS)
    return jsonify(
        {
            "generator": gen or {},
            "puzzle": puz or {},
            "server_time": time.time(),
        }
    )


@app.route("/")
def index():
    return render_template_string(TEMPLATE)


if __name__ == "__main__":
    print(f"\n[Dashboard] Generator status: {GEN_STATUS}")
    print(f"[Dashboard] Puzzle status: {PUZ_STATUS}\n")
    app.run(host="0.0.0.0", port=5000)