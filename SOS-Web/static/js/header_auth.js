window.addEventListener("load", async () => {
    const authSlot = document.getElementById("auth-slot");
    let currentUser = await getCurrentUser();
    renderAuthUI();

    document.addEventListener("click", async (event) => {
        const openBtn = event.target.closest("[data-open-signin]");
        if (openBtn) {
            openSigninModal();
            return;
        }

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
        } else {
            authSlot.innerHTML = `
                <button class="auth-signin-button" type="button" data-open-signin>
                    Sign In
                </button>
            `;
        }
    }

    function openSigninModal() {
        const modal = document.getElementById("signin-modal");
        if (!modal) return;
        modal.classList.add("is-open");
    }

    function closeSigninModal() {
        const modal = document.getElementById("signin-modal");
        if (!modal) return;
        modal.classList.remove("is-open");
    }
});