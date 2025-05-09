function createChart(id, label, chartType, data) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    new Chart(ctx, {
        type: chartType,
        data: {
            labels: data.labels,
            datasets: [{
                label: label,
                data: data.values,
                backgroundColor: [
                    "#4e73df",
                    "#1cc88a",
                    "#36b9cc",
                    "#f6c23e",
                    "#e74a3b",
                    "#858796",
                    "#5a5c69",
                    "#36b9cc",
                    "#1cc88a",
                    "#4e73df",
                    "#f6c23e",
                    "#e74a3b",
                    "#858796",
                    "#5a5c69",
                ],
            }]
        },
        options: {
            responsive: true,
            aspectRatio: 5,
            plugins: {
                legend: { display: chartType === "pie" },
                datalabels: chartType === "pie" ? {
                    formatter: (value, context) => {
                        const dataArr = context.chart.data.datasets[0].data;
                        const total = dataArr.reduce((acc, val) => acc + val, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${percentage}%`;
                    },
                    color: "#fff",
                    font: {
                        weight: 'bold'
                    }
                } : false
            }
        },
        plugins: chartType === "pie" ? [ChartDataLabels] : []
    })
}

document.addEventListener("DOMContentLoaded", function () {
    const chartsConfig = [
        { id: "userFieldChart", label: "Field of Study", type: "bar" },
        { id: "educationLevelChart", label: "Education Level", type: "bar" },
        { id: "activityStatusChart", label: "Activity Status", type: "pie" },
        { id: "documentKeywordsChart", label: "Document Keywords", type: "bar" },
        { id: "documentStatsChart", label: "Document Stats", type: "bar" },
        { id: "authorStatsChart", label: "Author Stats", type: "bar" },
        { id: "sessionsByDayChart", label: "Sessions by Day", type: "bar" },
    ];

    chartsConfig.forEach(({ id, label, type }) => {
        const el = document.getElementById(id);
        if (el && el.dataset.chart) {
            const data = JSON.parse(el.dataset.chart);
            createChart(id, label, type, data);
        }
    });
});
