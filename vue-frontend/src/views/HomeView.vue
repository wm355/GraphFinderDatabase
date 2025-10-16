<template>
  <div class="home">
    <div class="searchpanel">
      <h1>Search VO2 Dopants</h1>
      <br />
      <div class="searchbox">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search Dopants (e.g., W, B, Cr, Al)…"
          @keyup.enter="searchDopants"
        />
        <button type="button" @click="searchDopants" :disabled="loading">
          {{ loading ? 'Searching...' : 'Search' }}
        </button>

        <!-- Upload CSV controls -->
        <button type="button" @click="triggerUpload" :disabled="uploading" style="margin-left:10px;">
          {{ uploading ? 'Uploading…' : 'Upload CSV' }}
        </button>
        <input
          ref="csvInput"
          type="file"
          accept=".csv"
          multiple
          @change="handleCsvUpload"
          style="display:none"
        />
        <!-- Data type selector -->
        <select v-model="uploadDataType" style="margin-left:10px; padding:10px; border-radius:8px;">
          <option value="resistance_temp">Resistance vs Temp</option>
          <option value="transmittance_temp">Transmittance vs Temp</option>
        </select>

        
      </div>
      <div v-if="uploadHint" style="margin-top:8px; color:#e5e7eb;">{{ uploadHint }}</div>
    </div>

    <div class="databox">
      <div class="datadisplaybox">
        <div class="datatitlepanel">
          <h2 v-if="selectedSeries">
            <!-- If an uploaded CSV is selected, show a friendly header -->
            <template v-if="selectedSeries.isUpload">
              {{ selectedSeries.title }} : Uploaded Data
            </template>
            <template v-else>
              {{ selectedSeries.element + ' ' + selectedSeries.concentration + '% doped : ' + prettyType(selectedSeries.type) }}
            </template>
          </h2>
          <h2 v-else>Select a dataset below. Graphical data will be displayed here</h2>

          <!-- Chart visualization panel -->
          <div v-if="chartData" style="margin-top: 20px;">
            <TemperatureChart :chart-data="chartData" :key="chartKey" />
          </div>

          <!-- Loading chart panel -->
          <div v-else-if="loadingChart" style="margin-top: 20px; padding: 20px; text-align: center; color: whitesmoke;">
            <div style="font-size: 1.1rem;">Loading chart data...</div>
          </div>
        </div>

        <div class="datapanel">
          <h1>Results</h1>
          <div v-if="error" style="padding: 16px; color: #ff6b6b">{{ error }}</div>

          <!-- ===== Uploaded CSVs (appear at top) ===== -->
          <div v-if="uploads.length" style="margin-bottom: 10px;">
            <div style="opacity:0.85; font-size:0.95rem; margin-bottom:6px;">
              Uploaded files
            </div>
            <ul style="list-style:none; padding:0; margin:0;">
              <li
                v-for="u in uploads"
                :key="u.id"
                style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.08);"
              >
                <button
                  class="upload-row"
                  @click="selectUpload(u)"
                  title="View uploaded CSV in chart"
                  style="width:100%; text-align:left; background:transparent; border:1px solid rgba(255,255,255,0.2); border-radius:10px; padding:10px 12px; cursor:pointer;"
                >
                  <strong>{{ u.title }}</strong>
                  <span class="badge" style="margin-left:8px; font-size:12px; opacity:0.9;">Uploaded</span>
                  <div style="opacity:0.8; font-size:0.85rem; margin-top:4px;">
                    y: {{ u.y_label }} • series: {{ u.datasets.length }}
                  </div>
                </button>
              </li>
            </ul>
          </div>

          <!-- ===== Search results from API ===== -->
          <div v-if="results.length">
            <ul style="list-style: none; padding: 0; margin: 0;">
              <li
                v-for="(row, idx) in results"
                :key="row.element + idx"
                style="padding: 14px 0; border-bottom: 1px solid rgba(255,255,255,0.08);"
              >
                <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
                  <div>
                    <strong style="font-size:1.1rem;">{{ row.element }}</strong>
                    <div style="opacity:0.85; font-size:0.9rem;">Available data types:</div>
                  </div>
                  <!-- type chips -->
                  <div style="display:flex; gap:8px; flex-wrap:wrap;">
                    <button
                      v-for="t in row.types"
                      :key="row.element + '|' + t.type"
                      @click="loadSeries(row.element, t.type)"
                      :disabled="loadingSeriesKey === row.element + '|' + t.type"
                      style="background:transparent; border:1px solid rgba(255,255,255,0.25); border-radius:20px; padding:8px 12px; cursor:pointer;"
                      title="Show files for this dopant + type"
                    >
                      {{ prettyType(t.type) }} ({{ t.file_count }})
                    </button>
                  </div>
                </div>

                <!-- concentration pairs for the current element+type -->
                <div v-if="expandedKey === row.element + '|' + chosenType" style="padding: 12px 0 0 0;">
                  <div v-if="series.length">
                    <div style="opacity:0.85; font-size:0.9rem; margin-bottom:6px;">
                      Concentrations for <strong>{{ chosenElement }}</strong> — <strong>{{ prettyType(chosenType) }}</strong>
                    </div>
                    <ul style="list-style:none; padding-left:0; margin:0;">
                      <li
                        v-for="s in series"
                        :key="s.concentration"
                        @click="loadChart(row.element, chosenType, s.concentration)"
                        style="padding: 8px 6px; margin: 2px 0; cursor: pointer; border-radius: 8px; border: 1px solid rgba(255,255,255,0.15);"
                        :title="'View chart for ' + s.concentration + '% concentration'"
                      >
                        <strong>{{ s.concentration }}% Concentration</strong>
                        <span v-if="s.error" style="color:#ff6b6b;"> — {{ s.error }}</span>
                        <div style="opacity:0.8; font-size:0.85rem;">
                          <span v-if="s.has_both" style="color: #10b981;">✓ Heating & Cooling</span>
                          <span v-else-if="s.heating_file" style="color: #ef4444;">Heating only</span>
                          <span v-else-if="s.cooling_file" style="color: #3b82f6;">Cooling only</span>
                          <span v-if="s.sample_points"> • {{ s.sample_points }} points</span>
                          <span v-if="s.y_label"> • y: {{ s.y_label }}</span>
                        </div>
                      </li>
                    </ul>
                  </div>
                  <div v-else-if="loadingSeriesKey" style="opacity:0.85;">Loading concentrations…</div>
                  <div v-else style="opacity:0.85;">No concentrations found.</div>
                </div>
              </li>
            </ul>
          </div>

          <div v-else-if="!loading && !error" style="padding: 16px;">
            No dopants matched. Try a different search (e.g., “W”, “B”, “Ti”).
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Papa from "papaparse";
import TemperatureChart from '../components/TemperatureChart.vue';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api"
});

