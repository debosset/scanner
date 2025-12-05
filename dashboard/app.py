from flask import Flask, jsonify, render_template_string
import json
import time
import os

# psutil pour CPU/RAM/temp
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

GEN_STATUS = os.path.join(PARENT_DIR, "generator", "status.json")
PUZ_STATUS = os.path.join(PARENT_DIR, "puzzleweb", "status.json")

TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Scanner Dashboard</title>
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
      <h1 class="text-3xl font-bold">Scanner Dashboard</h1>
      <p class="text-sm text-slate-400">
        Generator (ETH+BTC random) &amp; Bitcoin Puzzle #71 &mdash; auto-refresh toutes les 5s.
      </p>
    </header>

    <!-- GLOBAL SUMMARY -->
    <section class="bg-slate-800 rounded-2xl p-4 shadow-lg">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold">Vue d'ensemble</h2>
          <p class="text-xs text-slate-400">
            Total global, vitesses (actuelle / moyenne / pic) et état système.
          </p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 gap-3 text-sm w-full md:w-auto">
          <!-- TOTAL GLOBAL -->
          <div class="bg-slate-900/60 rounded-xl px-3 py-2">
            <div class="text-xs text-slate-400">Total global de clés</div>
            <div id="global-total-keys" class="font-mono text-lg">-</div>
          </div>

          <!-- GENERATOR SPEEDS -->
          <div class="bg-slate-900/60 rounded-xl px-3 py-2">
            <div class="text-xs text-slate-400 mb-1">Generator speed</div>
            <div class="text-[11px] space-y-0.5">
              <div><span class="text-slate-500">Actuel :</span>
                   <span id="global-speed-gen-current" class="font-mono">-</span></div>
              <div><span class="text-slate-500">Moyenne :</span>
                   <span id="global-speed-gen-avg" class="font-mono">-</span></div>
              <div><span class="text-slate-500">Pic :</span>
                   <span id="global-speed-gen-peak" class="font-mono">-</span></div>
            </div>
          </div>

          <!-- PUZZLE SPEEDS -->
          <div class="bg-slate-900/60 rounded-xl px-3 py-2">
            <div class="text-xs text-slate-400 mb-1">Puzzle speed</div>
            <div class="text-[11px] space-y-0.5">
              <div><span class="text-slate-500">Actuel :</span>
                   <span id="global-speed-puz-current" class="font-mono">-</span></div>
              <div><span class="text-slate-500">Moyenne :</span>
                   <span id="global-speed-puz-avg" class="font-mono">-</span></div>
              <div><span class="text-slate-500">Pic :</span>
                   <span id="global-speed-puz-peak" class="font-mono">-</span></div>
            </div>
          </div>

          <!-- SYSTEM INFO -->
          <div class="bg-slate-900/60 rounded-xl px-3 py-2">
            <div class="text-xs text-slate-400 mb-1">Système</div>
            <div class="text-[11px] space-y-0.5">
              <div><span class="text-slate-500">CPU :</span>
                   <span id="sys-cpu" class="font-mono">-</span></div>
              <div><span class="text-slate-500">RAM :</span>
                   <span id="sys-ram" class="font-mono">-</span></div>
              <div><span class="text-slate-500">Temp :</span>
                   <span id="sys-temp" class="font-mono">-</span></div>
            </div>
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
      Dashboard temps réel optimisé. Version 2.1 (perf + système).
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

    function computeAvg(arr) {
      if (!arr || arr.length === 0) return 0;
      let sum = 0;
      for (let v of arr) sum += v;
      return sum / arr.length;
    }

    function computePeak(arr) {
      if (!arr || arr.length === 0) return 0;
      return Math.max(...arr);
    }

    function updateDashboard(data) {
      const gen = data.generator || {};
      const puz = data.puzzle || {};
      const system = data.system || {};

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

      // Historique vitesses (pour moyenne/pic)
      const nowLabel = new Date().toLocaleTimeString();
      const genSpeedNow = gen.speed_keys_per_sec || 0;
      const puzSpeedNow = puz.keys_per_second    || 0;

      speedHistoryLabels.push(nowLabel);
      speedHistoryGen.push(genSpeedNow);
      speedHistoryPuz.push(puzSpeedNow);

      if (speedHistoryLabels.length > MAX_POINTS) {
        speedHistoryLabels.shift();
        speedHistoryGen.shift();
        speedHistoryPuz.shift();
      }

      const genAvg  = computeAvg(speedHistoryGen);
      const genPeak = computePeak(speedHistoryGen);
      const puzAvg  = computeAvg(speedHistoryPuz);
      const puzPeak = computePeak(speedHistoryPuz);

      document.getElementById("global-total-keys").textContent =
        formatNumber(globalTotal);

      document.getElementById("global-speed-gen-current").textContent =
        genSpeedNow.toFixed(2) + " keys/s";
      document.getElementById("global-speed-gen-avg").textContent =
        genAvg.toFixed(2) + " keys/s";
      document.getElementById("global-speed-gen-peak").textContent =
        genPeak.toFixed(2) + " keys/s";

      document.getElementById("global-speed-puz-current").textContent =
        puzSpeedNow.toFixed(2) + " keys/s";
      document.getElementById("global-speed-puz-avg").textContent =
        puzAvg.toFixed(2) + " keys/s";
      document.getElementById("global-speed-puz-peak").textContent =
        puzPeak.toFixed(2) + " keys/s";

      // === SYSTEM INFO ===
      const cpu = system.cpu_percent;
      const ramUsed = system.ram_used_gb;
      const ramTotal = system.ram_total_gb;
      const temp = system.temp_c;

      document.getElementById("sys-cpu").textContent =
        (cpu === null || cpu === undefined) ? "-" : cpu.toFixed(1) + " %";

      if (ramUsed === null || ramUsed === undefined || ramTotal === null || ramTotal === undefined) {
        document.getElementById("sys-ram").textContent = "-";
      } else {
        document.getElementById("sys-ram").textContent =
          ramUsed.toFixed(1) + " / " + ramTotal.toFixed(1) + " GB";
      }

      document.getElementById("sys-temp").textContent =
        (temp === null || temp === undefined) ? "-" : temp.toFixed(1) + " °C";

      // === SPEED HISTORY CHART ===
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

def get_system_info():
    if not PSUTIL_AVAILABLE:
        return {}
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        vm = psutil.virtual_memory()
        ram_used_gb = vm.used / (1024**3)
        ram_total_gb = vm.total / (1024**3)

        temp_c = None
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            for key in ["coretemp", "k10temp", "cpu-thermal"]:
                if key in temps and temps[key]:
                    temp_c = temps[key][0].current
                    break

        return {
            "cpu_percent": cpu,
            "ram_percent": vm.percent,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
            "temp_c": temp_c,
        }
    except Exception:
        return {}

@app.route("/api/status")
def api_status():
    gen = read_json(GEN_STATUS)
    puz = read_json(PUZ_STATUS)
    sys_info = get_system_info()
    return jsonify(
        {
            "generator": gen or {},
            "puzzle": puz or {},
            "system": sys_info,
            "server_time": time.time(),
        }
    )

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

if __name__ == "__main__":
    print(f"\\n[Dashboard] Generator status: {GEN_STATUS}")
    print(f"[Dashboard] Puzzle status: {PUZ_STATUS}\\n")
    app.run(host="0.0.0.0", port=5000)
