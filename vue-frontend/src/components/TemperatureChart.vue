<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LogarithmicScale,   //By Cha
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  LogarithmicScale, //By Cha
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'TemperatureChart',
  props: {
    chartData: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      chart: null,
      isDestroying: false,
      lastDataKey: null
    }
  },
  mounted() {
    console.log("TemperatureChart mounted with data:", this.chartData);
    this.$nextTick(() => {
      this.createChart()
    })
  },
  beforeUnmount() {
    this.isDestroying = true
    this.destroyChart()
  },
  watch: {
    chartData: {
      handler() {
        this.updateChart()
      },
      deep: true
    }
  },
  methods: {
    async destroyChart() {
      if (this.chart) {
        try {
          // Cancel current animation
          this.chart.stop()
          if (this.chart.animator) {
            this.chart.animator.stop()
          }

          // Clear pending animation frames
          if (this.chart._animationRequest) {
            cancelAnimationFrame(this.chart._animationRequest)
            this.chart._animationRequest = null
          }

          // Wait to ensure animation frames are cleared
          await new Promise(resolve => setTimeout(resolve, 10));

          // Finally, destroy the chart
          this.chart.destroy()
        } catch (error) {
          console.warn("Error destroying chart:", error)
        } finally {
          this.chart = null
        }
      }
    },
    async createChart() {
      if (this.isDestroying) {
        console.log("Component is being destroyed, skipping chart creation");
        return;
      }

      if (!this.chartData || !this.chartData.datasets) {
        console.log("No chart data available yet");
        return;
      }

      if (!this.$refs.chartCanvas) {
        console.log("Canvas ref not available yet");
        return;
      }

      // Destroy existing chart first
      await this.destroyChart();

      console.log("Creating chart with datasets:", this.chartData.datasets);

      // Debug canvas dimensions
      const canvas = this.$refs.chartCanvas;
      console.log("Canvas dimensions:", {
        width: canvas.width,
        height: canvas.height,
        clientWidth: canvas.clientWidth,
        clientHeight: canvas.clientHeight,
        offsetWidth: canvas.offsetWidth,
        offsetHeight: canvas.offsetHeight
      });

      const ctx = canvas.getContext('2d')

      if (!ctx) {
        console.error("Could not get canvas context");
        return;
      }

      // Additional validation to prevent null context issues
      if (ctx.canvas !== canvas) {
        console.error("Context canvas mismatch");
        return;
      }

      try {
        // Set the data key for tracking
        this.lastDataKey = `${this.chartData.element}-${this.chartData.concentration}-${this.chartData.y_label}`;

        this.chart = new ChartJS(ctx, {
          type: 'line',
          data: {
            datasets: this.chartData.datasets || []
            
             // const EPS = 1e-9;  //By Cha
            //dataset.data = dataset.data.map(p => {
             //if (typeof p === 'number') return p > 0 ? p : null; 
            //return { x: p.x, y: p.y > 0 ? p.y : null} };
            //});

          },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            duration: 750,
            easing: 'easeInOutQuart'
          },
          interaction: {
            mode: 'point',
            intersect: false
          },
          hover: {
            mode: 'point',
            intersect: false
          },
          plugins: {
            legend: {
              position: 'top',
              labels: {
                color: '#ffffff',
                font: {
                  size: 14
                }
              }
            },
            title: {
              display: true,
              text: `${this.chartData?.element || ''} ${this.chartData?.concentration || ''}% - ${this.chartData?.y_label || 'Property'} vs Temperature`,
              color: '#ffffff',
              font: {
                size: 16,
                weight: 'bold'
              }
            },
            tooltip: {
              mode: 'point',
              intersect: false,
              callbacks: {
                title: function(context) {
                  // Show temperature for the hovered point
                  return `Temperature: ${context[0].parsed.x}°C`;
                },
                label: function(context) {
                  // Show the value and dataset label for the single point
                  return `${context.dataset.label}: ${context.parsed.y}`;
                }
              }
            }
          },
          scales: {
            x: {
              type: 'linear',
              display: true,
              title: {
                display: true,
                text: 'Temperature (°C)',
                color: '#ffffff',
                font: {
                  size: 14
                }
              },
              ticks: {
                color: '#ffffff'
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            },
            y: {
              type: 'logarithmic',
              display: true,
              title: {
                display: true,
                text: this.chartData?.y_label || 'Property Value',
                color: '#ffffff',
                font: {
                  size: 14
                }
              },
              ticks: {
                color: '#ffffff',   //by Cha
                callback: (value) => {  // value here is the tick value (number). Show only 1, 10, 100, ...
                  const log10 = Math.log10(value);
                  return Number.isInteger(log10) ? `10^${log10}` : '';
                }
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            }
          },
          elements: {
            point: {
              radius: 2,
              hoverRadius: 5
            },
            line: {
              tension: 0.1
            }
          }
        }
      })
      console.log("Chart created successfully");
      } catch (error) {
        console.error("Error creating chart:", error);
      }
    },
    async updateChart() {
      if (this.isDestroying) {
        console.log("Component is being destroyed, skipping chart update");
        return;
      }

      console.log("updateChart called", { hasChart: !!this.chart, hasData: !!this.chartData });

      // Generate a key for the current data to detect changes
      const currentDataKey = this.chartData ?
        `${this.chartData.element}-${this.chartData.concentration}-${this.chartData.y_label}` : null;

      // If we have data but no chart, create one
      if (!this.chart && this.chartData && this.chartData.datasets) {
        console.log("Creating chart from updateChart");
        this.lastDataKey = currentDataKey;
        await this.createChart();
        return;
      }

      // If we have both chart and data
      if (this.chart && this.chartData) {
        // If data has changed, always recreate the chart to avoid animation conflicts
        if (this.lastDataKey !== currentDataKey) {
          console.log("Chart data changed, recreating chart for safety");
          this.lastDataKey = currentDataKey;
          await this.createChart();
          return;
        }

        // If same data, try to update (though this shouldn't happen often)
        try {
          // Check if chart is still valid
          if (!this.chart.ctx || !this.chart.canvas) {
            console.log("Chart context is invalid, recreating chart");
            await this.createChart();
            return;
          }

          console.log("Updating existing chart with same data");
          this.chart.data.datasets = this.chartData.datasets || [];
          this.chart.update('none'); // Use no animation for same-data updates
        } catch (error) {
          console.error("Error updating chart:", error);
          await this.createChart();
        }
      }
    }
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
  background-color: rgba(45, 47, 53, 0.9);
  border-radius: 12px;
  padding: 20px;
}

canvas {
  max-height: 100%;
  max-width: 100%;
}
</style>