export default {
  components: { TemperatureChart },
  data() {
    return {
      // search
      searchTerm: "",
      results: [],        // [{ element, types: [{type, file_count}] }]
      error: "",
      loading: false,

      // uploads
      uploads: [],        // [{ id, title, y_label, datasets, isUpload:true }]
      uploading: false,
      uploadHint: "You can upload one or multiple (heating/cooling) CSV file(s) with temperature and series columns",
      uploadDataType: "resistance_temp",

      // series browsing
      chosenElement: "",
      chosenType: "",
      expandedKey: "",    // key is {element,type}
      loadingSeriesKey: "",
      series: [],         // [{ concentration, heating_file, cooling_file, has_both, y_label, sample_points?, error? }]
      selectedSeries: null, // {element, type, concentration} OR {isUpload:true, title}

      // chart data
      chartData: null,
      chartKey: 0,
      loadingChart: false,
      currentChartKey: ""
    };
  },
  mounted() {
    this.searchDopants();
  },
  methods: {
    prettyType(t) {
      if (t === 'upload') return 'Uploaded';
      return t.replace(/_/g, " ").split(" ").map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(" ") + " Data";
    },

    // ===== Upload CSV flow =====
    triggerUpload() {
      this.$refs.csvInput?.click();
    },

    // --- NEW: helpers for pairing/grouping ---
    detectRoleFromName(name) {
      const n = (name || "").toLowerCase();
      if (/(^|[_\-\s])(heating|heat)([_\-\s]|\.|$)/.test(n)) return "heating";
      if (/(^|[_\-\s])(cooling|cool)([_\-\s]|\.|$)/.test(n)) return "cooling";
      return null;
    },

    // Parse dopant + concentration from "<dopant>_<conc>_<role>.csv"
    parseNameParts(name) {
      const m = (name || "").match(/^([A-Za-z]+)_(\d+(?:\.\d+)?)(?:_|\.)/);
      if (!m) return { dopant: "Unknown", concentration: "" };
      const dopant = m[1].toUpperCase();                 // "Y"
      const concentration = m[2];                        // "0" or "2.5"
      return { dopant, concentration };
    },

    // Use "<dopant>_<conc>" as the group key so heating/cooling pair together
    groupKeyFromName(name) {
      const { dopant, concentration } = this.parseNameParts(name);
      if (dopant !== "Unknown" && concentration) {
        return `${dopant.toLowerCase()}_${concentration}`;
      }
      // fallback: strip role pieces
      return (name || "")
        .toLowerCase()
        .replace(/\.(csv)$/, "")
        .replace(/[_\-\s]?(heating|heat|cooling|cool)\b/g, "")
        .replace(/[_\-\s]+$/, "")
        .trim();
    },

    roleColor(role) {
      return role === "heating" ? "#ef4444" : "#3b82f6";
    },

    parseCsvFile(file) {
      return new Promise((resolve, reject) => {
        Papa.parse(file, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          complete: ({ data }) => resolve({ file, rows: data }),
          error: (err) => reject(err)
        });
      });
    },


    // NEW: try to infer dopant name from filename or CSV rows
    extractDopant(fileName, rows) {
      const { dopant } = this.parseNameParts(fileName);
      if (dopant !== "Unknown") return dopant;
      const first = rows?.[0] || {};
      const fromCol = first.Dopant || first.dopant || first.dopants || first.DOPANT;
      return (fromCol && String(fromCol).trim()) ? String(fromCol).trim() : "Unknown";
    },

    extractConcentration(fileName, rows) {
      const { concentration } = this.parseNameParts(fileName);
      if (concentration) return concentration;
      const first = rows?.[0] || {};
      const fromCol = first.Concentration || first.concentration || first.CONCENTRATION;
      return (fromCol == null ? "" : String(fromCol));
    },

    // NEW: POST a single file to server to persist in dopant folder + DB
    async uploadToServer(file, { dopant, role, groupKey }) {
      const form = new FormData();
      form.append("file", file);
      form.append("dopant", dopant);
      form.append("role", role || "");
      form.append("groupKey", groupKey || "");
      form.append("data_type", this.uploadDataType); 
      try {
        await api.post("/upload_csv", form, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } catch (err) {
        console.error("Upload save failed:", err?.response?.data || err);
        this.uploadHint = "Stored locally; server save failed for some files.";
      }
    },


    // UPDATED: accepts role/color for nicer labels + colors
    normalizeCsvToDatasets(rows, { role = null, color = null } = {}) {
      if (!rows?.length) throw new Error('CSV has no data rows.');

      const keys = Object.keys(rows[0] || {});
      const xKey = keys.find(k => ['temperature','temp','t','x'].includes(String(k).toLowerCase()));
      if (!xKey) throw new Error('CSV must contain a Temperature / Temp / T / X column.');

      const yCols = keys.filter(k => k !== xKey);
      if (!yCols.length) throw new Error('CSV must contain at least one Y series column.');

      return yCols.map(col => {
        const data = rows.map(r => {
          const x = Number(r[xKey]);
          const y = Number(r[col]);
          if (!isFinite(x) || !isFinite(y) || y <= 0) return null;
          return { x, y };
        }).filter(Boolean);

        const labelPrefix = role ? (role === 'heating' ? 'Heating — ' : 'Cooling — ') : '';
        const borderColor = color || (role ? this.roleColor(role) : undefined);

        return {
          label: labelPrefix + col,
          data,
          borderWidth: 2,
          fill: false,
          ...(borderColor ? {
            borderColor,
            backgroundColor: borderColor + '20'
          } : {})
        };
      });
    },

    // UPDATED: supports multiple files + groups heating/cooling together
    async handleCsvUpload(e) {
      const files = Array.from(e.target.files || []);
      if (!files.length) return;

      this.uploading = true;
      this.uploadHint = "";
      this.error = "";

      try {
        // Parse all files
        const parsed = await Promise.all(files.map(this.parseCsvFile));

        // Group by base key (filename minus heating/cooling + ext)
        const byGroup = new Map();
        for (const { file, rows } of parsed) {
          const role = this.detectRoleFromName(file.name);
          const key  = this.groupKeyFromName(file.name) || file.name.toLowerCase().replace(/\.(csv)$/,'');
          const dopant = this.extractDopant(file.name, rows);
          const conc = this.extractConcentration(file.name, rows);
          if (!byGroup.has(key)) byGroup.set(key, { items: [], dopant, conc, key });
          byGroup.get(key).items.push({ file, rows, role, dopant, conc, key });
        }

        // Persist each raw file to server (folder per dopant) in parallel
        await Promise.all(
          Array.from(byGroup.values()).flatMap(group =>
            group.items.map(item =>
              this.uploadToServer(item.file, {
                dopant: item.dopant,
                role: item.role,
                groupKey: item.key
              })
            )
          )
        );

        const created = [];
        for (const [key, group] of byGroup.entries()) {
          // optional aesthetics
          group.items.sort((a,b) => (a.role === 'heating' ? -1 : 1));

          const datasets = group.items.flatMap(({ rows, role }) => {
            const color = role ? this.roleColor(role) : undefined;
            return this.normalizeCsvToDatasets(rows, { role, color });
          });

          if (!datasets.length) continue;

          const dopant = group.items[0]?.dopant || "Unknown";
          const conc = group.conc ? `${group.conc}%` : "";
          const hasHeating = group.items.some(i => i.role === 'heating');
          const hasCooling = group.items.some(i => i.role === 'cooling');
          const roleBadge = hasHeating && hasCooling ? " (Heating + Cooling)" :
                            hasHeating ? " (Heating)" :
                            hasCooling ? " (Cooling)" : "";

          const item = {
            id: `csv:${Date.now()}:${Math.random().toString(36).slice(2)}`,
            source: 'csv',
            isUpload: true,
            title: `CSV: ${dopant}${conc ? " " + conc : ""} — ${key}${roleBadge}`,
            y_label: 'Value',
            datasets
          };

          this.uploads.unshift(item);
          created.push(item);
        }

        if (created.length) {
          this.selectUpload(created[0]);
          this.uploadHint = created.length > 1
            ? `Uploaded ${created.length} grouped item(s). Saved to server by dopant folder.`
            : `Upload complete. Saved to server by dopant folder.`;
        } else {
          this.uploadHint = 'No usable series found in the uploaded files.';
        }
      } catch (err) {
        console.error(err);
        this.error = err?.message || String(err);
      } finally {
        this.uploading = false;
        e.target.value = ''; // allow re-upload of same files
      }
    },

    selectUpload(item) {
      this.selectedSeries = { isUpload: true, title: item.title, type: 'upload' };
      this.chartData = {
        datasets: item.datasets,
        element: item.title,
        concentration: '',
        y_label: item.y_label || 'Value'
      };
      this.chartKey++; // Force chart to re-render
    },

    // ===== Search & API flow =====
    async searchDopants() {
      this.loading = true;
      this.error = "";
      this.results = [];
      this.expandedKey = "";
      this.series = [];
      // keep uploaded items
      this.selectedSeries = null;
      this.chartData = null;

      try {
        const { data } = await api.get("/search_dopants", { params: { q: this.searchTerm }});
        if (Array.isArray(data)) {
          this.results = data;
        } else if (data && data.error) {
          this.error = data.error;
        } else {
          this.results = [];
        }
      } catch (e) {
        console.error(e);
        const msg = e?.response?.data?.error || e?.message || "Error searching dopants.";
        this.error = msg;
      } finally {
        this.loading = false;
      }
    },

    async loadSeries(element, type) {
      this.error = "";
      this.series = [];
      this.chosenElement = element;
      this.chosenType = type;
      this.expandedKey = `${element}|${type}`;
      this.loadingSeriesKey = this.expandedKey;
      try {
        const { data } = await api.get("/series", { params: { type, element } });
        this.series = data.series || [];
      } catch (e) {
        console.error(e);
        this.error = "Failed to load files for that selection.";
      } finally {
        this.loadingSeriesKey = "";
      }
    },

    async loadChart(element, type, concentration) {
      const newKey = `${element}|${type}|${concentration}`;
      if (this.currentChartKey === newKey) {
        console.log("Chart already displayed, ignoring duplicate request");
        return;
      }
      if (this.loadingChart) {
        console.log("New chart requested while loading, will cancel previous animation");
      }

      this.loadingChart = true;
      this.chartData = null;
      this.selectedSeries = { element, type, concentration };
      this.currentChartKey = newKey;

      try {
        const { data } = await api.get("/chart_data", {
          params: { type, element, concentration }
        });

        const datasets = [];
        data.curves.forEach(curve => {
          if (curve.data && !curve.error) {
            datasets.push({
              label: curve.label,
              data: curve.data.map(point => ({
                x: point.temperature,
                y: point.value
              })),
              borderColor: curve.color,
              backgroundColor: curve.color + '20',
              fill: false,
              tension: 0.1,
              pointRadius: 2,
              pointHoverRadius: 5
            });
          }
        });

        this.chartData = {
          datasets,
          element: data.element,
          concentration: data.concentration,
          y_label: data.y_label
        };

        this.chartKey++; // Force chart to re-render
      } catch (e) {
        console.error(e);
        this.error = "Failed to load chart data.";
      } finally {
        this.loadingChart = false;
      }
    },
  },
};
</script>

