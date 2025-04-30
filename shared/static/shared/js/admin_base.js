let links = document.querySelectorAll('.section-links li a');


links.forEach(link => {
    link.addEventListener('click', function(e) {
  
      // Remove 'active' from all li elements inside all .section-links
      document.querySelectorAll('.section-links li').forEach(li => li.classList.remove('active'));
  
      // Add 'active' to the parent li of the clicked a tag
      this.parentElement.classList.add('active');
    });
  });
  