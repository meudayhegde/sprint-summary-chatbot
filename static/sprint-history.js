/**
 * Sprint History JavaScript - Handles sprint history table and report downloads
 */

// Load sprint history when the view is switched
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to Sprint History nav item
    const sprintHistoryNav = document.querySelector('[data-view="sprint-history"]');
    if (sprintHistoryNav) {
        sprintHistoryNav.addEventListener('click', function() {
            loadSprintHistory();
        });
    }
});

async function loadSprintHistory() {
    const loadingSpinner = document.getElementById('sprint-loading');
    const tableContainer = document.getElementById('sprint-table-container');
    
    try {
        // Show loading
        if (loadingSpinner) loadingSpinner.style.display = 'block';
        if (tableContainer) tableContainer.style.display = 'none';
        
        // Fetch sprint list
        const response = await fetch('/api/sprint-history/list');
        
        if (!response.ok) {
            throw new Error('Failed to fetch sprint history');
        }
        
        const sprints = await response.json();
        
        // Populate table
        populateSprintTable(sprints);
        
        // Hide loading and show table
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        if (tableContainer) tableContainer.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading sprint history:', error);
        
        if (loadingSpinner) {
            loadingSpinner.innerHTML = `
                <div style="color: #f56565;">
                    <p>Error loading sprint history</p>
                    <p style="font-size: 14px; margin-top: 8px;">${error.message}</p>
                </div>
            `;
        }
    }
}

function populateSprintTable(sprints) {
    const tbody = document.getElementById('sprint-history-tbody');
    
    if (!tbody) return;
    
    // Clear existing content
    tbody.innerHTML = '';
    
    if (sprints.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 40px; color: #718096;">
                    No sprint history available
                </td>
            </tr>
        `;
        return;
    }
    
    // Add rows for each sprint
    sprints.forEach(sprint => {
        const row = document.createElement('tr');
        
        // Format dates
        const startDate = new Date(sprint.sprint_start).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        });
        const endDate = new Date(sprint.sprint_end).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        });
        
        // Determine delivery percentage color
        let deliveryClass = 'low';
        if (sprint.delivery_percentage >= 80) {
            deliveryClass = 'good';
        } else if (sprint.delivery_percentage >= 60) {
            deliveryClass = 'medium';
        }
        
        // Build row HTML
        row.innerHTML = `
            <td>
                <span class="sprint-id">${sprint.sprint_id}</span>
            </td>
            <td>
                <div class="sprint-duration">
                    ${startDate}<br/>to<br/>${endDate}
                </div>
            </td>
            <td>
                <span class="stat-value">${sprint.total_items}</span>
            </td>
            <td>
                <span class="stat-value">${sprint.completed_items}</span>
            </td>
            <td>
                <div class="sprint-stats">
                    <span class="stat-value">${sprint.completed_points.toFixed(0)}</span>
                    <span style="color: #a0aec0;">/</span>
                    <span style="color: #718096;">${sprint.planned_points.toFixed(0)}</span>
                </div>
            </td>
            <td>
                <span class="delivery-percentage ${deliveryClass}">
                    ${sprint.delivery_percentage.toFixed(1)}%
                </span>
            </td>
            <td>
                <span class="stat-value">${sprint.team_size}</span>
            </td>
            <td>
                <div class="team-members-cell" title="${sprint.team_members}">
                    ${sprint.team_members}
                </div>
            </td>
            <td>
                <button 
                    class="download-btn" 
                    onclick="downloadSprintReport('${sprint.sprint_id}')"
                    title="Download comprehensive sprint report"
                >
                    <span class="icon">📥</span>
                    <span>Download Report</span>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

async function downloadSprintReport(sprintId) {
    try {
        // Find the download button and disable it
        const button = event.target.closest('.download-btn');
        if (button) {
            button.disabled = true;
            button.innerHTML = `
                <span class="icon">⏳</span>
                <span>Generating...</span>
            `;
        }
        
        // Fetch the report
        const response = await fetch(`/api/sprint-history/download/${sprintId}`);
        
        if (!response.ok) {
            throw new Error('Failed to generate report');
        }
        
        // Get the blob
        const blob = await response.blob();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${sprintId}_Sprint_Report.docx`;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Show success message
        if (button) {
            button.innerHTML = `
                <span class="icon">✅</span>
                <span>Downloaded!</span>
            `;
            
            // Reset button after 2 seconds
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = `
                    <span class="icon">📥</span>
                    <span>Download Report</span>
                `;
            }, 2000);
        }
        
    } catch (error) {
        console.error('Error downloading report:', error);
        
        // Show error
        const button = event.target.closest('.download-btn');
        if (button) {
            button.innerHTML = `
                <span class="icon">❌</span>
                <span>Error</span>
            `;
            
            // Reset button after 2 seconds
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = `
                    <span class="icon">📥</span>
                    <span>Download Report</span>
                `;
            }, 2000);
        }
        
        alert(`Failed to download report: ${error.message}`);
    }
}
