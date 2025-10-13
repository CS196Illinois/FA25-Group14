document.addEventListener("DOMContentLoaded", () => {
  // ---- Course explorer backed by CSV API ----
  const courseGrid = document.querySelector("#course-grid");
  const majorSelect = document.querySelector("#filter-major");
  const genedDropdownBtn = document.querySelector("#gened-dropdown-btn");
  const genedDropdown = document.querySelector("#gened-dropdown");
  const genedOptions = document.querySelectorAll(".gened-option");
  const selectedGenedsContainer = document.querySelector("#selected-geneds");
  const searchInput = document.querySelector("#filter-search");
  const summary = document.querySelector("#course-summary");
  const loadMoreBtn = document.querySelector("#course-load-more");
  const scrollLeftBtn = document.querySelector("#course-scroll-left");
  const scrollRightBtn = document.querySelector("#course-scroll-right");
  const infiniteLoading = document.querySelector("#infinite-loading");

  if (courseGrid && summary && loadMoreBtn) {
    const state = {
      limit: 30,
      step: 30,
      filters: {
        major: "all",
        geneds: [],
        q: "",
      },
      selectedGeneds: [],
      totalMatches: 0,
      isLoading: false,
    };

    const normalizeFilters = () => {
      state.filters.major = (majorSelect?.value || "all").trim();
      state.filters.geneds = state.selectedGeneds || [];
      state.filters.q = (searchInput?.value || "").trim();
    };

    const truncate = (text, length = 220) => {
      if (!text) return "No description available yet.";
      return text.length > length ? `${text.slice(0, length).trim()}…` : text;
    };

    const renderCourses = (courses) => {
      if (!courses.length) {
        courseGrid.innerHTML =
          '<p class="empty-state">No courses match those filters yet. Try broadening your search.</p>';
        return;
      }

      courseGrid.innerHTML = courses
        .map((course) => {
          const geneds = course.gen_ed_requirements
            ? course.gen_ed_requirements
                .split(/[;,]/)
                .map((part) => part.trim())
                .filter(Boolean)
            : [];
          const genedMarkup =
            geneds.length > 0
              ? `<div class="course-tags">${geneds
                  .map((tag) => `<span class="badge">${tag}</span>`)
                  .join("")}</div>`
              : "";

          return `
            <article class="card course-card" data-major="${course.department}">
              <a href="/course/${encodeURIComponent(
                course.course_code
              )}" class="course-link">
                <header>
                  <h3>${course.course_code}</h3>
                  <span class="badge">${course.credit_hours || "N/A"} hrs</span>
                </header>
                <p class="course-title">${course.course_name}</p>
                <ul class="course-meta">
                  <li><strong>Department:</strong> ${
                    course.department || "—"
                  }</li>
                  <li><strong>Gen Ed:</strong> ${
                    geneds.length ? geneds.join(", ") : "None listed"
                  }</li>
                </ul>
                ${genedMarkup}
                <p class="course-highlight">${truncate(course.description)}</p>
              </a>
            </article>
          `;
        })
        .join("");

      // Update scroll buttons after rendering
      setTimeout(() => {
        if (scrollLeftBtn && scrollRightBtn) {
          const scrollLeft = courseGrid.scrollLeft;
          const maxScroll = courseGrid.scrollWidth - courseGrid.clientWidth;
          scrollLeftBtn.disabled = scrollLeft <= 0;
          scrollRightBtn.disabled = scrollLeft >= maxScroll;
        }
      }, 100);
    };

    const updateSummary = (shown) => {
      const total = state.totalMatches;
      const filters = [];

      if (state.filters.major && state.filters.major !== "all") {
        filters.push(`${state.filters.major} major`);
      }

      if (state.filters.geneds && state.filters.geneds.length > 0) {
        const genEdNames = state.filters.geneds.join(", ");
        filters.push(
          `${genEdNames} gen ed${state.filters.geneds.length > 1 ? "s" : ""}`
        );
      }

      if (state.filters.q) {
        filters.push(`"${state.filters.q}"`);
      }

      const filterText =
        filters.length > 0 ? ` matching ${filters.join(" + ")}` : "";

      if (total === 0) {
        summary.textContent = `No courses${filterText} found. Try adjusting your filters.`;
      } else if (total <= shown) {
        summary.textContent = `Showing ${shown} course${
          shown === 1 ? "" : "s"
        }${filterText} (all results).`;
      } else {
        summary.textContent = `Showing ${shown} of ${total} courses${filterText}.`;
      }
    };

    const setLoading = (isLoading) => {
      state.isLoading = isLoading;
      if (isLoading) {
        courseGrid.classList.add("is-loading");
        summary.textContent = "Loading explorer data...";
        loadMoreBtn.disabled = true;
        loadMoreBtn.textContent = "Loading…";
      } else {
        courseGrid.classList.remove("is-loading");
        loadMoreBtn.disabled = false;
        loadMoreBtn.textContent = "Load more courses";
      }
    };

    const fetchCourses = async () => {
      normalizeFilters();
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (state.filters.major && state.filters.major !== "all") {
          params.set("major", state.filters.major);
        }
        if (state.filters.geneds && state.filters.geneds.length > 0) {
          params.set("geneds", state.filters.geneds.join(","));
        }
        if (state.filters.q) {
          params.set("q", state.filters.q);
        }
        params.set("limit", String(state.limit));

        const response = await fetch(`/api/courses?${params.toString()}`);
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        const data = await response.json();
        const results = Array.isArray(data.results) ? data.results : [];
        state.totalMatches = data.matches || 0;
        renderCourses(results);
        updateSummary(results.length);

        if (state.totalMatches === 0) {
          loadMoreBtn.disabled = true;
          loadMoreBtn.textContent = "Load more courses";
        } else {
          const moreAvailable = state.totalMatches > results.length;
          loadMoreBtn.disabled = !moreAvailable;
          loadMoreBtn.textContent = moreAvailable
            ? "Load more courses"
            : "All results loaded";
        }
      } catch (error) {
        console.error(error);
        summary.textContent =
          "Unable to load courses right now. Please try again soon.";
        courseGrid.innerHTML =
          '<p class="empty-state">We hit a snag loading courses. Refresh or adjust filters to retry.</p>';
        loadMoreBtn.disabled = true;
        loadMoreBtn.textContent = "Load more courses";
      } finally {
        setLoading(false);
        // Hide infinite loading indicator
        if (infiniteLoading) {
          infiniteLoading.hidden = true;
        }
      }
    };

    const fetchMeta = async () => {
      try {
        const response = await fetch("/api/courses/meta");
        if (!response.ok) {
          throw new Error(`Meta request failed with status ${response.status}`);
        }
        const data = await response.json();

        const updateSelect = (select, values) => {
          if (!select || !Array.isArray(values)) return;
          const defaultOption = select.querySelector('option[value="all"]');
          const defaultNode = defaultOption
            ? defaultOption.cloneNode(true)
            : new Option("All", "all");
          select.innerHTML = "";
          select.appendChild(defaultNode);
          values.forEach((value) => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = value;
            select.appendChild(option);
          });
        };

        updateSelect(majorSelect, data.departments || []);
      } catch (error) {
        console.error(error);
      }
    };

    // Gen ed dropdown functionality
    const updateSelectedGeneds = () => {
      selectedGenedsContainer.innerHTML = state.selectedGeneds
        .map((value) => {
          const option = Array.from(genedOptions).find(
            (opt) => opt.dataset.value === value
          );
          const text = option ? option.textContent : value;
          return `<span class="tag">${text}<button type="button" class="tag-remove" data-value="${value}">×</button></span>`;
        })
        .join("");

      // Update dropdown button text
      const btnText =
        state.selectedGeneds.length === 0
          ? "Add gen ed requirement"
          : `${state.selectedGeneds.length} gen ed${
              state.selectedGeneds.length > 1 ? "s" : ""
            } selected`;
      genedDropdownBtn.querySelector("span").textContent = btnText;

      // Update option states
      genedOptions.forEach((option) => {
        option.classList.toggle(
          "selected",
          state.selectedGeneds.includes(option.dataset.value)
        );
      });
    };

    const toggleGenedDropdown = () => {
      const isOpen = genedDropdown.classList.contains("open");
      genedDropdown.classList.toggle("open", !isOpen);
      genedDropdownBtn.classList.toggle("active", !isOpen);
    };

    const addGened = (value) => {
      if (!state.selectedGeneds.includes(value)) {
        state.selectedGeneds.push(value);
        updateSelectedGeneds();
        state.limit = state.step;
        fetchCourses();
      }
      toggleGenedDropdown();
    };

    const removeGened = (value) => {
      state.selectedGeneds = state.selectedGeneds.filter((g) => g !== value);
      updateSelectedGeneds();
      state.limit = state.step;
      fetchCourses();
    };

    // Event listeners for filters
    majorSelect?.addEventListener("change", () => {
      state.limit = state.step;
      fetchCourses();
    });

    genedDropdownBtn?.addEventListener("click", toggleGenedDropdown);

    genedOptions.forEach((option) => {
      option.addEventListener("click", () => {
        addGened(option.dataset.value);
      });
    });

    selectedGenedsContainer?.addEventListener("click", (e) => {
      if (e.target.classList.contains("tag-remove")) {
        removeGened(e.target.dataset.value);
      }
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
      if (
        !genedDropdownBtn?.contains(e.target) &&
        !genedDropdown?.contains(e.target)
      ) {
        genedDropdown?.classList.remove("open");
        genedDropdownBtn?.classList.remove("active");
      }
    });

    // Initialize gen ed display
    updateSelectedGeneds();

    searchInput?.addEventListener("input", () => {
      state.limit = state.step;
      fetchCourses();
    });

    loadMoreBtn.addEventListener("click", () => {
      state.limit = Math.min(state.limit + state.step, 120);
      fetchCourses();
    });

    // Scroll functionality for course grid
    const updateScrollButtons = () => {
      if (!scrollLeftBtn || !scrollRightBtn) return;

      const scrollLeft = courseGrid.scrollLeft;
      const maxScroll = courseGrid.scrollWidth - courseGrid.clientWidth;

      scrollLeftBtn.disabled = scrollLeft <= 0;
      scrollRightBtn.disabled = scrollLeft >= maxScroll;
    };

    scrollLeftBtn?.addEventListener("click", () => {
      const cardWidth = 320 + 28; // card width + gap
      courseGrid.scrollBy({ left: -cardWidth, behavior: "smooth" });
      setTimeout(updateScrollButtons, 300);
    });

    scrollRightBtn?.addEventListener("click", () => {
      const cardWidth = 320 + 28; // card width + gap
      courseGrid.scrollBy({ left: cardWidth, behavior: "smooth" });
      setTimeout(updateScrollButtons, 300);
    });

    // Infinite scroll functionality
    const checkInfiniteScroll = () => {
      if (!courseGrid || state.isLoading) return;

      const scrollLeft = courseGrid.scrollLeft;
      const scrollWidth = courseGrid.scrollWidth;
      const clientWidth = courseGrid.clientWidth;
      const threshold = 200; // Load more when within 200px of the end

      // Check if we're near the end and have more courses to load
      const nearEnd = scrollLeft + clientWidth >= scrollWidth - threshold;
      const hasMoreCourses = state.totalMatches > courseGrid.children.length;

      if (nearEnd && hasMoreCourses) {
        // Show loading indicator
        if (infiniteLoading) {
          infiniteLoading.hidden = false;
        }

        state.limit = Math.min(state.limit + state.step, 120);
        fetchCourses();
      }
    };

    courseGrid?.addEventListener("scroll", () => {
      updateScrollButtons();
      checkInfiniteScroll();
    });

    // Initial scroll button state
    setTimeout(updateScrollButtons, 500);

    fetchMeta().finally(fetchCourses);
  }

  // ---- Flash message dismissal ----
  const alertCloseButtons = document.querySelectorAll(".alert-close");
  alertCloseButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const alert = button.closest(".alert");
      if (alert) {
        alert.style.opacity = "0";
        alert.style.transform = "translateY(-10px)";
        setTimeout(() => {
          alert.remove();
        }, 300);
      }
    });
  });

  // Auto-dismiss flash messages after 5 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      if (alert && alert.parentNode) {
        alert.style.opacity = "0";
        alert.style.transform = "translateY(-10px)";
        setTimeout(() => {
          if (alert.parentNode) {
            alert.remove();
          }
        }, 300);
      }
    }, 5000);
  });

  // ---- AI assistant with Gemini API ----
  const aiForm = document.querySelector("#ai-form");
  const aiOutput = document.querySelector("#ai-output");
  if (aiForm && aiOutput) {
    aiForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const formData = new FormData(aiForm);
      const major = formData.get("ai-major");
      const goals = formData.get("ai-goals");
      const priorities = formData.getAll("priority");

      // Show loading state
      aiOutput.innerHTML = `
        <div class="ai-loading">
          <div class="loading-spinner"></div>
          <p>Generating personalized recommendations...</p>
        </div>
      `;
      aiOutput.classList.add("active");
      aiOutput.scrollIntoView({ behavior: "smooth", block: "start" });

      try {
        // Call the AI endpoint
        const response = await fetch("/api/ai-assistant", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            major: major,
            goals: goals,
            priorities: priorities,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(
            errorData.error || "Failed to generate recommendation"
          );
        }

        const data = await response.json();

        // Parse JSON response
        let recommendationHTML = "";
        try {
          const jsonResponse =
            typeof data.recommendation === "string"
              ? JSON.parse(data.recommendation)
              : data.recommendation;

          if (
            jsonResponse.recommended_courses &&
            Array.isArray(jsonResponse.recommended_courses)
          ) {
            recommendationHTML = jsonResponse.recommended_courses
              .map(
                (course) => `
              <a href="/course/${encodeURIComponent(
                course.course
              )}" class="course-recommendation-card">
                <div class="course-code">${course.course}</div>
                <div class="course-reason">${course.reason}</div>
              </a>
            `
              )
              .join("");
          } else {
            // Fallback if JSON doesn't match expected structure
            recommendationHTML = `<p>${
              typeof data.recommendation === "string"
                ? data.recommendation
                : JSON.stringify(data.recommendation)
            }</p>`;
          }
        } catch (parseError) {
          // If JSON parsing fails, display as plain text
          console.error("Failed to parse JSON response:", parseError);
          recommendationHTML = `<p>${data.recommendation}</p>`;
        }

        // Display the AI response
        aiOutput.innerHTML = `
          <h3>Your Personalized Course Recommendations</h3>
          <div class="ai-recommendation">
            ${recommendationHTML}
          </div>
          <button type="button" class="btn btn-ghost" onclick="this.parentElement.classList.remove('active')">
            Close
          </button>
        `;
      } catch (error) {
        console.error("AI assistant error:", error);
        aiOutput.innerHTML = `
          <h3>Unable to Generate Recommendation</h3>
          <p class="error-message">
            ${
              error.message ||
              "Sorry, we couldn't generate a recommendation at this time. Please try again."
            }
          </p>
          <button type="button" class="btn btn-ghost" onclick="this.parentElement.classList.remove('active')">
            Close
          </button>
        `;
      }
    });
  }

  // ---- Simple nav state ----
  const navLinks = document.querySelectorAll(".site-nav a");
  if (navLinks.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const id = entry.target.getAttribute("id");
          if (!id) return;
          const link = document.querySelector(`.site-nav a[href="#${id}"]`);
          if (!link) return;
          if (entry.isIntersecting) {
            navLinks.forEach((nav) => nav.classList.remove("active"));
            link.classList.add("active");
          }
        });
      },
      { rootMargin: "-40% 0px -50%" }
    );

    document
      .querySelectorAll("main section[id]")
      .forEach((section) => observer.observe(section));
  }
});
