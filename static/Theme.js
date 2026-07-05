// Pulse Index — shared interactions
(function () {
  "use strict";

  /* ---------- shared helper: flag a field with a red shake ----------
     Used by every "is-error" state (search box, filter dropdown, filter
     button) to restart the CSS shake animation on the same element. */
  function flashError(el) {
    el.classList.remove("is-error");
    void el.offsetWidth; // force reflow so the animation can replay
    el.classList.add("is-error");
  }

  /* ---------- theme toggle ---------- */
  var root = document.documentElement;
  var toggle = document.getElementById("themeToggle");

  if (toggle) {
    toggle.addEventListener("click", function () {
      var current = root.getAttribute("data-theme") || "light";
      var next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try {
        localStorage.setItem("pulse-index-theme", next);
      } catch (e) {}
      window.dispatchEvent(
        new CustomEvent("pulse-theme-change", { detail: { theme: next } }),
      );
    });
  }

  /* ---------- active nav link ---------- */
  var path = window.location.pathname.replace(/\/$/, "") || "/";
  document.querySelectorAll(".topbar-links a").forEach(function (a) {
    var href = a.getAttribute("href").replace(/\/$/, "") || "/";
    if (href === path) a.classList.add("active");
  });

  /* ---------- ripple on buttons ---------- */
  document.querySelectorAll("button, .btn").forEach(function (btn) {
    btn.addEventListener("pointerdown", function (e) {
      var rect = btn.getBoundingClientRect();
      var size = Math.max(rect.width, rect.height);
      var span = document.createElement("span");
      span.className = "ripple";
      span.style.width = span.style.height = size + "px";
      span.style.left = e.clientX - rect.left - size / 2 + "px";
      span.style.top = e.clientY - rect.top - size / 2 + "px";
      btn.appendChild(span);
      span.addEventListener("animationend", function () {
        span.remove();
      });
    });
  });

  /* ---------- drag & drop auto-upload ---------- */
  var dropzone = document.getElementById("dataset-dropzone");
  var fileInput = document.getElementById("dataset-input");
  var uploadForm = document.getElementById("upload-form");

  if (dropzone && fileInput) {
    var fileNameEl = dropzone.querySelector(".file-name");
    var dropText = dropzone.querySelector(".drop-text");
    var originalText = dropText.innerHTML;

    // SVG Icons to replace the text ✓ and ✗
    var successSvg =
      '<svg class="icon" viewBox="0 0 24 24" style="vertical-align: text-bottom; margin-right: 4px;"><polyline points="20 6 9 17 4 12"></polyline></svg>';
    var errorSvg =
      '<svg class="icon" viewBox="0 0 24 24" style="vertical-align: text-bottom; margin-right: 4px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';

    // Prevent default form submission if they press enter
    if (uploadForm) {
      uploadForm.addEventListener("submit", function (e) {
        e.preventDefault();
      });
    }

    ["dragenter", "dragover", "dragleave", "drop"].forEach(
      function (eventName) {
        dropzone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
      },
    );

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    ["dragenter", "dragover"].forEach(function (eventName) {
      dropzone.addEventListener(
        eventName,
        function () {
          dropzone.classList.add("is-dragover");
          dropzone.classList.remove("is-invalid", "is-valid");
        },
        false,
      );
    });

    ["dragleave", "drop"].forEach(function (eventName) {
      dropzone.addEventListener(
        eventName,
        function () {
          dropzone.classList.remove("is-dragover");
        },
        false,
      );
    });

    dropzone.addEventListener(
      "drop",
      function (e) {
        var dt = e.dataTransfer;
        var files = dt.files;
        if (files && files.length) {
          fileInput.files = files;
          handleFiles(files);
        }
      },
      false,
    );

    fileInput.addEventListener("change", function () {
      if (this.files && this.files.length) {
        handleFiles(this.files);
      }
    });

    function handleFiles(files) {
      var file = files[0];
      var activeCard = document.getElementById("active-dataset-card");
      
      // MEMORY: Check if the dataset card was visible BEFORE this new drag/drop
      var wasCardActive = activeCard && (activeCard.style.display !== "none" && activeCard.style.display !== "");
      
      // Clean up all UI states before starting
      dropzone.classList.remove("is-invalid", "is-success", "is-compact", "is-dragover");
      fileNameEl.style.color = "";
      
      // Immediately hide the active card while we process the new file or show errors
      if (activeCard) activeCard.style.display = "none";

      if (
        file.name.toLowerCase().endsWith(".txt") ||
        file.type === "text/plain"
      ) {
        fileNameEl.innerHTML = successSvg + file.name;
        fileNameEl.classList.add("show");

        dropText.innerHTML = "Uploading dataset... <span class='spinner' style='display:inline-block; border-top-color:var(--mint); width:12px; height:12px;'></span>";

        var formData = new FormData();
        formData.append("dataset", file);

        fetch("/upload", {
          method: "POST",
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            // Show the Success state
            dropzone.classList.add("is-success");
            dropText.innerHTML = `<strong>${data.message}</strong>`;

            // Update the text in the background
            document.getElementById("current-filename").textContent = data.filename;
            document.getElementById("current-count").textContent = data.count + " posts";

            // Wait 2.5s, collapse the dropzone, and reveal the NEW dataset card
            setTimeout(function() {
              dropzone.classList.remove("is-success");
              dropzone.classList.add("is-compact");
              dropText.innerHTML = originalText;
              
              // FIX: Ensure the file name text hides cleanly when it collapses
              fileNameEl.classList.remove("show"); 
              
              if (activeCard) activeCard.style.display = "flex";
            }, 2500);
          })
          .catch((err) => {
            // ERROR: Server failed
            dropzone.classList.add("is-invalid");
            dropText.innerHTML = "Upload failed. Please check your connection.";
            fileNameEl.innerHTML = errorSvg + "Server error.";
            fileNameEl.classList.add("show");
            fileNameEl.style.color = "var(--coral)";
            
            setTimeout(function() {
              dropzone.classList.remove("is-invalid");
              dropText.innerHTML = originalText;
              
              // FIX: Fade out the error text!
              fileNameEl.classList.remove("show"); 
              
              // If they had a dataset before the error, bring it back
              if (wasCardActive && activeCard) {
                dropzone.classList.add("is-compact");
                activeCard.style.display = "flex";
              }
            }, 3000);
          });
      } else {
        // ERROR: Wrong file type (Rejection)
        dropzone.classList.add("is-invalid");
        fileNameEl.innerHTML = errorSvg + "Invalid file. Must be a .txt dataset.";
        fileNameEl.classList.add("show");
        fileNameEl.style.color = "var(--coral)";
        dropText.innerHTML = "File rejected.";
        if (fileInput) fileInput.value = "";

        setTimeout(function () {
          dropzone.classList.remove("is-invalid");
          dropText.innerHTML = originalText;
          
          // FIX: Fade out the error text!
          fileNameEl.classList.remove("show"); 

          // If they had a dataset before the rejection, bring it back
          if (wasCardActive && activeCard) {
            dropzone.classList.add("is-compact");
            activeCard.style.display = "flex";
          }
        }, 3000);
      }
    }
  }

  /* ---------- submit button loading state ---------- */
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function () {
      var btn = form.querySelector('button[type="submit"]');
      if (btn) btn.classList.add("is-loading");
    });
  });

  /* ---------- staggered entrance for dynamic rows ---------- */
  document.querySelectorAll("tbody tr, .data-row").forEach(function (row, i) {
    row.style.animationDelay = Math.min(i * 35, 600) + "ms";
  });

  /* ---------- hashtag pills (progressive enhancement) ---------- */
  document.querySelectorAll("td.hashtags").forEach(function (cell) {
    var raw = cell.textContent.trim();
    if (!raw) return;
    var tokens = raw.split(/[\s,]+/).filter(Boolean);
    if (tokens.length < 2 && tokens[0] && tokens[0].indexOf("#") !== 0) return;
    cell.innerHTML = "";
    tokens.forEach(function (t) {
      var pill = document.createElement("span");
      pill.className = "tag-pill";
      pill.textContent = t.indexOf("#") === 0 ? t : "#" + t;
      cell.appendChild(pill);
    });
  });

  /* ---------- delete dataset logic ---------- */
  var deleteBtn = document.getElementById("delete-dataset-btn");
  var activeCard = document.getElementById("active-dataset-card");

  if (deleteBtn && activeCard) {
    deleteBtn.addEventListener("click", function () {
      // Show loading spinner
      deleteBtn.classList.add("is-loading");

      fetch("/delete", { method: "POST" })
        .then((response) => response.json())
        .then((data) => {
          // 1. Hide the active card and stop spinner
          activeCard.style.display = "none";
          deleteBtn.classList.remove("is-loading");

          // 2. completely reset the dropzone UI
          var dropText = document.querySelector(".drop-text");
          var fileNameEl = document.querySelector(".file-name");
          var dropzone = document.getElementById("dataset-dropzone");

          if (dropText && dropzone) {
            // Reset text to default
            dropText.innerHTML =
              "Drag & drop your <strong>.txt</strong> dataset here, or";

            // Strip ALL state classes so it returns to STATE 1 (Empty)
            dropzone.classList.remove(
              "is-valid",
              "is-invalid",
              "is-success",
              "is-compact",
              "is-dragover",
            );

            // Clear the file name tracker
            if (fileNameEl) {
              fileNameEl.innerHTML = "";
              fileNameEl.classList.remove("show");
            }

            // Clear the actual file input so you can re-upload the same file if needed
            var fileInput = document.getElementById("dataset-input");
            if (fileInput) fileInput.value = "";
          }
        })
        .catch((err) => {
          deleteBtn.classList.remove("is-loading");
          alert("Failed to delete dataset. Please try again.");
        });
    });
  }

  /* ---------- search validation logic ---------- */
  var searchForm = document.getElementById("search-form");
  var searchInput = document.getElementById("keyword-input");

  if (searchForm && searchInput) {
    searchForm.addEventListener("submit", function (e) {
      var keyword = searchInput.value.trim();

      if (keyword === "") {
        // Prevent the form from actually submitting
        e.preventDefault();

        // Stop the submit button's spinner since the request never fires
        var submitBtn = searchForm.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.classList.remove("is-loading");
        }

        // Apply the red border and shake animation
        flashError(searchInput);

        // Clean up the class after the 400ms shake animation finishes
        setTimeout(function () {
          searchInput.classList.remove("is-error");
        }, 400);
      }
    });
  }

  /* ---------- handle browser back button (bfcache) ---------- */
  window.addEventListener("pageshow", function (event) {
    // The 'persisted' property is true if the page was loaded from the browser's back/forward cache
    if (event.persisted) {
      // Force a hard reload from the server to reset all states and fetch fresh data
      window.location.reload();
    }
  });

  /* ---------- Stateful Results Toolbar Logic ---------- */
  var resultsSortSelect = document.getElementById("results-sort");
  var resultsOrderBtn = document.getElementById("results-order-btn");

  if (resultsSortSelect && resultsOrderBtn) {
    function updateExploreURL() {
      // 1. Grab the current URL parameters
      var urlParams = new URLSearchParams(window.location.search);

      // 2. Set the newly selected sort and order values
      urlParams.set("sort", resultsSortSelect.value);
      urlParams.set("order", resultsOrderBtn.getAttribute("data-order"));

      // 3. Reset to page 1 to prevent getting stuck on an empty page
      urlParams.delete("page");

      // 4. Navigate instantly!
      window.location.href = "/explore?" + urlParams.toString();
    }

    // Trigger update when they pick a new dropdown option
    resultsSortSelect.addEventListener("change", updateExploreURL);

    // Flip the 'asc' / 'desc' state and trigger update when arrow is clicked
    resultsOrderBtn.addEventListener("click", function () {
      var currentOrder = this.getAttribute("data-order");
      var newOrder = currentOrder === "asc" ? "desc" : "asc";
      this.setAttribute("data-order", newOrder);

      // Optional: Give it a loading class while it crunches the data
      this.classList.add("is-loading");
      updateExploreURL();
    });
  }

  /* ---------- Dynamic Topbar Search Button ---------- */
  var topbarInput = document.querySelector(
    "#topbar-search-form input[name='search']",
  );
  var topbarSubmitBtn = document.querySelector(
    "#topbar-search-form .search-submit",
  );

  if (topbarInput && topbarSubmitBtn) {
    // Listen for every keystroke
    topbarInput.addEventListener("input", function () {
      // .trim() ignores empty spaces. If length > 0, they typed real text!
      if (this.value.trim().length > 0) {
        topbarSubmitBtn.classList.add("is-visible");
      } else {
        topbarSubmitBtn.classList.remove("is-visible");
      }
    });
  }

  /* ---------- Custom Dropdown Logic ---------- */
  var customSelects = document.querySelectorAll(".custom-select");
  
  customSelects.forEach(function(select) {
    var trigger = select.querySelector(".select-trigger");
    var options = select.querySelectorAll(".option");
    var hiddenInput = select.querySelector("input[type='hidden']");
    var label = select.querySelector(".select-label");

    // Toggle menu open/close
    trigger.addEventListener("click", function(e) {
      e.stopPropagation();
      // Close any other open dropdowns first
      customSelects.forEach(s => { if(s !== select) s.classList.remove("is-open") });
      select.classList.toggle("is-open");
    });

    // Handle option selection
    options.forEach(function(opt) {
      opt.addEventListener("click", function(e) {
        e.stopPropagation();
        var value = this.getAttribute("data-value");
        var text = this.textContent;

        label.textContent = text;
        hiddenInput.value = value;
        select.classList.remove("is-open");
        select.classList.add("has-value");

        // Force a 'change' event so the existing URL router catches it
        hiddenInput.dispatchEvent(new Event('change'));
      });
    });
  });

  // Close dropdown if user clicks anywhere else on the page
  document.addEventListener("click", function() {
    customSelects.forEach(function(select) {
      select.classList.remove("is-open");
    });
  });
})();
