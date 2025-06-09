// details_page.js
(function () {
    const links = document.querySelectorAll('.aside-panel .nav-link');
    const panels = document.querySelectorAll('.detail-section');

    // Store a reference to each chart instance, keyed by "<type>-<year>"
    const chartInstances = {
        bar: {},
        pie: {}
    };

    // Helper to slugify a year string (same as Django's slugify)
    function slugify(text) {
        return text.toString().toLowerCase()
            .replace(/\s+/g, '-')      // Replace spaces with -
            .replace(/[^\w\-]+/g, '')   // Remove all non-word chars
            .replace(/\-\-+/g, '-')    // Replace multiple - with single -
            .replace(/^-+/, '')        // Trim - from start of text
            .replace(/-+$/, '');       // Trim - from end of text
    }

    // Show a single panel by id; hide all others
    function showPanel(id) {
        panels.forEach(p => p.id === id
            ? p.classList.remove('d-none')
            : p.classList.add('d-none'));
        // If we just showed the "stat-info" panel, initialize charts
        if (id === 'stat-info') {
            initializeStatisticsCharts();
        }
    }

    // Set up the left-nav linking
    function linking() {
        links.forEach(link => {
            link.addEventListener('click', e => {
                e.preventDefault();
                // remove .active from all, add to this one
                links.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                // show the corresponding panel
                const target = link.dataset.target;
                showPanel(target);
            });
        });
    }

    // Build charts for each year if not already built
    function initializeStatisticsCharts() {
        // Ensure the DOM for stat-tabs is present
        const statPane = document.querySelector('#stat-info');
        if (!statPane) return;

        // Select all year-tab panes
        const tabPanes = statPane.querySelectorAll('.tab-pane');

        tabPanes.forEach(pane => {
            const paneId = pane.id; // e.g. "tab-2023-24"
            const yearSlug = paneId.replace('tab-', ''); // "2023-24"
            const displayYear = pane.querySelector('.card .text-muted').textContent.match(/\(([^)]+)\)/)[1]; // "2023-24"

            // 1) BAR CHART: "Staff & Volunteers"
            const barCanvas = pane.querySelector(`#barChart-${yearSlug}`);
            if (barCanvas && !chartInstances.bar[yearSlug]) {
                // Extract data attributes from the raw Django context:
                // We can find the numeric values by reading the <dd> elements directly.
                // Assuming the order: Deacons, Brothers, Sisters, Lay, PartTime, Volunteers
                const statsList = pane.querySelectorAll('dt, dd');
                // Build a map from label→value
                const dataMap = {};
                statsList.forEach((node, i) => {
                    if (node.tagName.toLowerCase() === 'dt') {
                        const label = node.textContent.trim();
                        const dd = node.nextElementSibling;
                        if (dd && dd.tagName.toLowerCase() === 'dd') {
                            const val = parseInt(dd.textContent.trim(), 10) || 0;
                            dataMap[label] = val;
                        }
                    }
                });

                const barLabels = [
                    'Full-Time Deacons',
                    'Full-Time Brothers',
                    'Full-Time Sisters',
                    'Full-Time Lay Staff',
                    'Part-Time Staff',
                    'Catechist Paid',
                    'Youth Ministry Volunteers',
                    'Volunteers'
                ];
                const barValues = barLabels.map(lbl => dataMap[lbl] ?? 0);

                const barCtx = barCanvas.getContext('2d');
                chartInstances.bar[yearSlug] = new Chart(barCtx, {
                    type: 'bar',
                    data: {
                        labels: barLabels,
                        datasets: [{
                            label: `Staff & Volunteers (${displayYear})`,
                            data: barValues,
                            backgroundColor: [
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)',
                                'rgba(255, 205, 86, 0.6)',
                                'rgba(201, 203, 207, 0.6)'
                            ],
                            borderColor: [
                                'rgba(54, 162, 235, 1)',
                                'rgba(75, 192, 192, 1)',
                                'rgba(153, 102, 255, 1)',
                                'rgba(255, 159, 64, 1)',
                                'rgba(255, 205, 86, 1)',
                                'rgba(201, 203, 207, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        }
                    }
                });
            }

            // 2) PIE CHART: “Census Breakdown” (only if is_censusEstimate = true)
            const pieCanvas = pane.querySelector(`#pieChart-${yearSlug}`);
            if (pieCanvas && !chartInstances.pie[yearSlug]) {
                // Pull out the percentages from the pane
                // We assume that the template put the % fields in the same <dl> as:
                // “% African,” “% African-American,” “% Asian,” “% Hispanic,” “% American-Indian,” “% Other”
                const statsList = pane.querySelectorAll('dt, dd');
                const dataMap = {};
                statsList.forEach((node, i) => {
                    if (node.tagName.toLowerCase() === 'dt') {
                        const label = node.textContent.trim();
                        const dd = node.nextElementSibling;
                        if (dd && dd.tagName.toLowerCase() === 'dd') {
                            // percentages might be decimal strings like "12.34"
                            const raw = dd.textContent.trim().replace('%','').trim();
                            const val = parseFloat(raw) || 0;
                            dataMap[label] = val;
                        }
                    }
                });

                const pieLabels = [
                    '% African',
                    '% African-American',
                    '% Asian',
                    '% Hispanic',
                    '% American-Indian',
                    '% Other'
                ];
                // Only include those labels that are present in dataMap
                const pieData = pieLabels.map(lbl => dataMap[lbl] ?? 0);

                const pieCtx = pieCanvas.getContext('2d');
                chartInstances.pie[yearSlug] = new Chart(pieCtx, {
                    type: 'pie',
                    data: {
                        labels: pieLabels,
                        datasets: [{
                            data: pieData,
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 205, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(201, 203, 207, 0.6)'
                            ],
                            borderColor: [
                                'rgba(255, 99, 132, 1)',
                                'rgba(54, 162, 235, 1)',
                                'rgba(255, 205, 86, 1)',
                                'rgba(75, 192, 192, 1)',
                                'rgba(153, 102, 255, 1)',
                                'rgba(201, 203, 207, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
        });
        // ── NEW: Offertory bar chart ──
        const offCanvas = document.getElementById('offertoryChart');
        if (offCanvas && typeof offertoryYears !== 'undefined' && typeof offertoryIncomes !== 'undefined') {
          const offCtx = offCanvas.getContext('2d');
          new Chart(offCtx, {
            type: 'bar',
            data: {
              labels: offertoryYears,
              datasets: [{
                label: 'Offertory Income',
                data: offertoryIncomes,
                backgroundColor: 'rgba(44, 181, 60, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true
                }
              }
            }
          });
        }
    }

    function init() {
        linking();
    }

    // run init() once the DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
