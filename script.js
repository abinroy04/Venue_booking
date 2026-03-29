const API = "http://localhost:5000/api";
const token = localStorage.getItem("token");

// Load Clubs
async function loadClubs() {
  const res = await fetch(API + "/clubs");
  const data = await res.json();

  const clubSelect = document.getElementById("club");
  data.data.forEach(c => {
    clubSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
  });
}

// Load Venues
async function loadVenues() {
  const res = await fetch(API + "/venues");
  const data = await res.json();

  const venueSelect = document.getElementById("venue");
  data.data.forEach(v => {
    venueSelect.innerHTML += `<option value="${v.id}">${v.name}</option>`;
  });
}

// On Venue Change → Load Amenities + Items
document.getElementById("venue").addEventListener("change", async function() {
  const venueId = this.value;

  // Load amenities
  const res = await fetch(`${API}/venues/${venueId}`);
  const data = await res.json();

  const amenitiesDiv = document.getElementById("amenities");
  amenitiesDiv.innerHTML = "";

  data.data.facilities.forEach(item => {
    amenitiesDiv.innerHTML += `
      <label><input type="checkbox" value="${item}" class="amenity"> ${item}</label>`;
  });

  // Load venue items
  const resItems = await fetch(`${API}/venues/${venueId}/items`);
  const itemsData = await resItems.json();

  const itemsDiv = document.getElementById("items");
  itemsDiv.innerHTML = "";

  itemsData.data.forEach(item => {
    itemsDiv.innerHTML += `
      <div class="flex gap-2 items-center mb-2">
        <span>${item.item_name}</span>
        <input type="number" min="0" value="0" class="item-qty border p-1 w-20"
          data-id="${item.id}">
      </div>`;
  });
});

// Submit Form
document.getElementById("eventForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const msg = document.getElementById("msg");

  const phone = document.getElementById("faculty_phone").value;
  if (!/^\d{10}$/.test(phone)) {
    msg.innerText = "Invalid phone number!";
    msg.className = "text-red-500";
    return;
  }

  const start = new Date(document.getElementById("start_time").value);
  const end = new Date(document.getElementById("end_time").value);

  if (end <= start) {
    msg.innerText = "End time must be after start time!";
    msg.className = "text-red-500";
    return;
  }

  const venueId = document.getElementById("venue").value;

  // 🔥 Availability Check
  const check = await fetch(API + "/bookings/check-availability", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      venue_id: venueId,
      booking_date: start.toISOString().split("T")[0],
      start_time: start.toTimeString().slice(0,5),
      end_time: end.toTimeString().slice(0,5)
    })
  });

  const checkData = await check.json();

  if (!checkData.data.available) {
    msg.innerText = "Slot already booked!";
    msg.className = "text-red-500";
    return;
  }

  // Amenities
  const amenities = Array.from(document.querySelectorAll(".amenity:checked"))
    .map(a => a.value);

  // Venue Items
  const items = Array.from(document.querySelectorAll(".item-qty"))
    .filter(i => i.value > 0)
    .map(i => ({
      item_id: i.dataset.id,
      quantity: parseInt(i.value)
    }));

  const formData = new FormData();

  formData.append("event_title", document.getElementById("event_title").value);
  formData.append("description", document.getElementById("description").value);
  formData.append("faculty_coordinator_name", document.getElementById("faculty_name").value);
  formData.append("faculty_coordinator_phone_number", phone);
  formData.append("event_type", document.getElementById("event_type").value);

  formData.append("start_date", start.toISOString().split("T")[0]);
  formData.append("start_time", start.toTimeString().slice(0,5));
  formData.append("end_date", end.toISOString().split("T")[0]);
  formData.append("end_time", end.toTimeString().slice(0,5));

  formData.append("associated_club_id", document.getElementById("club").value);
  formData.append("venue_id", venueId);
  formData.append("venue_amenities", amenities.join(","));
  formData.append("venue_items", JSON.stringify(items));

  formData.append("approval_document", document.getElementById("file").files[0]);

  try {
    const res = await fetch(API + "/bookings", {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + token
      },
      body: formData
    });

    const data = await res.json();

    if (data.success) {
      msg.innerText = "Event created successfully!";
      msg.className = "text-green-500";
      document.getElementById("eventForm").reset();
    } 
    else if (data.error?.code === "BOOKING_CONFLICT") {
      msg.innerText = "Conflict: Slot already booked!";
      msg.className = "text-red-500";
    } 
    else {
      msg.innerText = data.error.message;
      msg.className = "text-red-500";
    }

  } catch (err) {
    msg.innerText = "Server error!";
    msg.className = "text-red-500";
  }
});

// Init
loadClubs();
loadVenues();