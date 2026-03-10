/** @odoo-module **/

/**
 * Module 10 UX enhancement:
 * Enable drag-and-drop upload directly in QHSE Photos/Attachments section.
 *
 * We route dropped files to the existing many2many_binary input so the native
 * Odoo upload flow remains unchanged.
 */

function getDropzone(target) {
    return target && target.closest ? target.closest(".btp_qse_dropzone") : null;
}

function getFileInput(dropzone) {
    if (!dropzone) {
        return null;
    }
    return dropzone.querySelector("input[type='file']");
}

function setInputFiles(input, files) {
    if (!input || !files || !files.length) {
        return false;
    }
    try {
        const dt = new DataTransfer();
        for (const file of files) {
            dt.items.add(file);
        }
        input.files = dt.files;
        input.dispatchEvent(new Event("change", { bubbles: true }));
        return true;
    } catch (_err) {
        return false;
    }
}

document.addEventListener("dragover", (ev) => {
    const dropzone = getDropzone(ev.target);
    if (!dropzone) {
        return;
    }
    ev.preventDefault();
    dropzone.classList.add("btp_qse_dropzone--active");
});

document.addEventListener("dragleave", (ev) => {
    const dropzone = getDropzone(ev.target);
    if (!dropzone) {
        return;
    }
    if (!dropzone.contains(ev.relatedTarget)) {
        dropzone.classList.remove("btp_qse_dropzone--active");
    }
});

document.addEventListener("drop", (ev) => {
    const dropzone = getDropzone(ev.target);
    if (!dropzone) {
        return;
    }
    ev.preventDefault();
    ev.stopPropagation();
    dropzone.classList.remove("btp_qse_dropzone--active");

    const input = getFileInput(dropzone);
    const files = ev.dataTransfer ? ev.dataTransfer.files : null;
    if (!setInputFiles(input, files)) {
        // Fallback: focus upload widget so user can click browse immediately.
        const button = dropzone.querySelector("button, .o_select_file_button");
        if (button) {
            button.click();
        }
    }
});
