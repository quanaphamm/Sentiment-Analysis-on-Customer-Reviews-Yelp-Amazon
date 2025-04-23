// Search input suggestions
function searchItems() {
    const query = document.getElementById("itemSearch").value;

    fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
    })
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById("suggestions");
        list.innerHTML = "";
        data.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            li.onclick = () => selectItem(item);
            li.style.cursor = "pointer";
            list.appendChild(li);
        });
    });
}

// Handle selection of product/place
function selectItem(selected) {
    document.getElementById("itemSearch").value = selected;
    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("selected-item").innerText = selected;
    document.getElementById("reset-button").style.display = "inline-block";

    fetch("/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selected })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("summary").style.display = "block";
        document.getElementById("review-form").style.display = "block";

        document.getElementById("positive").innerText = data.positive + "%";
        document.getElementById("neutral").innerText = data.neutral + "%";
        document.getElementById("negative").innerText = data.negative + "%";
        document.getElementById("suggestion").innerText = data.suggestion;

        const existingList = document.querySelector("#summary ul.review-list");
        if (existingList) existingList.remove();

        const reviewList = document.createElement("ul");
        reviewList.classList.add("review-list");

        data.reviews.forEach(r => {
            const item = document.createElement("li");
            item.innerHTML = `<strong>[${r.sentiment}]</strong> ${r.review}`;
            reviewList.appendChild(item);
        });

        document.getElementById("summary").appendChild(reviewList);
    });
}

// Submit a review and append to list
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("review-form").addEventListener("submit", function (e) {
        e.preventDefault();
        const reviewText = document.getElementById("review").value;
        const selected = document.getElementById("selected-item").innerText;

        fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ review: reviewText, selected: selected })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById("prediction-result").style.display = "block";
            document.getElementById("predicted-sentiment").innerText = data.sentiment;

            const newReviewItem = document.createElement("li");
            newReviewItem.innerHTML = `<strong>[${data.sentiment}]</strong> ${reviewText}`;

            const reviewList = document.querySelector("#summary ul.review-list");
            if (reviewList) {
                reviewList.insertBefore(newReviewItem, reviewList.firstChild);
            } else {
                const newList = document.createElement("ul");
                newList.classList.add("review-list");
                newList.appendChild(newReviewItem);
                document.getElementById("summary").appendChild(newList);
            }

            document.getElementById("review").value = "";

            // 🔄 Re-fetch updated summary + stats
            selectItem(selected);
        });
    });

    // Load Top 10 lists on page load
    fetch("/top-places")
    .then(res => res.json())
    .then(data => {
        const topVisit = document.getElementById("top-visit");
        const topAvoid = document.getElementById("top-avoid");

        data.visit.forEach(name => {
            const li = document.createElement("li");
            li.textContent = name;
            li.onclick = () => selectItem(name);
            li.style.cursor = "pointer";
            topVisit.appendChild(li);
        });

        data.avoid.forEach(name => {
            const li = document.createElement("li");
            li.textContent = name;
            li.onclick = () => selectItem(name);
            li.style.cursor = "pointer";
            topAvoid.appendChild(li);
        });
    });
});

// Reset back to search input
function resetToSearch() {
    document.getElementById("itemSearch").value = "";
    document.getElementById("selected-item").innerText = "";
    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("summary").style.display = "none";
    document.getElementById("review-form").style.display = "none";
    document.getElementById("prediction-result").style.display = "none";
    document.getElementById("reset-button").style.display = "none";
}
