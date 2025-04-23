// Step 1: Handle source dropdown
function handleSourceChange(value) {
    if (value === "amazon" || value === "yelp") {
        document.getElementById("search-section").style.display = "block";
        document.getElementById("review-section").style.display = "none";
        document.getElementById("summary").style.display = "none";
        document.getElementById("prediction-result").style.display = "none";
        document.getElementById("itemSearch").value = "";
        document.getElementById("suggestions").innerHTML = "";
        searchItems(true);
    }
}

function searchItems(forceShow = false) {
    const query = document.getElementById("itemSearch").value;
    const source = document.getElementById("source").value;

    // Always show if forced or query is typed
    if (!forceShow && query.length < 2) return;

    fetch("/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query, source })
    })
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById("suggestions");
        list.innerHTML = "";

        data.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            li.style.cursor = "pointer";
            li.onclick = () => selectItem(item);
            list.appendChild(li);
        });
    });
}


// Step 3: After user selects a product/place
function selectItem(selectedText) {
    const source = document.getElementById("source").value;

    // Clear suggestions
    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("itemSearch").value = selectedText;
    document.getElementById("selected-item").innerText = selectedText;

    // Show review form and summary
    document.getElementById("review-section").style.display = "block";

    // Fetch summary
    fetch("/summary", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ selected: selectedText, source })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("summary").style.display = "block";
        document.getElementById("positive").innerText = data.positive + "%";
        document.getElementById("neutral").innerText = data.neutral + "%";
        document.getElementById("negative").innerText = data.negative + "%";
        document.getElementById("suggestion").innerText = data.suggestion;
    });
}

// Step 4: Handle new review submission
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("review-form");
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const reviewText = document.getElementById("review").value;

        fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ review: reviewText })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById("prediction-result").style.display = "block";
            document.getElementById("predicted-sentiment").innerText = data.sentiment;
        });
    });
});
