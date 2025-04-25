var successedStreams = [];
var failedStreams = [];
var issuesStreams = [];

const API_URL = "http://104.194.10.42:8010/";

$(document).ready(function() {
    loadSources();
 
});

 showLoading = (show) => {
    if (show) {
        $("#loadingSpinner").addClass("active").removeClass("d-none");
    } else {
        $("#loadingSpinner").removeClass("active").addClass("d-none");
    }
};

 loadSources = () => {
    showLoading(true);
    $.ajax({
        url: API_URL+"Sources/GetAllSources",
        type: "GET",
        dataType: "json",
        success: function(data) {
            const sourceSelect = $("#sourceSelect");
            sourceSelect.empty().append('<option value="">Select a source</option>');
            
            data.forEach(source => {
                sourceSelect.append(
                    $(`<option value="${source.id}">${source.name}</option>`)
                );
            });
            
            $("#runInspect").prop('disabled', false);
        },
        error: function(xhr) {
            showAlert('danger', `Failed to load sources: ${xhr.responseJSON?.detail || xhr.statusText}`);
        },
        complete: function() {
            showLoading(false);
        }
    });
};

 getVideoUrl = (filePath) => {
    const relativePath = filePath.replace(/^.*recordings[\\/]/, '');
    return API_URL+`recordings/${relativePath.replace(/\\/g, '/')}`;
};

 showAlert = (type, message) => {
    const alert = $("#statusAlert");
    alert.removeClass('d-none alert-danger alert-success')
         .addClass(`alert-${type}`)
         .html(message);
    setTimeout(() => alert.addClass('d-none'), 5000);
};

function OpenDetails(streamId, isFailed){
    $("#details-modal").addClass("show d-block").removeClass("fade d-none");

    var stream = isFailed ? failedStreams.find(stream => stream.stream_id == streamId) : successedStreams.find(stream => stream.stream_id == streamId);
    var html =  renderStreamDetails(stream);

    $("#ulDetails").html(html);
};

function renderStreamDetails(stream){  
     
        let issuesHtml = '';
        if (stream.issues && Object.keys(stream.issues).length > 0) {
            issuesHtml = `
            <div class="mt-2">
                <div class="fw-bold small">Detected Issues:</div>
                <ul class="list-unstyled mb-0">
                    ${Object.entries(stream.issues).map(([issue, exists]) => 
                        exists ? `<li class="text-danger small">• ${issue.replace(/_/g, ' ')}</li>` : ''
                    ).join('')}
                </ul>
            </div>`;
        }
    
        return `
            <li class="list-group-item">
                <div class="fw-bold">Stream Name: ${stream.stream_name}</div>
                <div class="text-muted small">URL: ${stream.url}</div>
                ${stream.error ? `<div class="text-danger small">Error: ${stream.error}</div>` : ''}
                ${issuesHtml}
            </li>
        `;

   }

