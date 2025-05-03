const API_URL = "http://localhost:8010/";
const appState = {
  allSources: [],
};

$(document).ready(function () {
  loadSources();

  // Show Add Source modal
  $("#AddSource").click(function () {
    $("#addSourceModal").modal("show");
  });

  // Handle Add Source form submission
  $("#addSourceForm").submit(function (event) {
    event.preventDefault();

    const sourceName = $("#sourceName").val();

    if (!sourceName) {
      showAlert("danger", "Please fill in the source name.");
      return;
    }

    const newSource = {
      id: 0,
      name: sourceName,
    };

    saveSource(newSource);
  });

  // Handle Edit button click
  $(document).on("click", ".edit-btn", function () {
    const sourceId = $(this).data("source-id");
    const source = appState.allSources.find((s) => s.id === sourceId);

    if (!source) {
      showAlert("danger", "Source not found.");
      return;
    }

    // Populate the modal with the source's data
    $("#editSourceId").val(source.id);
    $("#editSourceName").val(source.name);

    // Show the modal
    $("#editSourceModal").modal("show");
  });

  // Handle Edit Source form submission
  $("#editSourceForm").submit(function (event) {
    event.preventDefault();

    const sourceId = $("#editSourceId").val();
    const updatedSource = {
      id: parseInt(sourceId), // Include the id field
      name: $("#editSourceName").val(),
    };

    if (!updatedSource.name) {
      showAlert("danger", "Please fill in the source name.");
      return;
    }

    updateSource(sourceId, updatedSource);
  });

  // Handle Delete button click
  $(document).on("click", ".delete-btn", function () {
    const sourceId = $(this).data("source-id");

    if (!confirm("Are you sure you want to delete this source?")) {
      return;
    }

    deleteSource(sourceId);
  });
});

function loadSources() {
  showLoading(true);
  $.ajax({
    url: API_URL + "Sources/GetAllSources",
    type: "GET",
    dataType: "json",
    success: function (data) {
      appState.allSources = data;
      renderSources(data);
    },
    error: function (xhr) {
      showAlert("danger", `Failed to load sources: ${xhr.responseJSON?.detail || xhr.statusText}`);
    },
    complete: function () {
      showLoading(false);
    },
  });
}

function renderSources(sources) {
  const tableBody = $("table.table-striped tbody");
  tableBody.empty();

  if (sources.length === 0) {
    tableBody.append('<tr><td colspan="4">No sources found.</td></tr>');
    return;
  }

  const rows = sources.map((source) => {
    return `
      <tr>
        <th>${source.id}</th>
        <td>${source.name}</td>
        
        <td>
          <button type="button" class="btn btn-primary edit-btn" data-source-id="${source.id}">
            Edit
          </button>
          <button type="button" class="btn btn-danger delete-btn" data-source-id="${source.id}">
            Delete
          </button>
        </td>
      </tr>
    `;
  }).join("");

  tableBody.append(rows);
}

function saveSource(source) {
  showLoading(true);
  $.ajax({
    url: API_URL + "Sources/AddSource",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(source),
    success: function (data) {
      showAlert("success", `Source "${data.name}" added successfully.`);
      $("#addSourceModal").modal("hide");
      loadSources();
    },
    error: function (xhr) {
      showAlert("danger", `Failed to save source: ${xhr.responseJSON?.detail || xhr.statusText}`);
    },
    complete: function () {
      showLoading(false);
    },
  });
}

function updateSource(sourceId, updatedSource) {
  showLoading(true);
  $.ajax({
    url: `${API_URL}Sources/UpdateSource/${sourceId}`,
    type: "PUT",
    contentType: "application/json",
    data: JSON.stringify(updatedSource),
    success: function (data) {
      showAlert("success", `Source "${data.name}" updated successfully.`);
      $("#editSourceModal").modal("hide");
      loadSources();
    },
    error: function (xhr) {
      showAlert("danger", `Failed to update source: ${xhr.responseJSON?.detail || xhr.statusText}`);
    },
    complete: function () {
      showLoading(false);
    },
  });
}

function deleteSource(sourceId) {
  showLoading(true);
  $.ajax({
    url: `${API_URL}Sources/DeleteSource/${sourceId}`,
    type: "DELETE",
    success: function (data) {
      showAlert("success", data.message);
      loadSources();
    },
    error: function (xhr) {
      showAlert("danger", `Failed to delete source: ${xhr.responseJSON?.detail || xhr.statusText}`);
    },
    complete: function () {
      showLoading(false);
    },
  });
}

function showLoading(show) {
  if (show) {
    $("#loadingSpinner").addClass("active").removeClass("d-none");
  } else {
    $("#loadingSpinner").removeClass("active").addClass("d-none");
  }
}

function showAlert(type, message) {
  console.log(`[${type.toUpperCase()}] ${message}`);
  const alert = $("#statusAlert");
  alert.removeClass("d-none alert-danger alert-success")
    .addClass(`alert-${type}`)
    .html(message);
  setTimeout(() => alert.addClass("d-none"), 5000);
}