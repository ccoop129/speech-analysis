// Back to Top Button functionality
document.addEventListener("DOMContentLoaded", function() {
  const backToTopButton = document.getElementById("back-to-top");
  
  if (!backToTopButton) return; // Exit if button doesn't exist on page
  
  window.addEventListener("scroll", () => {
    if (window.pageYOffset > 300) {
      backToTopButton.classList.add("show");
    } else {
      backToTopButton.classList.remove("show");
    }
  });
  
  backToTopButton.addEventListener("click", (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
});
