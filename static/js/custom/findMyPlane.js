let findmyplaneConnectionStatus;
let findmyplaneIdentPublicKey;
let findmyplaneLinkURL;

findmyplaneConnectionStatus = "disconnected";

function toggleFindmyplaneTracking() {

    if (findmyplaneConnectionStatus === "disconnected") {
        startFindmyplaneTracking()
    }

    if (findmyplaneConnectionStatus === "connected") {
        stopFindmyplaneTracking()
    }

}

function startFindmyplaneTracking() {
    $.getJSON($SCRIPT_ROOT + '/findmyplane/status/set/connected', {}, function(data) {
        if (data.status === 'connected') {
            findmyplaneConnectionStatus = 'connected';
            findmyplaneIdentPublicKey = data.ident_public_key;
            findmyplaneLinkURL = data.url_to_view;

            checkAndUpdateButton("#findmyplaneMaster", 1, "Connected", "Disconnected")

            //$("findmyplaneConnectionStatus").html = "Connected"

            window.alert("Connected")
        }

        if (data.status === 'error') {
            findmyplaneConnectionStatus = 'disconnected'

            checkAndUpdateButton("#findmyplaneMaster", 0)
            window.alert("Errored")
        }
    });
}



function stopFindmyplaneTracking() {

    window.alert("Pass")

}