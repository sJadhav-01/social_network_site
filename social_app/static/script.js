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
          likeCountSpan.textContent = data.likes_count;
        } else if (data.status === "unliked") {
          likeIcon.classList.remove("bi-hand-thumbs-up-fill");
          likeIcon.classList.add("bi-hand-thumbs-up");
          likeCountSpan.textContent = data.likes_count;
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
          btnText.textContent = "Requested";
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
      body: JSON.stringify({ action: action }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (
          data.request_status === "accepted" ||
          data.request_status === "rejected"
        ) {
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

// Function to fetch and display comments

function fetchAndDisplayComments(postId) {
  fetch(`/api/postcomment/${postId}/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      // Get the comments container for this specific post
      const commentsContainer = document.getElementById(
        `comments-container-${postId}`
      );
      if (!commentsContainer) return; // Exit if container not found

      // Clear any existing comments to prevent duplicates
      commentsContainer.innerHTML = "";

      // Loop through the fetched comments
      const comments = data.comments_on_post; // Use data from GET request
      for (const cmt of comments) {
        // Create comment elements
        const commentDiv = document.createElement("div");
        commentDiv.classList.add("comment-item");

        const userNameElement = document.createElement("h6");
        const commentElement = document.createElement("p");

        // Access data correctly
        userNameElement.textContent = `${cmt.user_first_name} ${cmt.user_last_name}`;
        commentElement.textContent = cmt.comment_content;

        // Append elements
        commentDiv.appendChild(userNameElement);
        commentDiv.appendChild(commentElement);
        commentsContainer.appendChild(commentDiv);
      }
    })
    .catch((error) => console.error("Error fetching comments:", error));
}

// Event listener for "Comment" button
document.querySelectorAll(".comment-btn").forEach((button) => {
  button.addEventListener("click", function (e) {
    const divId = this.dataset.divId;
    const postId = this.dataset.postId;
    const commentSect = document.getElementById(divId);

    if (commentSect.hasAttribute("hidden")) {
      commentSect.removeAttribute("hidden");
      // Fetch and display comments only when revealing the section
      fetchAndDisplayComments(postId);
    } else {
      commentSect.setAttribute("hidden", "");
    }
  });
});

// Event listener for "Post comment" button
document.querySelectorAll(".save-comment-btn").forEach((button) => {
  button.addEventListener("click", function (e) {
    const divId = this.dataset.divId;
    const commentSect = document.getElementById(divId);
    const textareaId = this.dataset.textareaId;
    const commentArea = document.getElementById(textareaId);
    const postId = commentArea.dataset.postId;
    const commentContent = commentArea.value;
    const commentCountSpan = document.getElementById(`comment-count-${postId}`);
    if (!commentContent.trim()) {
      alert("Comment cannot be empty.");
      return;
    }

    fetch(`/api/postcomment/${postId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ comment_content: commentContent }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "added") {
          commentArea.value = "";
          commentSect.setAttribute("hidden", "");
          commentCountSpan.textContent = data.comments_count;

          // Re-fetch comments to show the newly added one
          fetchAndDisplayComments(postId);
        }
      })
      .catch((error) => console.error("Error posting comment:", error));
  });
});

// deleteing post

document.querySelectorAll(".post-delete-btn").forEach((button) => {
  button.addEventListener("click", function (e) {
    const postId = this.dataset.postId;
    const cardId = this.dataset.cardId;
    const postCard = document.getElementById(cardId);

    fetch(`/api/deletepost/${postId}/`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "deleted") {
          if (postCard) {
            postCard.remove(); // This removes the entire card from the DOM
          }
        } else {
          console.log("Unexpected status:", data.status);
        }
      })
      .catch((error) => console.error("Error posting comment:", error));
  });
});
