const API_URL = "http://localhost:8010/";
let streamIdToDelete = null;
const appState = {
    sourceMap: {},
    currentPage: 1,
    pageSize: 25,
    totalPages: 1,
    allStreams: [],
};

$(document).ready(function () {
    loadSources();
    loadStreams();

    // Handle source selection
    $("#sourceSelect").change(function () {
        const sourceId = $(this).val();
        console.log("Selected sourceId:", sourceId);

        appState.currentPage = 1;
        loadStreams(sourceId);
    });

    // Handle search input with debounce
    $("#searchInput").on(
        "input",
        debounce(function () {
            const query = $(this).val().toLowerCase();
            const filteredStreams = appState.allStreams.filter((stream) =>
                stream.stream_name.toLowerCase().includes(query) ||
                stream.stream_url.toLowerCase().includes(query)
            );
            renderStreams(filteredStreams);
        }, 300)
    );

    // Show Add Stream modal
    $("#AddStream").click(function () {
        $("#addStreamModal").modal("show");
    });

    // Handle Add Stream form submission
    $("#addStreamForm").submit(function (event) {
        event.preventDefault();

        const streamName = $("#streamName").val();
        const streamUrl = $("#streamUrl").val();
        const sourceId = $("#sourceId").val();

        if (!streamName || !streamUrl || !sourceId) {
            showAlert("danger", "Please fill in all fields.");
            return;
        }

        const newStream = {
            id: 0,
            stream_name: streamName,
            stream_url: streamUrl,
            sourceID: parseInt(sourceId),
        };

        saveStream(newStream);
    });

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

    // Handle page size selection
    $("#pageSizeSelect").change(function () {
        const selectedValue = $(this).val();
        appState.pageSize = selectedValue === "all" ? 100000 : parseInt(selectedValue);
        appState.currentPage = 1;

        // Get the currently selected sourceId
        const sourceId = $("#sourceSelect").val();
        loadStreams(sourceId); // Pass the selected sourceId to loadStreams
    });

    // Handle Edit button click
    $(document).on("click", ".edit-btn", function () {
        const streamId = $(this).data("stream-id");
        const stream = appState.allStreams.find((s) => s.id === streamId);

        if (!stream) {
            showAlert("danger", "Stream not found.");
            return;
        }

        // Populate the modal with the stream's data
        $("#editStreamId").val(stream.id);
        $("#editStreamName").val(stream.stream_name);
        $("#editStreamUrl").val(stream.stream_url);
        $("#editSourceId").val(stream.sourceID);

        // Show the modal
        $("#editStreamModal").modal("show");
    });

    // Handle Edit Stream form submission
    $("#editStreamForm").submit(function (event) {
        event.preventDefault();

        const streamId = $("#editStreamId").val();
        const updatedStream = {
            stream_name: $("#editStreamName").val(),
            stream_url: $("#editStreamUrl").val(),
            sourceID: parseInt($("#editSourceId").val()),
        };

        if (!updatedStream.stream_name || !updatedStream.stream_url || !updatedStream.sourceID) {
            showAlert("danger", "Please fill in all fields.");
            return;
        }

        updateStream(streamId, updatedStream);
    });

    $(document).on("click", ".delete-btn", function () {
        const streamId = $(this).data("stream-id");
    
        if (!confirm("Are you sure you want to delete this stream?")) {
            return;
        }
    
        deleteStream(streamId);
    });
});

