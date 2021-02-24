let findmyplaneConnectionStatus;
let findmyplaneIdentPublicKey;
let findmyplaneUrlToView;

findmyplaneConnectionStatus = 0;
//startFindmyplaneTracking();  //no longer default


function findmyplaneUpdateDisplay() {

    console.log (findmyplaneConnectionStatus)
    if (findmyplaneConnectionStatus === 1) {
        $("#findmyplaneMaster").removeClass("btn-danger").addClass("btn-success").html("Connected to Find My Plane");
        $("#findmyplaneMenuButton").removeClass("btn-danger").addClass("btn-success");
        $("#findmyplaneConnectionStatusLabel").text("Connected to Find My Plane");
        $("#findmyplaneIdentLabel").text(findmyplaneIdentPublicKey).attr('style', 'color: green');
        $("#findmyplaneFollowingUrlButton").show();
        $("#findmyplaneFollowingUrlLabel").html(findmyplaneUrlToView);
    } else {
        $("#findmyplaneMaster").addClass("btn-danger").removeClass("btn-success").html("Disconnected - click to connect");
        $("#findmyplaneMenuButton").addClass("btn-danger").removeClass("btn-success")
        $("#findmyplaneConnectionStatusLabel").text("Disconnected from Find My Plane");
        $("#findmyplaneIdentLabel").text("N/A").attr('style', 'color: red');
        $("#findmyplaneFollowingUrlLabel").html("N/A");
        $("#findmyplaneFollowingUrlButton").hide();

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

function goToTrackingUrl() {

    // This code is pretty ugly but it does allow this to open in another window through javascript
    // See this stackoverflow answer to show what I'm doing
    // https://stackoverflow.com/questions/7930001/force-link-to-open-in-mobile-safari-from-a-web-app-with-javascript
    var a = document.createElement('a');
    a.setAttribute("href", findmyplaneUrlToView);
    a.setAttribute("target", "_blank");

    var dispatch = document.createEvent("HTMLEvents");
    dispatch.initEvent("click", true, true);
    a.dispatchEvent(dispatch);

    // This is the old way of doing it - kept here for reference
    //window.open(findmyplaneUrlToView,"_blank")

}