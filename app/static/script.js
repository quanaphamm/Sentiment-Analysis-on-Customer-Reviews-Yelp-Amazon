// Triggered when user types in search bar
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

// Triggered when user selects a business/place
function selectItem(selected) {
    document.getElementById("itemSearch").value = selected;
    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("selected-item").innerText = selected;

    fetch("/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selected })
    })
    .then(res => res.json())
    .then(data => {
        // Display summary stats
        document.getElementById("summary").style.display = "block";
        document.getElementById("review-form").style.display = "block";

        document.getElementById("positive").innerText = data.positive + "%";
        document.getElementById("neutral").innerText = data.neutral + "%";
        document.getElementById("negative").innerText = data.negative + "%";
        document.getElementById("suggestion").innerText = data.suggestion;

        // Clear existing review list
        const existingList = document.querySelector("#summary ul.review-list");
        if (existingList) existingList.remove();

        // Add top 10 reviews
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

// Handle new review submission
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("review-form").addEventListener("submit", function (e) {
        e.preventDefault();
        const reviewText = document.getElementById("review").value;

        fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ review: reviewText })
        })
        .then(res => res.json())
        .then(data => {
            // Show prediction result
            document.getElementById("prediction-result").style.display = "block";
            document.getElementById("predicted-sentiment").innerText = data.sentiment;

            // Prepend new review to list
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

            // Clear the review input box
            document.getElementById("review").value = "";
        });
    });
});