function CloseModal(){
    $("#details-modal").addClass("fade d-none").removeClass("show d-block");
};
 renderResults = (data) => {

        let failedHtml = '';
        if (data.failure_count > 0 && data.failed && data.failed.length > 0) {
            failedHtml = data.failed.map(failed => `
                            ${renderStreamDetails(failed)}
                        `).join('')
        }

        $("#toggleModal").removeAttr("style");
        $("#toggleModal").attr("style" , "display:block; z-index: 1000;");
        $("#toggleModal").attr("style" , "display:block; z-index: 1000;");

        if(failedHtml == '') {
            $("#successfullDiv").removeAttr("style");
            $("#successfullDiv").attr("style" , "display:block");

            $("#toggleButton").removeAttr("style");
            $("#toggleButton").attr("style" , "display:none");
            $("#panelTitle").text('');
            $("#detailsPanel").html("All Streams processed successfully!");
        }else{
            

            $("#toggleButton").text(`${data.failure_count} Failed Streams`);

            $("#toggleButton").removeAttr("style");
            $("#toggleButton").attr("style" , "display:block");

            $("#successfullDiv").removeAttr("style");
            $("#successfullDiv").attr("style" , "display:none");

            $("#panelTitle").text(`Server failed to connect to ${data.failure_count} streams`);
            $("#detailsPanel").html(failedHtml);
        }


        var videosHtml = data.failed.map(recording => {
            const displayName = recording.stream_name;
            const streamId = recording.stream_id;
            
           
            return `
            <div class="card animate__animated animate__fadeIn">
                <div class="card-body p-0">
                    <div class="ratio ratio-16x9">
                        <video loop muted autoplay playsinline preload="metadata">
                            <source src="" type="video/mp4"">
                            <p>video is unavailable.</p>
                        </video>
                    </div>
                    <div class="p-3">
                        <h5 class="card-title" style="color:red;">${displayName}</h5>
                        <div class="text-danger small mb-2">Connection drops</div>
                        <div class="d-flex gap-2">
                           
                            <button class="btn btn-sm btn-outline-primary copy-btn" 
                                    onclick="OpenDetails(${streamId}, true)"
                                    >
                                <i class="bi"></i> Capture Details
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            `;
        }).join('');

       
        const successfulWithIssues = data.successful.filter(stream => Object.keys(stream.issues).length > 0);
        const successfulWithoutIssues = data.successful.filter(stream => Object.keys(stream.issues).length === 0);
 
       
        videosHtml += successfulWithIssues.map(recording => {
            const displayName = recording.stream_name;
            const streamId = recording.stream_id;
            const videoUrl = getVideoUrl(recording.output_file);
            const issues = Object.keys(recording.issues).join(', ');
            return `
                <div class="card animate__animated animate__fadeIn">
                    <div class="card-body p-0">
                        <div class="ratio ratio-16x9">
                            <video loop muted autoplay playsinline preload="metadata">
                                <source src="${videoUrl}?t=${Date.now()}" type="video/mp4">
                            </video>
                        </div>
                        <div class="p-3">
                            <h5 class="card-title" style="color:red;">${displayName}</h5>
                            ${issues ? `<div class="text-danger small mb-2">Issues: ${issues}</div>` : ''}
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-outline-primary copy-btn" 
                                        onclick="OpenDetails(${streamId}, false)">
                                    <i class="bi"></i> Capture Details
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    
        
        videosHtml += successfulWithoutIssues.map(recording => {
            const displayName = recording.stream_name;
            const streamId = recording.stream_id;
            const videoUrl = getVideoUrl(recording.output_file);
            return `
                <div class="card animate__animated animate__fadeIn">
                    <div class="card-body p-0">
                        <div class="ratio ratio-16x9">
                            <video loop muted autoplay playsinline preload="metadata">
                                <source src="${videoUrl}?t=${Date.now()}" type="video/mp4">
                            </video>
                        </div>
                        <div class="p-3">
                            <h5 class="card-title">${displayName}</h5>
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-outline-primary copy-btn" 
                                        onclick="OpenDetails(${streamId}, false)">
                                    <i class="bi"></i> Capture Details
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    
        $("#videoGrid").html(videosHtml);
    };

$("#runInspect").click(function() {
    
    $("#videoGrid").html(`<div class="empty-state text-center py-5">
              <i class="bi bi-camera-video-off fs-1 text-muted"></i>
              <p class="text-muted">No inspection results yet</p>
            </div>`);
    const sourceId = $("#sourceSelect").val();
    if (!sourceId) {
        showAlert('warning', 'Please select a source first');
        return;
    }

    const duration = $("#durationSelect").val(); 
    
    showLoading(true);
    try {
         $.ajax({
            url: API_URL+`Streams/record-streams-by-source/${sourceId}/${duration}`,
            type: "POST",
            dataType: "json",
            success: function(data) {
                successedStreams = data.successful;
                failedStreams = data.failed;

                renderResults(data);
                showAlert('success', `Inspection completed: ${data.success_count} successful, ${data.failure_count} failed`);
            },
            error: function(xhr) {
                showAlert('danger', `Inspection failed: ${xhr.responseJSON?.detail || xhr.statusText}`);
            },
            complete: function() {
                showLoading(false);
            }
        });
    }catch (error) {
        console.error("Error during inspection:", error);
        showAlert('danger', 'An unexpected error occurred. Please try again.');
    }
});

$("#toggleButton").click(function() {
    if ($('#detailsPanel').hasClass('collapse')) {
        $("#detailsPanel").removeClass("collapse").addClass("show");
    }else{
        $("#detailsPanel").removeClass("show").addClass("collapse");
    }
})



// Logout functionality
function logout() {
    console.log("Logout function triggered"); // Debug log
    $.ajax({
        url: API_URL + "logout", // Backend logout endpoint
        type: "POST",
        xhrFields: {
            withCredentials: true, // Include cookies in the request
        },
        success: function () {
            console.log("Logout successful"); // Debug log
            alert("You have been logged out.");
            window.location.href = "/"; // Redirect to the login page
        },
        error: function (xhr, status, error) {
            console.error("Logout failed:", status, error); // Debug log
            alert("Failed to log out. Please try again.");
        },
    });
}

$(document).on("click", "#logoutButton", function (event) {
    event.preventDefault(); // Prevent default behavior (e.g., form submission or page refresh)
    logout();
});
