let map;
let points = [];

async function addNewDraggablePoint(type) {
    const { InfoWindow } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    // create a new pin
    let newPin = document.createElement("div");
    newPin.className = "new-pin";
    newPin.innerText = type;

    let newPinesContainer = document.getElementById("add-new-pins");
    newPinesContainer.appendChild(newPin);

    const randomNess = Math.random() * 0.001;
    const draggableMarker = new AdvancedMarkerElement({
        map,
        position: { lat: 38.73067129535301, lng: -9.129937518620784 + randomNess },
        gmpDraggable: true,
        title: type,
    });

    points.push({
        cordinates: { lat: 38.73067129535301, lng: -9.129937518620784 + randomNess },
        type: type,
    });

    const infoWindow = new InfoWindow();
    draggableMarker.addListener("dragend", () => {
        infoWindow.close();
        infoWindow.setContent(`Novo ${type} adicionado`);
        infoWindow.open(draggableMarker.map, draggableMarker);
    });
}

async function initMap() {
    // Request needed libraries.
    const { Map } = await google.maps.importLibrary("maps");

    map = new Map(document.getElementById("map"), {
        center: { lat: 38.73067129535301, lng: -9.129937518620784 },
        zoom: 16,
        mapId: "4504f8b37365c3d0",
    });
}