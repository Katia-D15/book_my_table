const alerts = document.querySelectorAll('.alert');

/**
 * Displays the edit form for a specific booking.
 * 
 * Requests user confirmation before proceeding.
 * Ensures that only the form corresponding to the booking is displayed,
 * hiding all other editing forms.
 */

function showEditForm(bookingId) {
    const confirmed = confirm("Are you sure you want to edit this booking?");
    if (!confirmed) return;

    const allForms = document.querySelectorAll("[id^=edit-form-]");
    allForms.forEach(form => form.style.display="none");

    const formToShow = document.getElementById(`edit-form-${bookingId}`);
    if (formToShow) {
        formToShow.classList.remove("d-none");
        formToShow.style.display = "block";
    }
}

/**
 * Automatically hides success and info alert messages after 3.5 seconds.
 * 
 * Applies to elements with the 'alert-success' or 'alert-info' classes.
 */
alerts.forEach((alert) => {
    if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
        setTimeout(() => {
            const alertInstance = new bootstrap.Alert(alert);
            alertInstance.close();
        }, 3500);
    }
});