function saveStream(stream) {
    showLoading(true);
    $.ajax({
        url: API_URL + "Streams/SaveStream",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(stream),
        success: function (data) {
            showAlert("success", `Stream "${data.stream_name}" added successfully.`);
            $("#addStreamModal").modal("hide");
            const sourceId = $("#sourceSelect").val();

            loadStreams(sourceId); // Reload the streams
        },
        error: function (xhr) {
            showAlert("danger", `Failed to save stream: ${xhr.responseJSON?.detail || xhr.statusText}`);
        },
        complete: function () {
            showLoading(false);
        },
    });
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

function loadStreams(sourceId = null, page = 1) {
    showLoading(true);
    const offset = appState.pageSize ? (page - 1) * appState.pageSize : 0;
    const limit = appState.pageSize || 0;
    let url = `${API_URL}Streams/GetAllStreams?offset=${offset}&limit=${limit}`;

    if (sourceId) {
        url += `&sourceID=${sourceId}`;
    }

    console.log("Fetching streams from URL:", url);

    $.ajax({
        url: url,
        type: "GET",
        dataType: "json",
        success: function (data, textStatus, xhr) {
            console.log("Fetched streams:", data);
            appState.allStreams = data;
            renderStreams(data);

            const totalCount = parseInt(xhr.getResponseHeader("X-Total-Count")) || data.length;
            $("#totalCount").text(`Total Streams: ${totalCount}`);

            appState.totalPages = appState.pageSize ? Math.ceil(totalCount / appState.pageSize) : 1;
        },
        error: function (xhr) {
            console.log("Error loading streams:", xhr);
            showAlert("danger", `Failed to load streams: ${xhr.responseJSON?.detail || xhr.statusText}`);
        },
        complete: function () {
            showLoading(false);
        },
    });
}

function loadSources() {
    showLoading(true);
    $.ajax({
        url: API_URL + "Sources/GetAllSources",
        type: "GET",
        dataType: "json",
        success: function (data) {
            appState.sourceMap = data.reduce((map, source) => {
                map[source.id] = source.name;
                return map;
            }, {});

            const sourceSelect = $("#sourceSelect");
            sourceSelect.empty().append('<option value="">All Sources</option>');

            data.forEach((source) => {
                sourceSelect.append(
                    $(`<option value="${source.id}">${source.name}</option>`)
                );
            });

            const sourceIdSelect = $("#sourceId");
            sourceIdSelect.empty().append('<option value="" selected disabled>Select a source</option>');

            data.forEach((source) => {
                sourceIdSelect.append(
                    $(`<option value="${source.id}">${source.name}</option>`)
                );
            });

            const editSourceIdSelect = $("#editSourceId");
            editSourceIdSelect.empty().append('<option value="" selected disabled>Select a source</option>');

            data.forEach((source) => {
                editSourceIdSelect.append(
                    $(`<option value="${source.id}">${source.name}</option>`)
                );
            });
        },
        error: function (xhr) {
            showAlert("danger", `Failed to load sources: ${xhr.responseJSON?.detail || xhr.statusText}`);
        },
        complete: function () {
            showLoading(false);
        },
    });
}

function renderStreams(streams) {
    const tableBody = $("table.table-striped tbody");
    tableBody.empty();

    if (streams.length === 0) {
        tableBody.append('<tr><td colspan="6">No streams found.</td></tr>');
        return;
    }

    const rows = streams.map((stream) => {
        const sourceName = appState.sourceMap[stream.sourceID] || "Unknown";
        return `
            <tr>
                <th>${stream.id}</th>
                <td>${stream.stream_name}</td>
                <td>${sourceName}</td>
                <td>${stream.stream_url}</td>
                <td>
                    <button type="button" class="btn btn-primary edit-btn" data-stream-id="${stream.id}">
                        Edit
                    </button>
                    <button type="button" class="btn btn-danger delete-btn" data-stream-id="${stream.id}">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    }).join("");

    tableBody.append(rows);
}

function updateStream(streamId, updatedStream) {
    showLoading(true);
    const requestBody = {
        id: parseInt(streamId), // Include the id field
        ...updatedStream, // Spread the other updated fields
    };

    $.ajax({
        url: `${API_URL}Streams/UpdateStream/${streamId}`,
        type: "PUT",
        contentType: "application/json",
        data: JSON.stringify(requestBody),
        success: function (data) {
            showAlert("success", `Stream "${data.stream_name}" updated successfully.`);
            $("#editStreamModal").modal("hide");
            const sourceId = $("#sourceSelect").val();

            loadStreams(sourceId); // Reload the streams
        },
        error: function (xhr) {
            showAlert("danger", `Failed to update stream: ${xhr.responseJSON?.detail || xhr.statusText}`);
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

function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

function deleteStream(streamId) {
    showLoading(true);
    $.ajax({
        url: `${API_URL}Streams/DeleteStream/${streamId}`,
        type: "DELETE",
        success: function (data) {
            showAlert("success", data.message);
            const sourceId = $("#sourceSelect").val();
            loadStreams(sourceId); // Reload the streams
        },
        error: function (xhr) {
            showAlert("danger", `Failed to delete stream: ${xhr.responseJSON?.detail || xhr.statusText}`);
        },
        complete: function () {
            showLoading(false);
        },
    });
}


