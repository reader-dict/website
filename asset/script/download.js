const subscription_end = document.getElementById("subscription-end");
const words_count = document.getElementById("words-count");

function updateDetails() {
	const words = Number.parseInt(words_count.getAttribute("data-value"));

	words_count.innerHTML = words.toLocaleString("en");

	if (subscription_end) {
		const end = new Date(subscription_end.getAttribute("data-end"));

		// 1 month expiricy
		end.setMonth(end.getMonth() + 1);

		subscription_end.innerHTML = new Intl.DateTimeFormat("en", {
			dateStyle: "full",
			timeStyle: "long",
		}).format(end);
	}
}

document.addEventListener("DOMContentLoaded", () => {
	updateDetails();
});
