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
      </div>
    </div>

    <div class="databox">
      <div class="datadisplaybox">
        <div class="datatitlepanel">
          <h2 v-if="selectedSeries">
            {{ selectedSeries.element + ' ' + selectedSeries.concentration + '% doped : ' + prettyType(selectedSeries.type) }}
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
          
          <!-- Search results -->
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
import TemperatureChart from '../components/TemperatureChart.vue';
const api = axios.create({ baseURL: "/api" });

export default {
  components: {
    TemperatureChart
  },
  data() {
    return {
      // search
      searchTerm: "",
      results: [],        // [{ element, types: [{type, file_count}] }]
      error: "",
      loading: false,

      // series browsing
      chosenElement: "",
      chosenType: "",
      expandedKey: "",    // key is {element,type} 
      loadingSeriesKey: "",
      series: [],         // [{ concentration, heating_file, cooling_file, has_both, y_label, sample_points?, error? }]
      selectedSeries: null, // series is {element, type, concentration}

      // chart data
      chartData: null,
      chartKey: 0,
      loadingChart: false,
      currentChartKey: ""
    };
  },
  mounted() {
    // Can implement this later: load all dopants initially (currently empty)
    this.searchDopants();
  },
  methods: {
    prettyType(t) {
      // Convert file text "resistance_temp" to prettier "Resistance Temperature Data"
      return t.replace(/_/g, " ").split(" ").map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(" ") + " Data";
    },
    async searchDopants() {
      this.loading = true;
      this.error = "";
      this.results = [];
      this.expandedKey = "";
      this.series = [];
      this.selectedSeries = null;
      try {
        const { data } = await api.get("/search_dopants", { params: { q: this.searchTerm }});
        if (Array.isArray(data)) {
          this.results = data;
        } else if (data && data.error) {
          this.error = data.error; // if data returns error, show this in the backend console
        } else {
          this.results = [];
        }
      } catch (e) {
        console.error(e);
        // surface HTTP payload if present
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
      // Prevents multiple calls for the same data
      const newKey = `${element}|${type}|${concentration}`;

      // If this exact chart is already displayed, ignore the request
      if (this.currentChartKey === newKey) {
        console.log("Chart already displayed, ignoring duplicate request");
        return;
      }

      // If loading a different chart, let it proceed (cancels previous animation)
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

        // Convert API data to Chart.js format
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
              backgroundColor: curve.color + '20', // some transparency
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

        console.log("Chart data set:", this.chartData); // Debug chart data set
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
.datatitlepanel { min-height:150px; background-color: #2D2F35; border-radius: 25px; width: 100%; color: whitesmoke; margin-bottom:10px; padding: 15px 30px; }
.datapanel { min-height: 200px; background-color: #2D2F35; border-radius: 25px; width: 100%; color: whitesmoke; padding: 16px 0 32px; padding: 15px 30px; }
</style>
