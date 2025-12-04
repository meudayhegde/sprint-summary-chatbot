/**
 * Dashboard JavaScript - Handles dashboard data fetching and visualization
 */

// Navigation handling
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    loadDashboard();
});

function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const view = this.getAttribute('data-view');
            switchView(view);
            
            // Update active state
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function switchView(view) {
    const views = ['dashboard-view', 'sprint-history-view', 'chatbot-view'];
    const titles = {
        'dashboard': 'Dashboard',
        'sprint-history': 'Sprint History',
        'chatbot': 'Chatbot'
    };
    const subtitles = {
        'dashboard': 'Comprehensive sprint metrics and visualizations',
        'sprint-history': 'Historical sprint data and trends',
        'chatbot': 'AI-powered sprint analytics assistant'
    };
    
    // Hide all views
    views.forEach(v => {
        const element = document.getElementById(v);
        if (element) element.style.display = 'none';
    });
    
    // Show selected view
    const selectedView = document.getElementById(view + '-view');
    if (selectedView) selectedView.style.display = 'block';
    
    // Update header
    document.getElementById('page-title').textContent = titles[view];
    document.getElementById('page-subtitle').textContent = subtitles[view];
    
    // Load dashboard data if switching to dashboard
    if (view === 'dashboard') {
        loadDashboard();
    }
}

