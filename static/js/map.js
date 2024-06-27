let map;
let selectedPoint = null;
let exisingPoints = [];
let points = [];

const FIXED_ICON = "https://cdn-icons-png.flaticon.com/512/602/602182.png";
const MOBILE_ICON = "https://cdn-icons-png.flaticon.com/512/31/31238.png";

const FIXED_COLOR = "0xFCBA03";
const MOBILE_COLOR = "0x000000";

const createNewImage = (type) => {
    const img = document.createElement("img");
    img.src = type === 'Fixo'
        ? FIXED_ICON
        : MOBILE_ICON;

    img.style.width = "30px";
    img.style.height = "30px";
    return img;
}

function removePointFromMap(id) {
    const index = _.findIndex(points, { id: id });
    if (index === -1) return;

    points[index].marker.setMap(null);
}


function getImageFromMap(existingPoint) {
    let data = {
        image: '',
        links: []
    };

    let mapCenter = map.getCenter();
    let zoomLevel = map.getZoom();

    const baseUrl = "https://maps.googleapis.com/maps/api/staticmap";
    const center = `${mapCenter.lat()},${mapCenter.lng()}`;

    let mapMarkers = `markers=color:red|label:A|${existingPoint.lat},${existingPoint.lng}`
    data['links'].push({
        'A': `https://www.google.com/maps/search/?api=1&query=${existingPoint.lat},${existingPoint.lng}`,
        type: 'Ponto selecionado'
    });

    let possibleLabels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (const [index, point] of points.entries()) {
        const color = point.type === 'Fixo' ? FIXED_COLOR : MOBILE_COLOR;
        mapMarkers += `&markers=color:${color}|label:${possibleLabels[index]}|${point.cordinates.lat},${point.cordinates.lng}`;
        data['links'].push({
            [`${possibleLabels[index]}`]: `https://www.google.com/maps/search/?api=1&query=${point.cordinates.lat},${point.cordinates.lng}`,
            type: point.type
        });
    }

    const mapImage = `${baseUrl}?style=visibility:on&center=${center}&zoom=${zoomLevel}&size=400x400&maptype=roadmap&${mapMarkers}&key=${mapsApiKey}`;
    data['image'] = mapImage;
    return data;
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

    let from = document.createElement("input");
    from.setAttribute("type", "month");
    from.setAttribute("name", "from");
    from.setAttribute("value", "2024-01");
    from.classList.add("ww");
    from.classList.add("p-2");
    from.classList.add(type == 'Fixo' ? "ml-5" : "mx-2");
    from.classList.add("fs-6");

    from.addEventListener("change", () => {
        // get the id of the pin
        let id = newPin.dataset.id;

        // remove the point from the array
        let point = _.head(points.filter((point) => point.id === id));
        point['from'] = from.value;
    });

    let to, typing;
    typing = `${type}`;
    if (typing == "Móvel")
    {
        to = document.createElement("input");
        to.setAttribute("type", "month");
        to.setAttribute("name", "to");
        to.setAttribute("value", "2027-12");
        to.classList.add("ww");
        to.classList.add("p-2");
        to.classList.add("mx-2");
        to.classList.add("fs-6");

        to.addEventListener("change", () => {
            // get the id of the pin
            let id = newPin.dataset.id;

            // remove the point from the array
            let point = _.head(points.filter((point) => point.id === id));
            point['to'] = to.value;
        });
    }

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
    newPin.appendChild(from);
    if (typing == "Móvel")
        newPin.appendChild(to);
    newPin.appendChild(deletePoint);

    let newPinesContainer = document.getElementById("add-new-pins");
    newPinesContainer.appendChild(newPin);

    return newPin.dataset.id;
};

async function addNewDraggablePoint(selectedLocation, type) {
    const { InfoWindow } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    const pointId = insetPointInView(type);

    const randomSalt = Math.random() * 0.003;
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
                // map.setCenter(point.cordinates);
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
    infoWindow.close();
    infoWindow.setContent(title);
    infoWindow.open(marker.map, marker);

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