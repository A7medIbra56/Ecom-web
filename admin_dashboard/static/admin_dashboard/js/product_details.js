document.addEventListener("DOMContentLoaded", function () {
    const showMoreBtn = document.getElementById("showMoreBtn");
    const extraThumbs = document.querySelectorAll(".extra-thumb");
    const showMoreContainer = document.getElementById("showMoreContainer");
    const thumbnailContainer = document.getElementById("thumbnailContainer");

    let isExpanded = false;

    showMoreBtn.addEventListener("click", function () {
    if (!isExpanded) {
        // === EXPAND ===
        extraThumbs.forEach((el, i) => {
        el.classList.remove("d-none");
        el.classList.add("showing")

        // setTimeout(() => el.classList.add("showing"), i * 0); // staggered animation

        });

        // Move the "Show More" container but do this only after animation is finished
        showMoreContainer.classList.add("moving");
        thumbnailContainer.appendChild(showMoreContainer);
        showMoreContainer.classList.remove("moving")
        
        // setTimeout(() => {
        // thumbnailContainer.appendChild(showMoreContainer);
        // showMoreContainer.classList.remove("moving");
        // }, 300);

        showMoreBtn.textContent = "Show Less";
        isExpanded = true;
    } else {
        // === COLLAPSE ===
        extraThumbs.forEach(el => {
        el.classList.remove("showing");
        el.classList.add("d-none")

        // setTimeout(() => el.classList.add("d-none"), 300);

        });

        // Move the "Show Less" container after it has collapsed
        showMoreContainer.classList.add("moving");
        thumbnailContainer.appendChild(showMoreContainer);
        showMoreContainer.classList.remove("moving");

        // setTimeout(() => {
        // thumbnailContainer.appendChild(showMoreContainer);
        // showMoreContainer.classList.remove("moving");
        // }, 300);

        showMoreBtn.textContent = `+${extraThumbs.length} More`;
        isExpanded = false;

        // Don't scroll the page when collapsing
    }
    });
});

