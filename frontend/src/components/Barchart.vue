<script setup>
import { ref, watch, onMounted } from 'vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const props = defineProps({
  labels: Array,
  data: Array,
  label: String,
  tooltips: Array
})

const canvas = ref(null)
let chartInstance = null

const drawchart = () => {
  if (chartInstance) {
    chartInstance.destroy()
    }   
    
  chartInstance = new Chart(canvas.value, {
      type: 'bar',
      data: {
        labels: props.labels,
        datasets: [{
            label: props.label,
            data: props.data,
        }]
    },
    options: {
        plugins: {
        tooltip: {
          callbacks: {
            afterLabel: function (context) {
              const index = context.dataIndex
              const date = props.tooltips?.[index] 
              return date ? `Date: ${date}` : ''
            }
          }
        }
      },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    precision: 0
          }
        }
      }
    }
  })
}

onMounted(drawchart)
watch(() => [props.labels, props.data], drawchart)
</script>

<template>
    <div>
        <canvas ref="canvas"></canvas>
    </div>
</template>