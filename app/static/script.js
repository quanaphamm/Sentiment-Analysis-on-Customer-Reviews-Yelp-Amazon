// 🔍 Live search
function searchItems() {
    const query = document.getElementById("itemSearch").value;

    fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
    })
    .then(res => res.json())
    .then(data => {
        const suggestions = document.getElementById("suggestions");
        suggestions.innerHTML = "";
        data.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            li.onclick = () => selectItem(item);
            suggestions.appendChild(li);
        });
    });
}

// 🧭 On page load: show top 10 places
document.addEventListener("DOMContentLoaded", () => {
    fetch("/top-places")
        .then(res => res.json())
        .then(data => {
            const topVisit = document.getElementById("top-visit");
            const topAvoid = document.getElementById("top-avoid");

            data.visit.forEach(place => {
                const li = document.createElement("li");
                li.textContent = place;
                li.onclick = () => selectItem(place);
                topVisit.appendChild(li);
            });

            data.avoid.forEach(place => {
                const li = document.createElement("li");
                li.textContent = place;
                li.onclick = () => selectItem(place);
                topAvoid.appendChild(li);
            });
        });

    // ✍️ Handle form submit
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
            selectItem(selected);  // Refresh updated stats & review count
        });
    });
});

// 📊 When a user selects a place
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
        document.getElementById("review-count").innerText = data.count || data.reviews.length;

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

// 🔙 Reset UI to search
function resetToSearch() {
    document.getElementById("itemSearch").value = "";
    document.getElementById("selected-item").innerText = "";
    document.getElementById("review-count").innerText = "";
    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("summary").style.display = "none";
    document.getElementById("review-form").style.display = "none";
    document.getElementById("prediction-result").style.display = "none";
    document.getElementById("reset-button").style.display = "none";
}
