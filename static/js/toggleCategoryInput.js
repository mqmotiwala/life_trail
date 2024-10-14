document.addEventListener("DOMContentLoaded", function() {
    function toggleCategoryInput() {
        const existingCategory = document.getElementById('existing_category').value;
        const categoryInput = document.getElementById('category_name');
        if (existingCategory) {
            categoryInput.disabled = true;
            categoryInput.value = "";
        } else {
            categoryInput.disabled = false;
        }
    }

    // Ensure the function is globally accessible for inline event listeners
    window.toggleCategoryInput = toggleCategoryInput;
});