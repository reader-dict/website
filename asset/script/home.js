const tabs_icons = document.querySelectorAll(".tab .icon");
const tabs_content = document.querySelectorAll(".tab-content > div");
const buy = document.getElementById("buy");
const select_lang_src = document.getElementById("lang-src");
const select_lang_dst = document.getElementById("lang-dst");
const select_lang_mono = document.getElementById("lang-mono");
const words_count = document.getElementById("words-count");
const wiktionary_snapshot = document.getElementById("wiktionary-snapshot");
const missing_mobi = document.getElementById("missing-mobi");
const missing_pocket = document.getElementById("missing-pocket");
const buy_link = document.getElementById("buy-link");

const locale = "en";
const language_formatter = new Intl.DisplayNames([locale], {
	type: "language",
});

// Updated in fetchMetrics() on document fully loaded
metrics = {};

function adaptLangDstOptions() {
	const lang_src = currentLangSrc();

	// Clean-up the current list
	for (row of [...select_lang_dst.children]) {
		select_lang_dst.removeChild(row);
	}

	for (const lang_dst in metrics[lang_src]) {
		if (lang_dst !== lang_src) {
			const option = document.createElement("option");

			option.value = lang_dst;
			option.innerHTML = `${lang_dst.toUpperCase()} - ${toTitle(language_formatter.of(lang_dst))}`;
			select_lang_dst.appendChild(option);
		}
	}

	select_lang_dst.options[0].selected = true;
}

function adjustDictionaryInformation() {
	const { formats, updated, words } =
		metrics[currentLangSrc()][currentLangDst()];

	words_count.innerHTML = words.toLocaleString(locale);
	wiktionary_snapshot.innerHTML = updated;
	missing_mobi.style.display = formats.includes("mobi") ? "none" : "block";
	missing_pocket.style.display = formats.includes("pocket") ? "none" : "block";
}

function currentLangDst() {
	return select_lang_dst.options[select_lang_dst.selectedIndex].value;
}

function currentLangSrc() {
	return select_lang_src.options[select_lang_src.selectedIndex].value;
}

function fetchMetrics() {
	fetch("/api/v1/dictionaries")
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			metrics = data;
			adaptLangDstOptions();
			scrollToLocViaAnchor();
			adjustDictionaryInformation();
		});
}

function fireBuyLink() {
	const buy_url = buy_link.dataset.url;
	const client_id = buy_link.dataset.cid;
	const client_reference_id = `${client_id}-${currentLangSrc()}-${currentLangDst()}`;

	fetch(`/api/v1/pre-order?client_reference_id=${client_reference_id}`)
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			console.debug(data);
			window.location = `${buy_url}?client_reference_id=${client_reference_id}`;
		});
}

function openTab(idx) {
	tabs_icons.forEach((item, idx_item) => {
		if (idx === idx_item) {
			item.classList.add("active");
		} else {
			item.classList.remove("active");
		}
	});
	tabs_content.forEach((item, idx_item) => {
		item.style.display = idx === idx_item ? "block" : "none";
	});
	return false;
}

function openDownloadPage() {
	const lang = select_lang_mono.options[select_lang_mono.selectedIndex].value;

	window.location = `/download/${lang}`;
}

function scrollToLocViaAnchor() {
	const [_, anchor] = new URL(document.location).href.split("#", 2);

	if (anchor) {
		let target;

		if (anchor.startsWith("faq-")) {
			const faq_item = document.getElementById(anchor);

			if (typeof faq_item !== "undefined") {
				faq_item.open = true;
				target = faq_item;
			}
		} else {
			let found_lang_src = false;
			let found_lang_dst = false;
			const [lang_src, lang_dst] = anchor.split("-");

			if (lang_src === lang_dst) {
				for (row of [...select_lang_mono.children]) {
					if (row.value === lang_src) {
						row.selected = true;
						found_lang_src = true;
						found_lang_dst = true;
						break;
					}
				}
			} else {
				for (row of [...select_lang_src.children]) {
					if (row.value === lang_src) {
						row.selected = true;
						found_lang_src = true;
						break;
					}
				}
				for (row of [...select_lang_dst.children]) {
					if (row.value === lang_dst) {
						row.selected = true;
						found_lang_dst = true;
						break;
					}
				}
			}

			if (found_lang_src && found_lang_dst) {
				target = buy;
			}
		}

		if (typeof target !== "undefined") {
			target.scrollIntoView({ block: "start", behavior: "smooth" });
		}
	}
}

function setupTabs() {
	tabs_icons.forEach((item, idx_item) => {
		item.addEventListener("click", (event) => {
			openTab(idx_item);
		});
	});
	tabs_content.forEach((item, idx_item) => {
		item.id = `tab${idx_item}`;
	});
	openTab(0);
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
			? str[i].toLocaleUpperCase(locale)
			: str[i].toLocaleLowerCase(locale);
		upper = false;
	}
	return newStr;
}

document.addEventListener("DOMContentLoaded", () => {
	setupTabs();
	fetchMetrics();

	select_lang_src.addEventListener("change", (event) => {
		adaptLangDstOptions();
		adjustDictionaryInformation();
	});
	select_lang_dst.addEventListener("change", (event) => {
		adjustDictionaryInformation();
	});
	select_lang_mono.addEventListener("change", (event) => {
		openDownloadPage();
	});
	buy_link.addEventListener("click", (event) => {
		fireBuyLink();
		event.preventDefault();
	});
	window.addEventListener("hashchange", (event) => {
		scrollToLocViaAnchor();
	});
});
