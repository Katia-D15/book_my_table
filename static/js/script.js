/**
 * Displays the edit form for a specific booking.
 */

function showEditForm(bookingId) {
    const confirmed = confirm("Are you sure you want to edit this booking?");
    if (!confirmed) return;

    const allForms = document.querySelectorAll("[id^=edit-form-]");
    allForms.forEach(form => form.style.display="none");

    const formToShow = document.getElementById(`edit-form-${bookingId}`)
    if (formToShow) {
        formToShow.style.display = "block";
    }
}