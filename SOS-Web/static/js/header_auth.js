window.addEventListener("load", async () => {
    const authSlot = document.getElementById("auth-slot");
    const signinModal = document.getElementById("signin-modal");
    const signinForm = document.getElementById("signin-form");
    const signinOpenButtons = document.querySelectorAll("[data-open-signin]");
    const signinCloseButtons = document.querySelectorAll("[data-close-signin]");
    const signinError = document.getElementById("signin-error");

    let currentUser = await getCurrentUser();
    renderAuthUI();

    signinOpenButtons.forEach((button) => {
        button.addEventListener("click", () => {
            openSigninModal();
        });
    });

    signinCloseButtons.forEach((button) => {
        button.addEventListener("click", () => {
            closeSigninModal();
        });
    });

    if (signinModal) {
        signinModal.addEventListener("click", (event) => {
            if (event.target === signinModal) {
                closeSigninModal();
            }
        });
    }

    if (signinForm) {
        signinForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            signinError.textContent = "";

            const formData = new FormData(signinForm);
            const email = formData.get("email")?.trim();
            const password = formData.get("password");

            try {
                const user = await signin(email, password);
                currentUser = user;
                closeSigninModal();
                signinForm.reset();
                renderAuthUI();

                const dashboardPath = getDashboardPathForRole(user.role);
                window.location.href = dashboardPath;
            } catch (error) {
                signinError.textContent = error.message || "Sign in failed.";
            }
        });
    }

    function renderAuthUI() {
        if (!authSlot) return;

        if (currentUser) {
            authSlot.innerHTML = `
                <div class="auth-user-menu">
                    <a class="auth-dashboard-link" href="${getDashboardPathForRole(currentUser.role)}">
                        ${roleLabel(currentUser.role)} Dashboard
                    </a>
                    <button class="auth-signout-button" id="auth-signout-button" type="button">
                        Sign Out
                    </button>
                </div>
            `;

            const signoutButton = document.getElementById("auth-signout-button");
            if (signoutButton) {
                signoutButton.addEventListener("click", async () => {
                    try {
                        await signout();
                    } catch (error) {
                        console.error("Sign out failed:", error);
                    }

                    currentUser = null;
                    renderAuthUI();
                    window.location.href = "/";
                });
            }
        } else {
            authSlot.innerHTML = `
                <button class="auth-signin-button" type="button" data-open-signin>
                    Sign In
                </button>
            `;

            const newSigninButton = authSlot.querySelector("[data-open-signin]");
            if (newSigninButton) {
                newSigninButton.addEventListener("click", openSigninModal);
            }
        }
    }

    function openSigninModal() {
        if (!signinModal) return;
        signinModal.classList.add("is-open");
    }

    function closeSigninModal() {
        if (!signinModal) return;
        signinModal.classList.remove("is-open");
    }
});