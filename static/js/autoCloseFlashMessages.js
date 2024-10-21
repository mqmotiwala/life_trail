const CLOSE_TIME_MS = 2000;
const FADE_OUT_MS = 1000;

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.opacity = '0';
            setTimeout(function() {
                let bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, FADE_OUT_MS); // Wait for fade-out to complete before closing
        });
    }, CLOSE_TIME_MS);
});