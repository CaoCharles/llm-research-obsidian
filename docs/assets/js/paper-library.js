// Search, filter, sort, and progressively reveal the generated paper library.
(function () {
  const PAGE_SIZE = 12;

  function initPaperLibrary() {
    const library = document.getElementById("paper-library");
    if (!library || library.dataset.ready === "true") return;
    library.dataset.ready = "true";

    const search = document.getElementById("paper-search");
    const sort = document.getElementById("paper-sort");
    const tag = document.getElementById("paper-tag");
    const reset = document.getElementById("paper-reset");
    const loadMore = document.getElementById("paper-load-more");
    const results = document.getElementById("paper-results");
    const empty = document.getElementById("paper-empty");
    const grid = library.querySelector(".paper-grid");
    const categoryChips = Array.from(library.querySelectorAll(".paper-category-chip"));
    const entries = Array.from(library.querySelectorAll(".paper-entry"));
    const params = new URLSearchParams(window.location.search);
    let selectedCategory = params.get("category") || "";
    let visibleLimit = PAGE_SIZE;

    if (search) search.value = params.get("q") || "";
    if (tag) tag.value = params.get("tag") || "";
    if (sort && ["date-desc", "relevance-desc", "title-asc"].includes(params.get("sort"))) {
      sort.value = params.get("sort");
    }
    if (!categoryChips.some((chip) => chip.dataset.category === selectedCategory)) {
      selectedCategory = "";
    }

    function syncUrl() {
      const next = new URLSearchParams();
      if (search?.value.trim()) next.set("q", search.value.trim());
      if (selectedCategory) next.set("category", selectedCategory);
      if (tag?.value) next.set("tag", tag.value);
      if (sort?.value && sort.value !== "date-desc") next.set("sort", sort.value);
      const query = next.toString();
      window.history.replaceState({}, "", query ? `${window.location.pathname}?${query}` : window.location.pathname);
    }

    function compareEntries(first, second) {
      if (sort?.value === "title-asc") {
        return first.dataset.title.localeCompare(second.dataset.title, "zh-TW");
      }
      if (sort?.value === "relevance-desc") {
        return Number(second.dataset.relevance) - Number(first.dataset.relevance)
          || second.dataset.date.localeCompare(first.dataset.date);
      }
      return second.dataset.date.localeCompare(first.dataset.date)
        || second.dataset.relevance - first.dataset.relevance;
    }

    function update() {
      const query = (search?.value || "").trim().toLocaleLowerCase("zh-TW");
      const selectedTag = tag?.value || "";
      const matches = entries.filter((entry) => {
        const matchesQuery = !query || entry.dataset.search.includes(query);
        const matchesCategory = !selectedCategory || entry.dataset.category === selectedCategory;
        const entryTags = (entry.dataset.tags || "").split(" ");
        const matchesTag = !selectedTag || entryTags.includes(selectedTag);
        return matchesQuery && matchesCategory && matchesTag;
      }).sort(compareEntries);

      entries.forEach((entry) => { entry.hidden = true; });
      matches.forEach((entry, index) => {
        grid?.appendChild(entry);
        entry.hidden = index >= visibleLimit;
      });

      categoryChips.forEach((chip) => {
        const active = chip.dataset.category === selectedCategory;
        chip.classList.toggle("is-active", active);
        chip.setAttribute("aria-pressed", String(active));
      });

      const shown = Math.min(visibleLimit, matches.length);
      if (results) results.textContent = `顯示 ${shown} / ${matches.length} 篇論文`;
      if (empty) empty.hidden = matches.length !== 0;
      if (loadMore) loadMore.hidden = shown >= matches.length;
      syncUrl();
    }

    search?.addEventListener("input", () => { visibleLimit = PAGE_SIZE; update(); });
    sort?.addEventListener("change", update);
    tag?.addEventListener("change", () => { visibleLimit = PAGE_SIZE; update(); });
    reset?.addEventListener("click", () => {
      if (search) search.value = "";
      if (tag) tag.value = "";
      if (sort) sort.value = "date-desc";
      selectedCategory = "";
      visibleLimit = PAGE_SIZE;
      update();
    });
    loadMore?.addEventListener("click", () => { visibleLimit += PAGE_SIZE; update(); });
    categoryChips.forEach((chip) => chip.addEventListener("click", () => {
      selectedCategory = chip.dataset.category || "";
      visibleLimit = PAGE_SIZE;
      update();
    }));
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
