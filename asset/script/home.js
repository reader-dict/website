const select_lang_src = document.getElementById("lang-src");
const select_lang_dst = document.getElementById("lang-dst");
const selected_lang_src = document.querySelectorAll("#selected-lang-src");
const selected_lang_dst = document.querySelectorAll("#selected-lang-dst");
const price = document.getElementById("price");
const price_purchase = document.getElementById("price-purchase");
const last_updated = document.getElementById("last-updated");
const words_count = document.getElementById("words-count");
const total_words_count = document.getElementById("total-words-count");
const total_dicts_count = document.getElementById("total-dict-count");
const total_langs_count = document.getElementById("total-lang-count");
const paypal_button_subscription = document.getElementById(
	"paypal-button-subscription",
);
const paypal_button_purchase = document.getElementById(
	"paypal-button-purchase",
);
const missing_mobi = document.getElementById("missing-mobi");
const monolingual = document.getElementById("this-is-monolingual");

// Updated in fetchMetrics() on document fully loaded
metrics = {};

function get(object, path, default_value) {
	// Source: https://edvins.io/get-deeply-nested-object-in-javascript
	if (!Object.keys(object).length) {
		return default_value;
	}

	const pathArray = Array.isArray(path) ? path : path.split(".");
	let result = object;

	for (let i = 0; i < pathArray.length; i++) {
		const value = pathArray[i];
		if (typeof result === "object" && result !== null && value in result) {
			result = result[value];
		} else {
			return default_value;
		}
	}
	return result;
}

function adaptLangDstOptions() {
	const lang_src = currentLangSrc();
	const intl_locale = new Intl.Locale("en");

	// Clean-up the current list
	for (row of [...select_lang_dst.children]) {
		select_lang_dst.removeChild(row);
	}

	for (const lang_dst in metrics[lang_src]) {
		const lang_name = new Intl.DisplayNames([intl_locale.language], {
			type: "language",
		}).of(lang_dst);
		const option = document.createElement("option");

		option.value = lang_dst;
		option.innerHTML = `[${lang_dst.toUpperCase()}] ${toTitle(lang_name)}`;
		select_lang_dst.appendChild(option);
	}

	select_lang_dst.options[0].selected = true;
}

function currentLangSrc() {
	return select_lang_src.options[select_lang_src.selectedIndex].value;
}

function currentLangDst() {
	return select_lang_dst.options[select_lang_dst.selectedIndex].value;
}

function eventPayPalApproved(kind, event) {
	const options = {
		method: "POST",
		body: JSON.stringify(event),
		headers: { "Content-Type": "application/json" },
	};

	fetch("/api/v1/order", options)
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			if (data.status === "ok") {
				document.location = `/${data.url}`;
			} else {
				console.error(data);
			}
		});
}

function fetchMetrics() {
	fetch("/api/v1/dictionaries")
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			metrics = data;
			updateGlobals();
			adaptLangDstOptions();
			pickLangsFromAnchor();
			updateDetails();
		});
}

function getLastUpdated(current_lang_src, current_lang_dst) {
	return get(
		metrics,
		`${current_lang_src}.${current_lang_dst}.updated`,
		"0000-00-00",
	);
}

function getPlanId(current_lang_src, current_lang_dst) {
	return get(metrics, `${current_lang_src}.${current_lang_dst}.plan_id`, "");
}

function getPrice(current_lang_src, current_lang_dst) {
	return Number.parseFloat(
		get(metrics, `${current_lang_src}.${current_lang_dst}.price`, 0.0),
	);
}

function getPricePurchase(current_lang_src, current_lang_dst) {
	return Number.parseFloat(
		get(metrics, `${current_lang_src}.${current_lang_dst}.price_purchase`, 0.0),
	);
}

function getProgress(current_lang_src, current_lang_dst) {
	return get(metrics, `${current_lang_src}.${current_lang_dst}.progress`, "");
}

function getWordsCount(current_lang_src, current_lang_dst) {
	return get(metrics, `${current_lang_src}.${current_lang_dst}.words`, 0);
}

function pickLangsFromAnchor() {
	const [_, anchor] = new URL(document.location).href.split("#", 2);

	if (anchor) {
		const [lang_src, lang_dst] = anchor.split("-");

		for (row of [...select_lang_src.children]) {
			if (row.value === lang_src) {
				row.selected = true;
				break;
			}
		}
		for (row of [...select_lang_dst.children]) {
			if (row.value === lang_dst) {
				row.selected = true;
				break;
			}
		}

		document.location = "#subscribe";
	}
}

function toTitle(str) {
	// Source: https://stackoverflow.com/a/64910248/1117028
	let upper = true;
	let newStr = "";
	for (let i = 0, l = str.length; i < l; i++) {
		if (str[i] === " ") {
			upper = true;
			newStr += " ";
			continue;
		}
		newStr += upper
			? str[i].toLocaleUpperCase("en")
			: str[i].toLocaleLowerCase("en");
		upper = false;
	}
	return newStr;
}

