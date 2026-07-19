// Client-side filtering for the generated paper library.
(function () {
  function initPaperLibrary() {
    const library = document.getElementById("paper-library");
    if (!library || library.dataset.ready === "true") return;
    library.dataset.ready = "true";

    const search = document.getElementById("paper-search");
    const category = document.getElementById("paper-category");
    const tag = document.getElementById("paper-tag");
    const results = document.getElementById("paper-results");
    const empty = document.getElementById("paper-empty");
    const entries = Array.from(library.querySelectorAll(".paper-entry"));

    function update() {
      const query = (search?.value || "").trim().toLocaleLowerCase("zh-TW");
      const selectedCategory = category?.value || "";
      const selectedTag = tag?.value || "";
      let visible = 0;

      entries.forEach((entry) => {
        const matchesQuery = !query || entry.dataset.search.includes(query);
        const matchesCategory = !selectedCategory || entry.dataset.category === selectedCategory;
        const entryTags = (entry.dataset.tags || "").split(" ");
        const matchesTag = !selectedTag || entryTags.includes(selectedTag);
        const show = matchesQuery && matchesCategory && matchesTag;
        entry.hidden = !show;
        if (show) visible += 1;
      });

      if (results) results.textContent = `顯示 ${visible} 篇論文`;
      if (empty) empty.hidden = visible !== 0;
    }

    search?.addEventListener("input", update);
    category?.addEventListener("change", update);
    tag?.addEventListener("change", update);
    update();
  }

  if (window.document$) {
    document$.subscribe(initPaperLibrary);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPaperLibrary);
  } else {
    initPaperLibrary();
  }
})();