async function loadDashboard() {
    try {
        await Promise.all([
            loadKPIs(),
            loadStateDistribution(),
            loadVelocityChart(),
            loadCycleTimeAnalysis(),
            loadBugsBreakdown(),
            loadWorkloadDistribution(),
            loadSpilloverOverview(),
            loadRawData()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// KPIs Section
async function loadKPIs() {
    try {
        const response = await fetch('/api/dashboard/kpis');
        const data = await response.json();
        
        const kpiGrid = document.getElementById('kpi-grid');
        kpiGrid.innerHTML = '';
        
        const kpis = [
            data.sprint_velocity,
            data.delivery_percentage,
            data.bug_count,
            data.spillover_percentage,
            data.avg_cycle_time
        ];
        
        kpis.forEach(kpi => {
            const card = document.createElement('div');
            card.className = `kpi-card ${kpi.indicator}`;
            card.innerHTML = `
                <div class="kpi-label">${kpi.label}</div>
                <div class="kpi-value">
                    <span>${kpi.value}</span>
                    <span class="kpi-indicator ${kpi.indicator}"></span>
                </div>
            `;
            kpiGrid.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading KPIs:', error);
    }
}

// State Distribution Chart
async function loadStateDistribution() {
    try {
        const response = await fetch('/api/dashboard/state-distribution');
        const data = await response.json();
        
        const trace = {
            x: data.states,
            y: data.counts,
            type: 'bar',
            text: data.percentages.map(p => `${p}%`),
            textposition: 'outside',
            marker: {
                color: '#667eea',
                line: {
                    color: '#764ba2',
                    width: 1.5
                }
            }
        };
        
        const layout = {
            title: 'Items per State',
            xaxis: { title: 'State' },
            yaxis: { title: 'Number of Items' },
            showlegend: false,
            height: 400
        };
        
        Plotly.newPlot('state-distribution-chart', [trace], layout, {responsive: true});
    } catch (error) {
        console.error('Error loading state distribution:', error);
    }
}

// Velocity Chart
async function loadVelocityChart() {
    try {
        const response = await fetch('/api/dashboard/velocity');
        const data = await response.json();
        
        const trace1 = {
            x: data.sprints,
            y: data.planned,
            name: 'Planned Points',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#667eea', width: 3 },
            marker: { size: 10 }
        };
        
        const trace2 = {
            x: data.sprints,
            y: data.completed,
            name: 'Completed Points',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#48bb78', width: 3 },
            marker: { size: 10 }
        };
        
        const layout = {
            title: 'Sprint Velocity: Planned vs Completed',
            xaxis: { title: 'Sprint' },
            yaxis: { title: 'Story Points' },
            height: 400,
            hovermode: 'x unified'
        };
        
        Plotly.newPlot('velocity-chart', [trace1, trace2], layout, {responsive: true});
    } catch (error) {
        console.error('Error loading velocity chart:', error);
    }
}

// Cycle Time Analysis
async function loadCycleTimeAnalysis() {
    try {
        const response = await fetch('/api/dashboard/cycle-time');
        const data = await response.json();
        
        // Box Plot
        if (data.box_plot && data.box_plot.length > 0) {
            const boxTraces = data.box_plot.map(item => ({
                y: item.cycle_times,
                name: item.state,
                type: 'box',
                boxmean: 'sd'
            }));
            
            const boxLayout = {
                title: 'Cycle Time Distribution by State',
                yaxis: { title: 'Cycle Time (Days)' },
                height: 400,
                showlegend: true
            };
            
            Plotly.newPlot('cycle-time-box-chart', boxTraces, boxLayout, {responsive: true});
        }
        
        // Scatter Plot
        if (data.scatter && data.scatter.story_points.length > 0) {
            const scatterTrace = {
                x: data.scatter.story_points,
                y: data.scatter.cycle_times,
                mode: 'markers',
                type: 'scatter',
                text: data.scatter.titles,
                marker: {
                    size: 12,
                    color: '#667eea',
                    line: {
                        color: 'white',
                        width: 2
                    }
                }
            };
            
            // Add trendline
            const xMean = data.scatter.story_points.reduce((a, b) => a + b, 0) / data.scatter.story_points.length;
            const yMean = data.scatter.cycle_times.reduce((a, b) => a + b, 0) / data.scatter.cycle_times.length;
            
            let numerator = 0;
            let denominator = 0;
            for (let i = 0; i < data.scatter.story_points.length; i++) {
                numerator += (data.scatter.story_points[i] - xMean) * (data.scatter.cycle_times[i] - yMean);
                denominator += Math.pow(data.scatter.story_points[i] - xMean, 2);
            }
            const slope = numerator / denominator;
            const intercept = yMean - slope * xMean;
            
            const minX = Math.min(...data.scatter.story_points);
            const maxX = Math.max(...data.scatter.story_points);
            
            const trendline = {
                x: [minX, maxX],
                y: [slope * minX + intercept, slope * maxX + intercept],
                mode: 'lines',
                type: 'scatter',
                name: `Trendline (r=${data.correlation.toFixed(3)})`,
                line: {
                    color: '#f56565',
                    width: 2,
                    dash: 'dash'
                }
            };
            
            const scatterLayout = {
                title: 'Story Points vs Cycle Time',
                xaxis: { title: 'Story Points' },
                yaxis: { title: 'Cycle Time (Days)' },
                height: 400,
                showlegend: true
            };
            
            Plotly.newPlot('cycle-time-scatter-chart', [scatterTrace, trendline], scatterLayout, {responsive: true});
        }
    } catch (error) {
        console.error('Error loading cycle time analysis:', error);
    }
}

// Bugs Breakdown
async function loadBugsBreakdown() {
    try {
        const response = await fetch('/api/dashboard/bugs');
        const data = await response.json();
        
        // Severity Pie Chart
        if (data.severity.labels.length > 0) {
            const severityTrace = {
                labels: data.severity.labels,
                values: data.severity.values,
                type: 'pie',
                marker: {
                    colors: ['#f56565', '#ed8936', '#ecc94b', '#48bb78']
                }
            };
            
            const severityLayout = {
                title: `Bug Severity Distribution (Total: ${data.total_bugs})`,
                height: 400
            };
            
            Plotly.newPlot('bugs-severity-chart', [severityTrace], severityLayout, {responsive: true});
        }
        
        // Bugs by Area Bar Chart
        if (data.by_area.areas.length > 0) {
            const areaTrace = {
                x: data.by_area.areas,
                y: data.by_area.counts,
                type: 'bar',
                marker: {
                    color: '#f56565'
                }
            };
            
            const areaLayout = {
                title: 'Bugs per Area',
                xaxis: { title: 'Area' },
                yaxis: { title: 'Number of Bugs' },
                height: 400
            };
            
            Plotly.newPlot('bugs-area-chart', [areaTrace], areaLayout, {responsive: true});
        }
    } catch (error) {
        console.error('Error loading bugs breakdown:', error);
    }
}

// Workload Distribution
async function loadWorkloadDistribution() {
    try {
        const response = await fetch('/api/dashboard/workload');
        const data = await response.json();
        
        // Stacked Bar Chart
        const devTrace = {
            x: data.stacked_bar.assignees,
            y: data.stacked_bar.dev_hours,
            name: 'Dev Hours',
            type: 'bar',
            marker: { color: '#667eea' }
        };
        
        const qaTrace = {
            x: data.stacked_bar.assignees,
            y: data.stacked_bar.qa_hours,
            name: 'QA Hours',
            type: 'bar',
            marker: { color: '#48bb78' }
        };
        
        const stackedLayout = {
            title: 'Hours per Assignee',
            xaxis: { title: 'Assignee' },
            yaxis: { title: 'Hours' },
            barmode: 'stack',
            height: 400
        };
        
        Plotly.newPlot('workload-bar-chart', [devTrace, qaTrace], stackedLayout, {responsive: true});
        
        // Pie Chart
        if (data.pie_data.length > 0) {
            const pieTrace = {
                labels: data.pie_data.map(d => d.assignee),
                values: data.pie_data.map(d => d.percentage),
                type: 'pie',
                textinfo: 'label+percent'
            };
            
            const pieLayout = {
                title: 'Workload Distribution %',
                height: 400
            };
            
            Plotly.newPlot('workload-pie-chart', [pieTrace], pieLayout, {responsive: true});
        }
        
        // Heatmap
        if (data.heatmap.assignees.length > 0) {
            const heatmapTrace = {
                x: data.heatmap.areas,
                y: data.heatmap.assignees,
                z: data.heatmap.values,
                type: 'heatmap',
                colorscale: 'Blues'
            };
            
            const heatmapLayout = {
                title: 'Assignee x Area Matrix',
                xaxis: { title: 'Area' },
                yaxis: { title: 'Assignee' },
                height: 400
            };
            
            Plotly.newPlot('workload-heatmap-chart', [heatmapTrace], heatmapLayout, {responsive: true});
        }
    } catch (error) {
        console.error('Error loading workload distribution:', error);
    }
}

// Spillover Overview
async function loadSpilloverOverview() {
    try {
        const response = await fetch('/api/dashboard/spillover');
        const data = await response.json();
        
        // Chart
        if (data.chart.areas.length > 0) {
            const trace = {
                x: data.chart.areas,
                y: data.chart.story_points,
                type: 'bar',
                marker: { color: '#ed8936' },
                text: data.chart.story_points.map(p => `${p} pts`),
                textposition: 'outside'
            };
            
            const layout = {
                title: `Spillover Story Points by Area (Total: ${data.total_points_spilled} pts)`,
                xaxis: { title: 'Area' },
                yaxis: { title: 'Story Points' },
                height: 400
            };
            
            Plotly.newPlot('spillover-chart', [trace], layout, {responsive: true});
        }
        
        // Table
        if (data.table.length > 0) {
            const table = document.getElementById('spillover-table');
            
            let html = `
                <thead>
                    <tr>
                        <th>Ticket ID</th>
                        <th>Title</th>
                        <th>Area</th>
                        <th>Story Points</th>
                        <th>Assignee</th>
                        <th>Carried Over From</th>
                    </tr>
                </thead>
                <tbody>
            `;
            
            data.table.forEach(row => {
                html += `
                    <tr>
                        <td>${row.ticket_id}</td>
                        <td>${row.title}</td>
                        <td>${row.area}</td>
                        <td>${row.story_points}</td>
                        <td>${row.assignee}</td>
                        <td>${row.carried_over_from || '-'}</td>
                    </tr>
                `;
            });
            
            html += '</tbody>';
            table.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading spillover overview:', error);
    }
}

// Raw Data Summary
async function loadRawData() {
    try {
        const response = await fetch('/api/dashboard/raw-data');
        const data = await response.json();
        
        // Sprint Summary Table
        if (data.sprint_summary.length > 0) {
            const table = document.getElementById('sprint-summary-table');
            let html = `
                <thead>
                    <tr>
                        <th>Sprint</th>
                        <th>Total Items</th>
                        <th>Stories</th>
                        <th>Bugs</th>
                        <th>Tasks</th>
                        <th>Completed</th>
                        <th>Total Points</th>
                        <th>Completed Points</th>
                    </tr>
                </thead>
                <tbody>
            `;
            
            data.sprint_summary.forEach(row => {
                html += `
                    <tr>
                        <td>${row.sprint_id}</td>
                        <td>${row.total_items}</td>
                        <td>${row.stories}</td>
                        <td>${row.bugs}</td>
                        <td>${row.tasks}</td>
                        <td>${row.completed}</td>
                        <td>${row.total_points}</td>
                        <td>${row.completed_points}</td>
                    </tr>
                `;
            });
            
            html += '</tbody>';
            table.innerHTML = html;
        }
        
        // Type Summary Table
        if (data.type_summary.length > 0) {
            const table = document.getElementById('type-summary-table');
            let html = `
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Count</th>
                        <th>Completed</th>
                        <th>In Progress</th>
                        <th>To Do</th>
                        <th>Total Points</th>
                    </tr>
                </thead>
                <tbody>
            `;
            
            data.type_summary.forEach(row => {
                html += `
                    <tr>
                        <td>${row.type}</td>
                        <td>${row.count}</td>
                        <td>${row.completed}</td>
                        <td>${row.in_progress}</td>
                        <td>${row.todo}</td>
                        <td>${row.total_points}</td>
                    </tr>
                `;
            });
            
            html += '</tbody>';
            table.innerHTML = html;
        }
        
        // Team Summary Table
        if (data.team_summary.length > 0) {
            const table = document.getElementById('team-summary-table');
            let html = `
                <thead>
                    <tr>
                        <th>Assignee</th>
                        <th>Role</th>
                        <th>Total Items</th>
                        <th>Completed</th>
                        <th>Total Points</th>
                        <th>Completed Points</th>
                        <th>Total Hours</th>
                    </tr>
                </thead>
                <tbody>
            `;
            
            data.team_summary.forEach(row => {
                html += `
                    <tr>
                        <td>${row.assignee}</td>
                        <td>${row.role}</td>
                        <td>${row.total_items}</td>
                        <td>${row.completed}</td>
                        <td>${row.total_points}</td>
                        <td>${row.completed_points}</td>
                        <td>${row.total_hours.toFixed(1)}</td>
                    </tr>
                `;
            });
            
            html += '</tbody>';
            table.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading raw data:', error);
    }
}