function updateDetails() {
	const current_lang_src = currentLangSrc();
	const current_lang_dst = currentLangDst();
	const formatter = new Intl.NumberFormat("en", {
		style: "currency",
		currency: "EUR",
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	});

	[...selected_lang_src].map((el) => {
		el.innerHTML =
			current_lang_src === "all"
				? `${current_lang_src}-to`
				: current_lang_src.toUpperCase();
	});
	[...selected_lang_dst].map((el) => {
		el.innerHTML = current_lang_dst.toUpperCase();
	});
	words_count.innerHTML = getWordsCount(
		current_lang_src,
		current_lang_dst,
	).toLocaleString("en");
	last_updated.innerHTML = getLastUpdated(current_lang_src, current_lang_dst);
	price.innerHTML = formatter.format(
		getPrice(current_lang_src, current_lang_dst),
	);
	price_purchase.innerHTML = formatter.format(
		getPricePurchase(current_lang_src, current_lang_dst),
	);

	if (current_lang_src === current_lang_dst) {
		const link = monolingual.querySelector("a");
		link.href = `/download/${current_lang_src}`;
		monolingual.style.display = "block";
	} else {
		monolingual.style.display = "none";
	}

	missing_mobi.style.display = getProgress(
		current_lang_src,
		current_lang_dst,
	).includes("mobi")
		? "block"
		: "none";

	updatePaypalButton(current_lang_src, current_lang_dst);
}

function updateGlobals() {
	const langs = new Set();
	let total_dicts = 0;
	let total_words = 0;

	for (const lang_src in metrics) {
		langs.add(lang_src);
		for (const lang_dst in metrics[lang_src]) {
			langs.add(lang_dst);
			total_dicts += 1;
			total_words += metrics[lang_src][lang_dst].words;
		}
	}
	langs.delete("all");

	total_langs_count.innerHTML = langs.size.toLocaleString("en");
	total_dicts_count.innerHTML = total_dicts.toLocaleString("en");
	total_words_count.innerHTML = total_words.toLocaleString("en");
}

function updatePaypalButton(current_lang_src, current_lang_dst) {
	// Remove old buttons
	for (row of [...paypal_button_subscription.children]) {
		paypal_button_subscription.removeChild(row);
	}
	for (row of [...paypal_button_purchase.children]) {
		paypal_button_purchase.removeChild(row);
	}

	paypal_subscription
		.Buttons({
			style: {
				shape: "pill",
				color: "gold",
				layout: "vertical",
				label: "subscribe",
			},
			createSubscription: (data, actions) =>
				actions.subscription.create({
					plan_id: getPlanId(current_lang_src, current_lang_dst),
				}),
			onApprove: (data, actions) => {
				eventPayPalApproved("subscription", data);
			},
			// onCancel: (data, actions) => {
			// 	eventPayPalCanceled(current_lang_src, current_lang_dst);
			// },
		})
		.render(paypal_button_subscription);

	paypal_purchase
		.Buttons({
			style: {
				shape: "pill",
				color: "gold",
				layout: "vertical",
				label: "buynow",
			},
			createOrder: (data, actions) => {
				const price = getPricePurchase(current_lang_src, current_lang_dst);
				const kind =
					current_lang_src === current_lang_dst
						? "monolingual"
						: current_lang_src === "all"
							? "universal"
							: "bilingual";
				const options = {
					payment_source: {
						paypal: {
							experience_context: {
								brand_name: "reader.dict",
								payment_method_preference: "IMMEDIATE_PAYMENT_REQUIRED",
								shipping_preference: "NO_SHIPPING",
								user_action: "PAY_NOW",
							},
						},
					},
					purchase_units: [
						{
							amount: {
								breakdown: {
									item_total: { currency_code: "EUR", value: price },
								},
								currency_code: "EUR",
								value: price,
							},
							items: [
								{
									category: "DIGITAL_GOODS",
									name: `reader.dict ${current_lang_src.toUpperCase()}-${current_lang_dst.toUpperCase()} (${kind})`,
									quantity: 1,
									sku: `${current_lang_src}-${current_lang_dst}`,
									unit_amount: { currency_code: "EUR", value: price },
								},
							],
						},
					],
				};

				return actions.order.create(options);
			},
			onApprove: (data, actions) =>
				actions.order.capture().then((orderData) => {
					eventPayPalApproved("purchase", orderData);
				}),
			// onCancel: (data) => {
			// 	eventPayPalCanceled(current_lang_src, current_lang_dst);
			// },
		})
		.render(paypal_button_purchase);
}

document.addEventListener("DOMContentLoaded", () => {
	fetchMetrics();

	select_lang_src.addEventListener("change", (event) => {
		adaptLangDstOptions();
		updateDetails();
	});
	select_lang_dst.addEventListener("change", (event) => {
		updateDetails();
	});
});
