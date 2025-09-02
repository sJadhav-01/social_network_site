const csrfToken = document
  .querySelector('meta[name="csrf-token"]')
  .getAttribute("content");
// console.log(csrfToken);

// post like status
document.querySelectorAll(".like-btn").forEach((button) => {
  button.addEventListener("click", function (e) {
    const postId = this.dataset.postId;
    const likeIcon = this.querySelector("i");
    const likeCountSpan = document.getElementById(`like-count-${postId}`);

    fetch(`/api/like/${postId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken, //"{% csrf_token %}", // Important for Django security
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "liked") {
          likeIcon.classList.remove("bi-hand-thumbs-up");
          likeIcon.classList.add("bi-hand-thumbs-up-fill");
          likeCountSpan.textContent = data.likes;
        } else if (data.status === "unliked") {
          likeIcon.classList.remove("bi-hand-thumbs-up-fill");
          likeIcon.classList.add("bi-hand-thumbs-up");
          likeCountSpan.textContent = data.likes;
        }
      })
      .catch((error) => console.error("Error:", error));
  });
});

// request status

document.querySelectorAll(".friend-req-btn").forEach((button) => {
  button.addEventListener("click", function (e) {
    const otherUserId = this.dataset.otherUserId;
    const btnText = this.querySelector("h6");

    fetch(`/api/friendreqto/${otherUserId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.request_status === "request_sent") {
          button.classList.remove("btn-primary");
          button.classList.add("btn-secondary");
          btnText.textContent = "requested";
        } else if (data.request_status === "request_not_sent") {
          button.classList.remove("btn-secondary");
          button.classList.add("btn-primary");
          btnText.textContent = "Add as Friend";
        }
      })
      .catch((error) => console.error("Error:", error));
  });
});

// accepting friend request

// Get all action buttons for friend requests
document.querySelectorAll(".friend-req-action-btn").forEach((button) => {
    button.addEventListener("click", function (e) {
        const receivedReqId = this.dataset.receivedReqId; // data-received-req-id="{{ received_req.id }}"
        const action = this.dataset.action; // the action from a data attribute

        if (!receivedReqId || !action) {
            console.error("Missing request ID or action.");
            return;
        }

        fetch(`/api/reqaccept/${receivedReqId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ action: action })
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.request_status === "accepted" || data.request_status === "rejected") {
                // Find the parent card or container and remove it
              const card = this.closest(".friend-req-card");
              // const card = this.querySelector(".friend-req-card");
                if (card) {
                    card.remove(); // This removes the entire card from the DOM
                }
            } else {
                console.log("Unexpected status:", data.request_status);
            }
        })
        .catch((error) => console.error("Error:", error));
    });
});