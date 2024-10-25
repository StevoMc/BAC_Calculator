// Helper function to get an element by ID
const getElementById = (id) => document.getElementById(id);

// Function to select a drink and submit the form
function selectDrink(drink) {
	const selectedDrinkInput = getElementById("selected-drink");
	const drinkForm = getElementById("drink-form");
	selectedDrinkInput.value = drink;
	drinkForm.submit();
}

// Function to show loading spinner and hide main content
function showLoading() {
	const mainContent = getElementById("main-content");
	const loadingSpinner = getElementById("loading-spinner");
	mainContent.style.display = "none";
	loadingSpinner.style.display = "block";
}

// Function to confirm resetting drinks
function confirmReset(event) {
	const userConfirmed = confirm(
		"Möchten Sie wirklich alle Getränke zurücksetzen?"
	);
	if (userConfirmed) {
		showLoading();
	} else {
		event.preventDefault(); // Prevent the default form submission
	}
}

// Function to redirect to the history page
function showHistory() {
	window.location.href = "/history";
}

// Function to toggle the display of the custom drink form
function toggleCustomForm() {
	const customForm = getElementById("custom-drink");
	customForm.style.display =
		customForm.style.display === "none" ? "block" : "none";
}

// Adding event listeners to forms for better default prevention
document
	.querySelector("#drink-form")
	.addEventListener("submit", function (event) {
		event.preventDefault(); // Prevent the default form submission
		selectDrink(getElementById("selected-drink").value);
	});

document.querySelector("#reset-form").addEventListener("submit", confirmReset);

// Adding event listeners to input fields for better default prevention
document.querySelector("input").addEventListener("keypress", function (event) {
	// Prevent the form from submitting when pressing enter
	if (event.key === "Enter") {
		event.preventDefault();
	}
});
