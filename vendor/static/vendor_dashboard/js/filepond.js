document.addEventListener("DOMContentLoaded", function() {
    // Get existing images from the hidden script tag
    const form = document.getElementById("update_form"); // Target the form
    const existingImagesElement = document.getElementById("existing-images");
    const existingFiles = existingImagesElement ? JSON.parse(existingImagesElement.textContent) : [];


    // Register the plugins
    FilePond.registerPlugin(
        FilePondPluginImagePreview, 
        FilePondPluginFileValidateType, 
        FilePondPluginFileValidateSize
    );

    FilePond.setOptions({
        server: {
            load: (source, load, error) => {
                fetch(source)
                    .then(response => {
                        if (response.ok) {
                            return response.blob();
                        }
                        throw new Error('Failed to load file');
                    })
                    .then(blob => load(blob))
                    .catch(err => error(err.message));
            }
        }
    });

    // Initialize FilePond
    const pond = FilePond.create(document.querySelector('.filepond'), {
        allowMultiple: true,
        allowReorder: true,
        instantUpload: false,
        storeAsFile: true,  // Ensures files are sent with the form
        acceptedFileTypes: ['image/*'],  // Only allow images
        imagePreviewHeight: 150,  // Adjust preview size
        labelIdle: "Drag & Drop your images or <span class='filepond--label-action'>Browse</span>", // Custom UI text
        files: existingFiles, 
        cache: false,
        // stylePanelLayout: 'integrated',
    });

    form.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent default submission for debugging

        const images = pond.getFiles().map(file => file.source); // Get image sources

        let hiddenInput = form.querySelector("input[name='existing_images']");
        
        if (!hiddenInput) {
            hiddenInput = document.createElement("input");
            hiddenInput.type = "hidden";
            hiddenInput.name = "existing_images";
            hiddenInput.id = "existing_images";
            form.appendChild(hiddenInput);  // ✅ Append inside the form
        }
        
        hiddenInput.value = JSON.stringify(images);
        console.log("Hidden Input Value:", hiddenInput.value); // Debugging output

        form.submit(); // ✅ Now submit the form
    });

    const filepondItems = document.querySelectorAll('.filepond--item');
    const gap = 15; // Define the gap between items (in pixels)

    filepondItems.forEach((item, index) => {
        // Add margin-right to all items except the last in each row
        if ((index + 1) % 3 !== 0) {
            item.style.marginRight = `${gap}px`;
        }

        // Add margin-bottom to all items
        item.style.marginBottom = `${gap}px`;
    });

});