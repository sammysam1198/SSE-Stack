document.addEventListener("DOMContentLoaded", async () => {
    const artistSelect = document.getElementById("contract-artist");
    const contractType = document.getElementById("contract-type");
    const contractEmails = document.getElementById("contract-emails");
    const contractNotes = document.getElementById("contract-notes");
    const contractBody = document.getElementById("contract-body");
    const form = document.getElementById("contract-form");
    const saveDraftButton = document.getElementById("save-draft-button");
    const saveSendButton = document.getElementById("save-send-button");
    const errorBox = document.getElementById("contract-error");
    const successBox = document.getElementById("contract-success");
    const formActions = document.getElementById("contract-form-actions");
    const successActions = document.getElementById("contract-success-actions");
    const sendAnotherButton = document.getElementById("send-another-contract-button");
    const backToDashboardButton = document.getElementById("back-to-dashboard-button");

    const params = new URLSearchParams(window.location.search);

    let artists = [];
    let currentUser = null;

    function clearMessages() {
        if (errorBox) errorBox.textContent = "";
        if (successBox) successBox.textContent = "";
    }

    function resetSuccessState() {
        if (formActions) formActions.style.display = "flex";
        if (successActions) successActions.style.display = "none";
    }

    function showSuccessState(message) {
        if (successBox) {
            successBox.textContent = message || "Contract created successfully.";
        }
        if (formActions) formActions.style.display = "none";
        if (successActions) successActions.style.display = "flex";
    }

    function getSelectedArtist() {
        const selectedId = artistSelect?.value;
        return artists.find((artist) => String(artist.id) === String(selectedId)) || null;
    }

    async function loadArtists() {
        const data = await apiFetch("/api/contracts/artists");
        artists = data.artists || [];

        if (!artistSelect) return;

        artistSelect.innerHTML = artists
            .map((artist) => `<option value="${artist.id}">${artist.artist_name}</option>`)
            .join("");

        const prefArtistId = params.get("artist_profile_id");
        const prefType = params.get("type");

        if (prefArtistId) {
            artistSelect.value = prefArtistId;
        }

        if (prefType && ["publishing", "distribution"].includes(prefType) && contractType) {
            contractType.value = prefType;
        }
    }

    function fillDefaultTemplate() {
        const selectedArtist = getSelectedArtist();
        const artistName = selectedArtist?.artist_name || "____________________________";

        if (!contractBody || !contractType) return;

        if (contractType.value === "distribution") {
            contractBody.value = `SpacedOut Studios Entertainment LLC
MASTER RECORDING CONTRACT


This is a contract (hereinafter referred to as the "Agreement") between SpacedOut Studios Entertainment LLC, doing business as “SpacedOut Studios Entertainment”, located at 137 Kelly Driver Rd., Laurel Springs, NJ 08021 (hereinafter referred to as the "Company"), and:

Legal Name: ________________________________

Artist Name: ${artistName}

Address: ___________________________________
____________________________________________

(hereinafter collectively referred to as the "Artist" or "Artist(s)" for the convenience of all parties)

Effective Date: ____ / ____ / ______ (the "Effective Date");


1. MASTER RECORDING(S)

During the term of this Agreement, Artist(s) will, at mutually convenient times, create sound recordings and provide them to the Company for the purpose of distribution and monetization of the compositions.

IT IS HEREBY UNDERSTOOD:

A. Company is an organization which specializes in the digital representation of artists, recording, and recording distribution;

B. Company is familiar with the musical abilities of the Artist(s) and possesses the expertise, ability, industry contacts, and resources to assist the Artist in the furtherance of their career;

C. Artist(s) perform under the name(s): ________________________________;

D. Master Recordings will be licensed to SpacedOut Studios Entertainment LLC and its subsidiaries;

E. Company and Artist(s) wish to enter into this Agreement to provide for the release and distribution of recordings worldwide;

F. Master Recording(s) will be released as Singles, EP(s), and/or Albums.

IT IS, THEREFORE, AGREED AS FOLLOWS:


A. TERM / TERMINATION

The Agreement shall commence on the Effective Date and continue for a period of five (5) years.

Notwithstanding the foregoing, after a period of two (2) years, specifically between April 15, 2028 and May 15, 2028, either the Artist(s) or the Company may terminate this Agreement without penalty by providing written notice.

If neither party elects to terminate the Agreement during such thirty (30) day period, the Agreement shall automatically continue in full force and effect for the remaining term of three (3) years, and neither party shall have any right to terminate this Agreement prior to the expiration of such term, except by mutual written agreement of the parties.


B. PRODUCTION OF RECORDINGS

1. PRODUCTION

Artist(s) agree to produce digital master Recordings (hereinafter referred to as “Recordings”). Master Recordings shall be delivered to Company in WAV and/or MP3 format of a quality consistent with professional standards for digital distribution.

Preferred specifications for WAV files:
24-bit, 44.1 kHz, stereo.


2. COSTS

Any fees or costs incurred in relation to the promotion and release of Recordings shall be recoupable from gross track revenue.

Such costs shall only be incurred upon mutual agreement between Artist(s) and Company.


3. ARTISTIC CONTROL

Company and Artist(s) shall be jointly responsible for decisions regarding all artistic content of the Recordings, including artwork and titles.


4. COMPLETION AND RELEASE

Recordings shall be completed and prepared for digital release. Company agrees to use commercially reasonable efforts to release the Recordings on mutually agreed dates.


5. LICENSE FOR USE OF NAME AND IMAGE

Artist(s) grant Company the right to use their name, likeness, and image in connection with the promotion and distribution of Recordings.


6. TRANSFER OF RIGHTS

A non-exclusive license is hereby granted to Company to distribute, exploit, and monetize the Recordings for the duration of this Agreement.


7. SAMPLES

Artist(s) represent and warrant that all Recordings are original or properly licensed, and do not infringe upon the rights of any third party.


8. DISTRIBUTION

Company shall distribute Recordings worldwide through digital platforms, including but not limited to Spotify, Apple Music, and other services.


9. ROYALTIES & ACCOUNTING

Company shall collect all royalties generated from the distribution of Recordings.

After recoupment of agreed costs, the remaining revenue shall be allocated as follows:

80% to Artist(s)
20% to Company

Royalties shall be paid quarterly, within forty-five (45) days following the end of each quarter.

Minimum payment threshold: $100 USD.

Artist(s) must provide valid payment details for receipt of royalties.


10. NON-CIRCUMVENTION

Artist(s) shall not interfere with Company’s distribution efforts or enter into conflicting agreements regarding the Recordings.


11. MISCELLANEOUS

a. This Agreement shall be binding upon the successors and assigns of the parties.

b. This Agreement shall be governed by and construed in accordance with the laws of the State of New Jersey, without regard to its conflict of law principles.

c. The parties hereby consent to the exclusive jurisdiction and venue of the state and federal courts located within the State of New Jersey for any disputes arising out of or relating to this Agreement.

d. The prevailing party in any dispute shall be entitled to recover reasonable attorney’s fees.

e. Both parties agree to perform in good faith.

f. Artist(s) shall be deemed an independent contractor and not an employee, partner, or agent of Company. Artist(s) shall be solely responsible for all taxes and obligations.

g. Artist(s) may work with other labels provided such activity does not conflict with this Agreement.


12. CURRENCY

All currency references are in United States Dollars (USD).


13. REPRESENTATIONS AND WARRANTIES

Artist(s) represent that they have full authority to enter into this Agreement and that all materials delivered are legally cleared.


14. REMIXES

Company may authorize remixes only with prior written consent of Artist(s).


15. INDEMNITY

Artist(s) agree to indemnify Company against claims arising from breach of this Agreement or infringement.


16. LIMITATION OF LIABILITY

To the maximum extent permitted by law, Company shall not be liable for any indirect, incidental, or consequential damages arising out of this Agreement.


17. ACCEPTANCE

This Agreement may be accepted and executed electronically.


18. ENTIRE AGREEMENT

This Agreement constitutes the entire understanding between the parties and supersedes all prior agreements.


----------------------------------------
SIGNATURES
----------------------------------------

ON BEHALF OF SpacedOut Studios Entertainment LLC:

Name: ________________________________
Signature: ____________________________
Date: ____ / ____ / ______


ARTIST:

Name: ________________________________
Signature: ____________________________
Date: ____ / ____ / ______`;
        } else {
            contractBody.value = `SpacedOut Studios Entertainment LLC
PUBLISHING, LICENSE & ROYALTY AGREEMENT


This music publishing agreement (hereinafter referred to as the "Agreement") is made between:

SpacedOut Studios Entertainment LLC, doing business as “SpacedOut Studios Entertainment”, located at 137 Kelly Driver Rd., Laurel Springs, NJ 08021 (hereinafter referred to as the "Publisher" or "Company"),

and

Licensor Legal Name: ________________________________

Artist Name: ${artistName}

Address: ___________________________________________
___________________________________________________

(hereinafter referred to as the "Licensor")

Effective Date: ____ / ____ / ______


WHEREAS, Licensor is the owner of certain musical compositions (hereinafter referred to as the "Composition(s)") and sound recordings embodying such Composition(s); and

WHEREAS, Publisher is engaged in the business of music publishing, licensing, and exploitation of musical works; and

WHEREAS, Licensor desires to grant Publisher rights to publish, administer, and exploit the Composition(s), and to appoint Publisher as administrator of such Composition(s); and

WHEREAS, Publisher is willing to accept such appointment under the terms set forth herein;

NOW, THEREFORE, the parties agree as follows:


1. GRANT OF RIGHTS

Licensor hereby grants to Publisher, on an exclusive basis, the right to administer, publish, license, and exploit the Composition(s) and related sound recordings throughout the Territory for the duration of this Agreement.

Licensor authorizes Publisher to register the Composition(s) with performance rights organizations (including but not limited to ASCAP, BMI, or SESAC) and to collect the Publisher’s share of royalties.

Licensor further grants Publisher the right to license the Composition(s) and related sound recordings to third parties for use across all media now known or hereafter devised.


2. TERM / TERMINATION

This Agreement shall commence on the Effective Date and continue for a period of five (5) years.

Notwithstanding the foregoing, after a period of two (2) years, specifically between April 15, 2028 and May 15, 2028, either the Licensor or the Publisher may terminate this Agreement without penalty by providing written notice.

If neither party elects to terminate the Agreement during such thirty (30) day period, the Agreement shall automatically continue in full force and effect for the remaining term of three (3) years, and neither party shall have any right to terminate this Agreement prior to the expiration of such term, except by mutual written agreement of the parties.


3. ADMINISTRATION & LICENSING

Publisher shall have the right, but not the obligation, to administer and exploit Licensor’s interest in the Composition(s), including:

- Mechanical licensing
- Performance licensing
- Synchronization licensing
- Digital distribution and usage

Publisher may enter into agreements in Licensor’s name where necessary for the exploitation of the Composition(s).

Publisher shall have the right to issue direct licenses, including licenses involving upfront payments for use of the Composition(s). In such cases, Licensor shall receive compensation as defined under the Royalty provisions of this Agreement.


4. ROYALTIES & ACCOUNTING

Publisher shall pay to Licensor fifty percent (50%) of Net Proceeds derived from the exploitation of the Composition(s).

“Net Proceeds” shall mean all Gross Receipts actually received by Publisher from the exploitation of the Composition(s), less any agreed costs.

Payments shall be made semi-annually, within sixty (60) days following June 30 and December 31 of each year.

Minimum payment threshold: $100 USD.

Licensor shall be responsible for providing valid payment details.


5. COSTS

Any costs incurred in connection with the promotion, licensing, or exploitation of the Composition(s) must be mutually agreed upon and shall be recoupable from Gross Receipts prior to royalty distribution.


6. REPRESENTATIONS & WARRANTIES

Licensor represents and warrants that:

a. Licensor owns or controls all rights necessary to enter into this Agreement;
b. The Composition(s) do not infringe upon any third-party rights;
c. All samples, if any, are properly licensed or cleared.


7. INDEMNIFICATION

Licensor agrees to indemnify, defend, and hold harmless Publisher and its affiliates from any claims arising out of Licensor’s breach of this Agreement.

Publisher agrees to indemnify Licensor from claims arising out of Publisher’s breach of this Agreement.


8. NON-CIRCUMVENTION

Licensor shall not interfere with Publisher’s licensing or exploitation efforts or enter into conflicting agreements regarding the Composition(s).


9. INDEPENDENT CONTRACTOR

Licensor is an independent contractor and not an employee, partner, or agent of Publisher. Licensor shall be solely responsible for all taxes, withholdings, and obligations of any kind.


10. LIMITATION OF LIABILITY

To the maximum extent permitted by law, Publisher shall not be liable for any indirect, incidental, or consequential damages arising from this Agreement.


11. GOVERNING LAW

This Agreement shall be governed by and construed in accordance with the laws of the State of New Jersey, without regard to its conflict of law principles.

The parties consent to the exclusive jurisdiction and venue of the state and federal courts located within the State of New Jersey.


12. ENTIRE AGREEMENT

This Agreement constitutes the entire understanding between the parties and supersedes all prior agreements.

Any modifications must be made in writing and signed by both parties.


----------------------------------------
CONTACT / PRO INFORMATION
----------------------------------------

FULL NAME: __________________________________________
PRO (BMI/ASCAP/SESAC): ______________________________
IPI #: ______________________________________________
ADDRESS: ___________________________________________
PHONE: _____________________________________________
EMAIL: _____________________________________________


----------------------------------------
SIGNATURES
----------------------------------------

LICENSOR:

Name: ________________________________
Signature: ____________________________
Date: ____ / ____ / ______


ON BEHALF OF SpacedOut Studios Entertainment LLC:

Name: ________________________________
Signature: ____________________________
Date: ____ / ____ / ______`;
        }
    }

    function setRecipientEmailsFromSelectedArtist() {
        const selected = getSelectedArtist();
        if (contractEmails) {
            contractEmails.value = (selected?.emails || []).join(", ");
        }
    }

    function resetFormForAnother() {
        clearMessages();
        resetSuccessState();

        if (contractNotes) {
            contractNotes.value = "";
        }

        setRecipientEmailsFromSelectedArtist();
        fillDefaultTemplate();

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    async function submitContract(sendNow) {
        clearMessages();
        resetSuccessState();

        const selectedArtist = getSelectedArtist();
        if (!selectedArtist) {
            if (errorBox) errorBox.textContent = "Please choose an artist.";
            return;
        }

        if (!contractBody || !contractBody.value.trim()) {
            if (errorBox) errorBox.textContent = "Contract body is required.";
            return;
        }

        if (saveDraftButton) saveDraftButton.disabled = true;
        if (saveSendButton) saveSendButton.disabled = true;

        const payload = {
            artist_profile_id: selectedArtist.id,
            artist_name: selectedArtist.artist_name,
            contract_type: contractType?.value || "distribution",
            body_text: contractBody.value.trim(),
            notes: contractNotes?.value?.trim() || "",
            send_now: sendNow,
            recipient_emails: (contractEmails?.value || "")
                .split(",")
                .map((value) => value.trim())
                .filter(Boolean),
        };

        try {
            await apiFetch("/api/contracts", {
                method: "POST",
                body: payload,
            });

            if (sendNow) {
                showSuccessState("Contract created and email sent.");
            } else {
                if (successBox) {
                    successBox.textContent = "Contract draft saved.";
                }
            }

            if (backToDashboardButton && currentUser) {
                if (currentUser.role === "developer") {
                    backToDashboardButton.href = "/dashboard-developer.html";
                } else if (currentUser.role === "admin") {
                    backToDashboardButton.href = "/dashboard-admin.html";
                } else {
                    backToDashboardButton.href = "/";
                }
            }
        } catch (error) {
            if (errorBox) {
                errorBox.textContent = error.message || "Failed to save contract.";
            }
        } finally {
            if (saveDraftButton) saveDraftButton.disabled = false;
            if (saveSendButton) saveSendButton.disabled = false;
        }
    }

    artistSelect?.addEventListener("change", () => {
        setRecipientEmailsFromSelectedArtist();
        fillDefaultTemplate();
        clearMessages();
        resetSuccessState();
    });

    contractType?.addEventListener("change", () => {
        fillDefaultTemplate();
        clearMessages();
        resetSuccessState();
    });

    form?.addEventListener("submit", async (event) => {
        event.preventDefault();
        await submitContract(false);
    });

    saveSendButton?.addEventListener("click", async () => {
        await submitContract(true);
    });

    sendAnotherButton?.addEventListener("click", () => {
        resetFormForAnother();
    });

    try {
        currentUser = await getCurrentUser();
        if (!currentUser || !["admin", "developer"].includes(currentUser.role)) {
            window.location.href = "/";
            return;
        }

        await loadArtists();
        setRecipientEmailsFromSelectedArtist();
        fillDefaultTemplate();
        resetSuccessState();

        if (backToDashboardButton) {
            if (currentUser.role === "developer") {
                backToDashboardButton.href = "/dashboard-developer.html";
            } else if (currentUser.role === "admin") {
                backToDashboardButton.href = "/dashboard-admin.html";
            } else {
                backToDashboardButton.href = "/";
            }
        }
    } catch (error) {
        if (errorBox) {
            errorBox.textContent = error.message || "Failed to load contract editor.";
        }
    }
});