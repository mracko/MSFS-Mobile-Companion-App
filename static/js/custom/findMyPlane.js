let findmyplaneConnectionStatus;
let findmyplaneIdentPublicKey;
let findmyplaneUrlToView;

findmyplaneConnectionStatus = 0;


function findmyplaneUpdateDisplay() {

    console.log (findmyplaneConnectionStatus)
    if (findmyplaneConnectionStatus === 1) {
        $("#findmyplaneMaster").removeClass("btn-danger").addClass("btn-success").html("Connected to Find My Plane");
        $("#findmyplaneMenuButton").removeClass("btn-danger").addClass("btn-success")
        $("#findmyplaneConnectionStatusLabel").text("Connected to Find My Plane");
        $("#findmyplaneIdentLabel").text(findmyplaneIdentPublicKey);
        $("#findmyplaneFollowingUrlLabel").html('<a href="'+findmyplaneUrlToView+'">'+findmyplaneUrlToView+'</a>');
    } else {
        $("#findmyplaneMaster").addClass("btn-danger").removeClass("btn-success").html("Disconnected - click to connect");
        $("#findmyplaneMenuButton").addClass("btn-danger").removeClass("btn-success")
        $("#findmyplaneConnectionStatusLabel").text("Disconnected from Find My Plane");
        $("#findmyplaneIdentLabel").text("N/A");
        $("#findmyplaneFollowingUrlLabel").html("N/A");
    }
    
}

function toggleFindmyplaneTracking() {

    console.log("Change triggered")
    if (findmyplaneConnectionStatus === 0) {
        startFindmyplaneTracking()
    } else {
        stopFindmyplaneTracking()
    }

}


function startFindmyplaneTracking() {
    $.getJSON($SCRIPT_ROOT + '/findmyplane/status/set/connected', {}, function(data) {});
}


function stopFindmyplaneTracking() {
    $.getJSON($SCRIPT_ROOT + '/findmyplane/status/set/disconnected', {}, function(data) {});
}