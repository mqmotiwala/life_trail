document.addEventListener("DOMContentLoaded", function() {
    async function fetchActivities(categoryId) {
        const activitySelect = document.getElementById('activity');
        activitySelect.innerHTML = '<option value="" disabled selected>Loading activities...</option>';
        activitySelect.disabled = true;

        try {
            const response = await fetch(`/get_activities?category_id=${categoryId}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const activities = await response.json();

            activitySelect.innerHTML = '<option value="" disabled selected>Select an activity</option>';
            activities.forEach(activity => {
                const option = document.createElement('option');
                option.value = activity.id;
                option.textContent = activity.name;
                activitySelect.appendChild(option);
            });
            activitySelect.disabled = false;
        } catch (error) {
            console.error('There was a problem fetching activities:', error);
            activitySelect.innerHTML = '<option value="" disabled selected>Error loading activities</option>';
        }
    }

    // Ensure the function is globally accessible for inline event listeners
    window.fetchActivities = fetchActivities;
});