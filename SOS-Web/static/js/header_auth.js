let currentUser = null;

function openSigninModal() {
    const signinModal = document.getElementById("signin-modal");
    if (!signinModal) return;
    signinModal.classList.add("is-open");
}

function closeSigninModal() {
    const signinModal = document.getElementById("signin-modal");
    if (!signinModal) return;
    signinModal.classList.remove("is-open");
}

function bindSigninButtons() {
    document.querySelectorAll("[data-open-signin]").forEach((button) => {
        if (button.dataset.signinBound === "true") return;

        button.dataset.signinBound = "true";
        button.addEventListener("click", (event) => {
            event.preventDefault();
            openSigninModal();
        });
    });
}

function renderAuthUI() {
    const authSlot = document.getElementById("auth-slot");
    if (!authSlot) return;

    authSlot.classList.remove("auth-slot-pending");

    if (currentUser) {
        authSlot.innerHTML = `
            <div class="auth-user-menu">
                <a class="auth-dashboard-link" href="${getDashboardPathForRole(currentUser.role)}">
                    Dashboard
                </a>
                <button class="auth-signout-button" id="auth-signout-button" type="button">
                    Sign Out
                </button>
            </div>
        `;
    } else {
        authSlot.innerHTML = `
            <a class="auth-dashboard-link" href="#" data-open-signin>
                Dashboard
            </a>
            <button class="auth-signin-button" type="button" data-open-signin>
                Sign In
            </button>
        `;

        bindSigninButtons();
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    bindSigninButtons();

    try {
        currentUser = await getCurrentUser();
    } catch (error) {
        currentUser = null;
    }

    renderAuthUI();
});

document.addEventListener("click", async (event) => {
    const closeBtn = event.target.closest("[data-close-signin]");
    if (closeBtn) {
        closeSigninModal();
        return;
    }

    const modal = document.getElementById("signin-modal");
    if (modal && event.target === modal) {
        closeSigninModal();
        return;
    }

    const passwordToggle = event.target.closest("#signin-password-toggle");
    if (passwordToggle) {
        const passwordInput = document.getElementById("signin-password");
        const passwordToggleIcon = document.getElementById("signin-password-toggle-icon");

        if (!passwordInput || !passwordToggleIcon) return;

        const isHidden = passwordInput.type === "password";
        passwordInput.type = isHidden ? "text" : "password";
        passwordToggleIcon.src = isHidden
            ? "/static/assets/show_password.png"
            : "/static/assets/hide_password.png";

        passwordToggle.setAttribute(
            "aria-label",
            isHidden ? "Hide password" : "Show password"
        );
    }

    const signoutButton = event.target.closest("#auth-signout-button");
    if (signoutButton) {
        try {
            await signout();
        } catch (error) {
            console.error("Sign out failed:", error);
        }

        currentUser = null;
        renderAuthUI();
        window.location.href = "/";
    }
});

document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!form || form.id !== "signin-form") return;

    event.preventDefault();

    const signinError = document.getElementById("signin-error");
    if (signinError) signinError.textContent = "";

    const formData = new FormData(form);
    const email = formData.get("email")?.trim();
    const password = formData.get("password");

    try {
        const user = await signin(email, password);
        currentUser = user;
        closeSigninModal();
        form.reset();
        renderAuthUI();

        const dashboardPath = getDashboardPathForRole(user.role);
        window.location.href = dashboardPath;
    } catch (error) {
        if (signinError) {
            signinError.textContent = error.message || "Sign in failed.";
        }
    }
});