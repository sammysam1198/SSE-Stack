document.addEventListener("DOMContentLoaded", async () => {
    const artistSelect = document.getElementById("contract-artist");
    const contractType = document.getElementById("contract-type");
    const contractEmails = document.getElementById("contract-emails");
    const contractNotes = document.getElementById("contract-notes");
    const contractBody = document.getElementById("contract-body");
    const form = document.getElementById("contract-form");
    const saveSendButton = document.getElementById("save-send-button");
    const errorBox = document.getElementById("contract-error");
    const successBox = document.getElementById("contract-success");
    const params = new URLSearchParams(window.location.search);

    let artists = [];

    function clearMessages() {
        errorBox.textContent = "";
        successBox.textContent = "";
    }

    function getSelectedArtist() {
        const selectedId = artistSelect.value;
        return artists.find((artist) => String(artist.id) === String(selectedId)) || null;
    }

    async function loadArtists() {
        const data = await apiFetch("/api/contracts/artists");
        artists = data.artists || [];

        artistSelect.innerHTML = artists.map((artist) => {
            return `<option value="${artist.id}">${artist.artist_name}</option>`;
        }).join("");

        const prefArtistId = params.get("artist_profile_id");
        const prefType = params.get("type");

        if (prefArtistId) {
            artistSelect.value = prefArtistId;
        }

        if (prefType && ["publishing", "distribution"].includes(prefType)) {
            contractType.value = prefType;
        }

        const selected = getSelectedArtist();
        if (selected) {
            contractEmails.value = (selected.emails || []).join(", ");
        }
    }

    function buildPublishingTemplate(artistName) {
        return `PUBLISHING, LICENSE & ROYALTY AGREEMENT

This music publishing agreement is made between ${artistName}, hereafter referred to as Licensor, and SpacedOut Studios Entertainment LLC, hereafter referred to as Publisher.

Publisher is engaged in the business of music publishing and exploitation of musical works. Licensor desires to grant Publisher rights to publish, administer, control, license, and collect royalties for the applicable Composition(s) and related sound recording(s), subject to the terms of this Agreement.

MECHANICAL LICENSE & PERFORMANCE ROYALTIES

As of the Effective Date, SpacedOut Studios Entertainment LLC shall have the right, but not the obligation, to administer and permit the exploitation of Licensor’s interest in the Licensed Song(s), Elements, and related Master(s) throughout the world and known universe.

Publisher may register Composition(s) with performance rights organizations, including ASCAP, BMI, SESAC, or equivalent organizations, on behalf of Licensor.

ROYALTY FEES

SpacedOut Studios Entertainment LLC shall pay to Licensor fifty percent (50%) of Net Proceeds generated from exploitation and licensing of the Licensed Song(s), unless otherwise stipulated in a successive written agreement.

Royalty payments shall be computed and paid within sixty (60) days following June 30 and December 31, with respect to receipts actually received during the immediately preceding six (6) month period.

INDEMNIFICATION

Licensor represents and warrants that Licensor owns, controls, or has obtained all necessary permissions for the Composition(s), Master(s), samples, elements, and related materials covered by this Agreement.

Licensor shall indemnify, defend, and hold harmless SpacedOut Studios Entertainment LLC, its successors, assigns, owners, parents, subsidiaries, affiliates, officers, directors, employees, and licensees from claims arising from breach of these representations.

REPRESENTATIONS & WARRANTIES

Licensor warrants that Licensor has full right and authority to enter into this Agreement and grant the rights described herein.

MISCELLANEOUS

This Agreement contains the full agreement between the parties. Any changes must be made in writing and signed by both parties.

This Agreement shall be governed by the laws of the State of New Jersey and the United States of America.

CONTACT / PRO ADMINISTRATION

FULL NAME: __________________________________________

PRO (BMI/ASCAP/SESAC): _______________________________

IPI#: ________________________________________________

ADDRESS: ____________________________________________

TELEPHONE: __________________________________________

EMAIL: _______________________________________________

SIGNATURE PAGE

Licensor [Print Name]: _________________________________

Licensor [Signature / Date]: _____________________________

Aliem L. Jumpp
On behalf of SpacedOut Studios Entertainment LLC

SpacedOut Studios Entertainment LLC [Signature / Date]:

______________________________________________________`;
    }

    function buildDistributionTemplate(artistName) {
        return `SPACEDOUT STUDIOS ENTERTAINMENT LLC
MASTER RECORDING AND DISTRIBUTION AGREEMENT

This Agreement is made between SpacedOut Studios Entertainment LLC, doing business as SpacedOut Studios Entertainment, located at 137 Kelly Driver Rd. Laurel Springs, NJ 08021, hereafter referred to as Company, and ${artistName}, hereafter referred to as Artist.

1. MASTER RECORDING(S)

During the term of this Agreement, Artist will create sound recordings and provide them to Company for the purpose of distribution, release, promotion, and monetization.

Company specializes in digital representation, recording distribution, and artist support. Company is familiar with Artist’s musical abilities and has the expertise, contacts, and resources to assist Artist in furthering their online music career.

Master Recording(s) will be licensed to SpacedOut Studios Entertainment LLC and its subsidiaries.

2. TERM / TERMINATION

This Agreement will commence on the Effective Date and continue for a period of five (5) years. Artist may terminate the Agreement after five (5) years with thirty (30) days written notice.

If Artist fails to notify Company in time, there will be an automatic five (5) year renewal of this Agreement.

3. PRODUCTION OF RECORDINGS

Artist agrees to produce digital master recordings. Master recordings shall be delivered to Company in WAV and/or MP3 format of commercially acceptable quality for digital distribution.

Preferred WAV specifications are 24-bit, 44.1 kHz, stereo WAV.

4. COSTS

Any fees or costs related to promotion and release shall be recoupable from gross track revenue only when mutually agreed upon by Company and Artist.

After costs have been recouped, remaining income will be distributed according to the revenue splits specified in this Agreement.

5. ARTISTIC CONTROL

Company and Artist shall be jointly responsible for decisions regarding artistic content, including cover art, titles, release timing, and presentation.

6. COMPLETION AND RELEASE

The recordings shall be completed and prepared for digital release and distribution. Company will use reasonable efforts to release the recordings on the mutually agreed release date.

7. LICENSE FOR USE OF NAME AND IMAGE

Artist grants Company the right to use Artist’s performing name, image, likeness, biography, and social media links in connection with promotion and distribution of the recordings.

8. TRANSFER / LICENSE OF RIGHTS

Artist grants Company the rights necessary to upload, distribute, monetize, promote, and exploit the Master Recording(s) online for the duration of this Agreement.

9. SAMPLES

Artist represents and warrants that, to the best of Artist’s knowledge, the Master Recording(s) are original or properly cleared and do not infringe on third-party rights.

10. DISTRIBUTION

Company will distribute the Master Recording(s) worldwide through digital platforms, including Spotify, Apple Music, iTunes, and other DSPs.

Artist understands and agrees that the Master Recording(s) will remain available for the term of this Agreement.

11. ROYALTIES & ACCOUNTING

Company will receive royalties or licensing fees from online networks and distributors. Artist shall not be personally liable for costs if royalties are insufficient to recoup agreed costs.

After recoupment of approved costs, royalties shall be distributed as follows:

30% to Company

70% to ${artistName}

Additional Artist / Split: ________________________________

Additional Artist / Split: ________________________________

Additional Artist / Split: ________________________________

Royalties are paid four (4) times per year, once every three (3) months, within forty-five (45) days of the start of every quarter.

First payment may take up to six (6) months depending on distributor payout schedules.

Payment threshold is $100 USD.

12. NON-CIRCUMVENTION

Artist shall not interfere with Company’s distribution efforts or enter into any contract inconsistent with the rights granted to Company for the Master Recording(s).

13. MISCELLANEOUS

This Agreement shall be binding upon the successors and assigns of the parties.

Company and Artist submit to the jurisdiction of the courts of the United States of America for enforcement of this Agreement.

This Agreement shall be governed by the laws of the United States of America and applicable state law.

14. REPRESENTATIONS AND WARRANTIES

Artist represents and warrants that Artist has full right and power to enter into this Agreement and has obtained all necessary rights and clearances.

15. REMIXES AND REMAKES

Company may authorize remixes only with prior written consent of Artist. Any approved remix shall be treated as a Master under this Agreement.

16. INDEMNITY

Artist agrees to indemnify and hold harmless Company from claims, liabilities, damages, expenses, costs, and losses arising from breach of Artist’s obligations, warranties, negligence, or misconduct.

17. ACCEPTANCE

For convenience, the parties may signal acceptance by electronic mail, electronic signature, or other agreed method.

18. ENTIRE AGREEMENT

This Agreement supersedes all prior written or oral agreements between the parties related to the subject matter.

SIGNATURE PAGE

ON BEHALF OF SPACEDOUT STUDIOS ENTERTAINMENT LLC

By: _________________________________________________

Aliem Jumpp
Founder / Owner

Date: _______________________________________________

ON BEHALF OF ARTIST

Artist Name: ${artistName}

By: _________________________________________________

Date: _______________________________________________

Parent / Guardian Signature, if applicable:

______________________________________________________`;
    }


    function fillDefaultTemplate() {
        const selectedArtist = getSelectedArtist();
        const type = contractType.value;
        const artistName = selectedArtist?.artist_name || "[Artist Name]";

        if (type === "publishing") {
            contractBody.value = buildPublishingTemplate(artistName);
        } else {
            contractBody.value = buildDistributionTemplate(artistName);
        }
    }

    artistSelect?.addEventListener("change", () => {
        const selected = getSelectedArtist();
        contractEmails.value = (selected?.emails || []).join(", ");
    });

    contractType?.addEventListener("change", () => {
        fillDefaultTemplate();
    });

    form?.addEventListener("submit", async (event) => {
        event.preventDefault();
        await submitContract(false);
    });

    saveSendButton?.addEventListener("click", async () => {
        await submitContract(true);
    });

    async function submitContract(sendNow) {
        clearMessages();

        const selectedArtist = getSelectedArtist();
        if (!selectedArtist) {
            errorBox.textContent = "Please choose an artist.";
            return;
        }

        const payload = {
            artist_profile_id: selectedArtist.id,
            artist_name: selectedArtist.artist_name,
            contract_type: contractType.value,
            body_text: contractBody.value.trim(),
            notes: contractNotes.value.trim(),
            send_now: sendNow,
            recipient_emails: contractEmails.value
                .split(",")
                .map((value) => value.trim())
                .filter(Boolean),
        };

        try {
            const data = await apiFetch("/api/contracts", {
                method: "POST",
                body: payload,
            });

            successBox.textContent = sendNow
                ? "Contract created and sent."
                : "Contract draft saved.";

            if (data.contract?.id) {
                window.location.href = `/contracts/view?id=${data.contract.id}`;
            }
        } catch (error) {
            errorBox.textContent = error.message || "Failed to save contract.";
        }
    }

    try {
        const currentUser = await getCurrentUser();
        if (!currentUser || !["admin", "developer"].includes(currentUser.role)) {
            window.location.href = "/";
            return;
        }

        await loadArtists();
        fillDefaultTemplate();
    } catch (error) {
        errorBox.textContent = error.message || "Failed to load contract editor.";
    }
});