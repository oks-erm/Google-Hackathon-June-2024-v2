let map;
let selectedPoint = null;
let exisingPoints = [];
let points = [];

const createNewImage = (type) => {
    const img = document.createElement("img");
    img.src = type === 'Fixo'
        ? "https://cdn-icons-png.flaticon.com/512/602/602182.png"
        : "https://cdn-icons-png.flaticon.com/512/31/31238.png";

    img.style.width = "30px";
    img.style.height = "30px";
    return img;
}

function removePointFromMap(id) {
    const index = _.findIndex(points, { id: id });
    if (index === -1) return;

    points[index].marker.setMap(null);
}


const insetPointInView = (type) => {
    // create a new pin
    let newPin = document.createElement("div");
    // add data id to the pin to use on delete later
    newPin.dataset.id = `${type}-pin-${points.length + 1}`;

    let pinText = document.createElement("p");
    pinText.innerText = `Ponto ${type}`;
    pinText.className = "pin-text";

    let deletePoint = document.createElement("button");
    deletePoint.innerText = "X";
    deletePoint.className = "delete-point";

    deletePoint.onclick = () => {
        // get the id of the pin
        let id = newPin.dataset.id;

        // remove the point from the array
        removePointFromMap(id);
        points = points.filter((point) => point.id !== id);
        newPin.remove();
    };

    newPin.className = "new-pin";
    newPin.appendChild(createNewImage(type));
    newPin.appendChild(pinText);
    newPin.appendChild(deletePoint);

    let newPinesContainer = document.getElementById("add-new-pins");
    newPinesContainer.appendChild(newPin);

    return newPin.dataset.id;
};

async function addNewDraggablePoint(selectedLocation, type) {
    const { InfoWindow } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    const pointId = insetPointInView(type);

    const randomSalt = Math.random() * 0.001;
    const draggableMarker = new AdvancedMarkerElement({
        map,
        position: {
            lat: selectedLocation.lat + randomSalt,
            lng: selectedLocation.lng + randomSalt,
        },
        gmpDraggable: true,
        content: createNewImage(type),
        title: type,
        id: pointId
    });

    points.push({
        cordinates: {
            lat: selectedLocation.lat + randomSalt,
            lng: selectedLocation.lng + randomSalt,
        },
        type: type,
        id: pointId,
        marker: draggableMarker,
    });

    const infoWindow = new InfoWindow();
    draggableMarker.addListener("click", () => {
        infoWindow.close();
        infoWindow.setContent(`Ponto ${type}`);
        infoWindow.open(draggableMarker.map, draggableMarker);
    });

    draggableMarker.addListener("dragend", (e) => {
        points = points.map((point) => {
            if (point.id === pointId) {
                point.cordinates = {
                    lat: e.latLng.lat(),
                    lng: e.latLng.lng(),
                };
                map.setCenter(point.cordinates);
            }
            return point;
        });
    });

}

async function addNewNonDraggabePoint(cord, title, center = false) {
    const { InfoWindow } = await google.maps.importLibrary("maps");
    const { Marker } = await google.maps.importLibrary("marker");

    const marker = new Marker({
        position: cord,
        map: map,
        draggable: false,
        animation: google.maps.Animation.DROP,
        title: title,
    });

    if (center) {
        map.setCenter(cord);
    }

    exisingPoints.push({
        cordinates: cord,
        title: title,
    });

    const infoWindow = new InfoWindow();
    marker.addListener("click", () => {
        infoWindow.close();
        infoWindow.setContent(title);
        infoWindow.open(marker.map, marker);
    });
}

async function initMap() {
    // Request needed libraries.
    const { Map } = await google.maps.importLibrary("maps");

    map = new Map(document.getElementById("map"), {
        zoom: 13,
        mapId: "4504f8b37365c3d0",
    });
}

async function initEditMap() {
    // Request needed libraries.
    const { Map } = await google.maps.importLibrary("maps");

    map = new Map(document.getElementById("map"), {
        zoom: 14,
        mapId: "4504f8b37365c3d0",
    });
}