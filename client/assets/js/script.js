"use strict";

document.addEventListener("submit", handleSubmit);

async function handleSubmit(e) {
	e.preventDefault();
	const form = e.target;
	const data = new FormData(form);
	const value = Object.fromEntries(data.entries());

	const text = value.text;

	await makeRequest(text);
}


async function makeRequest(text) {
	const url = "http://localhost:5000/sentiment-prediction";

	const response = await fetch(url, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({text}),
	});

	const jsonResponse = await response.json();
	displayResults(jsonResponse["sentiment"]);
}


function displayResults(response) {
	const result = document.getElementById("result");
	const text = document.getElementById("text");

	result.innerHTML = "";

	const emojis = {
		positive: "&#x1F495",
		negative: "&#x1F47A",
		neutral: "&#x1F610",
	};

	const emoji = emojis[response];
	result.innerHTML = `<p>"${text.value}" => ${emoji} ${response}</p>`;
	
	text.value = "";
}
