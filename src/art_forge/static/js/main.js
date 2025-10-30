// ArtForge - Main JavaScript

// Disable right-click on all images
document.addEventListener('DOMContentLoaded', function() {
    // Prevent context menu on images
    document.addEventListener('contextmenu', function(e) {
        if (e.target.tagName === 'IMG') {
            e.preventDefault();
            return false;
        }
    });
    
    // Prevent dragging images
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('dragstart', function(e) {
            e.preventDefault();
            return false;
        });
    });
});

