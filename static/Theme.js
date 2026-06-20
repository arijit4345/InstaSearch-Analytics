// Pulse Index — shared interactions
(function () {
  "use strict";

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
      dropzone.classList.remove("is-invalid", "is-valid");
      fileNameEl.style.color = "";

      if (
        file.name.toLowerCase().endsWith(".txt") ||
        file.type === "text/plain"
      ) {
        dropzone.classList.add("is-valid");
        fileNameEl.innerHTML = successSvg + file.name;
        fileNameEl.classList.add("show");

        // Change text to show loading state
        dropText.innerHTML =
          "Uploading dataset... <span class='spinner' style='display:inline-block; border-top-color:var(--mint); width:12px; height:12px;'></span>";

        // Create FormData and send it via Fetch API
        var formData = new FormData();
        formData.append("dataset", file);

        fetch("/upload", {
          method: "POST",
          body: formData,
        })
          .then((response) => response.json()) // Read as JSON now
          .then((data) => {
            dropText.innerHTML = `<strong>${data.message}</strong>`;

            // Populate and reveal the active dataset card
            document.getElementById("current-filename").textContent =
              data.filename;
            document.getElementById("current-count").textContent =
              data.count + " posts";
            document.getElementById("active-dataset-card").style.display =
              "flex";
          })
          .catch((err) => {
            dropzone.classList.remove("is-valid");
            dropzone.classList.add("is-invalid");
            dropText.innerHTML = "Upload failed. Please check your connection.";
            fileNameEl.innerHTML = errorSvg + "Server error.";
          });
      } else {
        dropzone.classList.add("is-invalid");
        fileNameEl.innerHTML =
          errorSvg + "Invalid file. Must be a .txt dataset.";
        fileNameEl.classList.add("show");
        fileNameEl.style.color = "var(--coral)";
        dropText.innerHTML = "File rejected.";
        fileInput.value = "";

        setTimeout(function () {
          if (dropzone.classList.contains("is-invalid")) {
            dropText.innerHTML = originalText;
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

  /* ---------- custom dropdown & filter logic ---------- */
  var customSelect = document.getElementById("custom-filter-wrapper");
  var hiddenInput = document.getElementById("filterSelect");
  var filterBtn = document.getElementById("filter-btn");

  if (customSelect && hiddenInput) {
    var trigger = customSelect.querySelector(".select-trigger");
    var label = customSelect.querySelector(".select-label");
    var options = customSelect.querySelectorAll(".option");

    // Toggle dropdown open/close
    trigger.addEventListener("click", function() {
      customSelect.classList.toggle("is-open");
    });

    // Handle option selection
    options.forEach(function(option) {
      option.addEventListener("click", function() {
        // Update text and value
        label.textContent = this.textContent;
        hiddenInput.value = this.getAttribute("data-value");
        
        // Add active classes and close menu
        customSelect.classList.add("has-value");
        customSelect.classList.remove("is-open", "is-error");
      });
    });

    // Close dropdown if clicking anywhere outside of it
    document.addEventListener("click", function(e) {
      if (!customSelect.contains(e.target)) {
        customSelect.classList.remove("is-open");
      }
    });
  }

  // Handle the "See Posts" button click
  if (filterBtn && hiddenInput && customSelect) {
    filterBtn.addEventListener("click", function () {
      var selected = hiddenInput.value;

      if (selected !== "") {
        window.location.href = selected;
      } else {
        // Reset animation
        customSelect.classList.remove("is-error");
        void customSelect.offsetWidth; 
        
        // Shake the custom select wrapper
        customSelect.classList.add("is-error");
        
        setTimeout(function() {
          customSelect.classList.remove("is-error");
        }, 400);
      }
    });
  }

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
          // Hide the card and stop spinner
          activeCard.style.display = "none";
          deleteBtn.classList.remove("is-loading");

          // Reset the dropzone UI visually
          var dropText = document.querySelector(".drop-text");
          var fileNameEl = document.querySelector(".file-name");
          var dropzone = document.getElementById("dataset-dropzone");

          if (dropText && dropzone) {
            dropText.innerHTML =
              "Drag & drop your <strong>.txt</strong> dataset here, or";
            dropzone.classList.remove("is-valid", "is-invalid");
            if (fileNameEl) {
              fileNameEl.innerHTML = "";
              fileNameEl.classList.remove("show");
            }
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

        // QUICK FIX: Find the submit button and instantly stop the spinner
        var submitBtn = searchForm.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.classList.remove("is-loading");
        }

        // Reset animation
        searchInput.classList.remove("is-error");
        void searchInput.offsetWidth; 
        
        // Apply the red border and shake animation
        searchInput.classList.add("is-error");
        
        // Clean up the class after the 400ms shake animation finishes
        setTimeout(function() {
          searchInput.classList.remove("is-error");
        }, 400);
      }
    });
  }

  /* ---------- Handle Browser Back Button (bfcache) ---------- */
  window.addEventListener("pageshow", function (event) {
    // The 'persisted' property is true if the page was loaded from the browser's back/forward cache
    if (event.persisted) {
      // Force a hard reload from the server to reset all states and fetch fresh data
      window.location.reload();
    }
  });
})();