<style>
.searchpanel { width: 750px; height: 175px; padding-top: 15px; margin: 40px auto 20px; padding-left: 20px; background-image: linear-gradient(0deg, #2D2F35 100px, #26a69a 0px); border-radius: 25px; -webkit-text-fill-color: whitesmoke;  }
.searchbox { width: 700px; margin-top: 20px; display: flex; justify-content: center; flex-direction: row; }
input { padding: 12px; width:700px; -webkit-text-fill-color: rgb(0, 0, 0); border-radius: 10px; border: none; margin-right:20px; }
button { background-color:#26a69a; padding: 12px 20px; -webkit-text-fill-color: whitesmoke; border-radius: 10px; border: none; cursor: pointer; }
.databox { height:auto; width: 1000px; display: flex; justify-content: center; flex-direction: row; align-items: flex-start; gap: 20px; margin: 20px auto 40px; }
.datadisplaybox { width: 1000px; display: flex; flex-direction: column; align-items: stretch; }
.datatitlepanel { min-height:100px; background-color: #2D2F35; border-radius: 25px; width: 100%; color: whitesmoke; margin-bottom:10px; padding: 15px 30px; }
.datapanel { min-height: 200px; background-color: #2D2F35; border-radius: 25px; width: 100%; color: whitesmoke; padding: 16px 0 32px; padding: 15px 30px; }
.badge { background: rgba(255,255,255,0.12); padding: 2px 8px; border-radius: 999px; }
</style>
